"""
Microstrip Patch Antenna Calculator — API Router (v1)

Endpoints for patch antenna dimension calculations.
"""

from fastapi import APIRouter, HTTPException

from app.core.units import frequency_to_hz, length_to_meters, meters_to_mm
from app.schemas.patch_antenna import (
    PatchAntennaRequest,
    PatchAntennaResponse,
    ErrorResponse,
    HealthResponse,
    InputEcho,
    MainResult,
    RecommendedGroundPlane,
    AdvancedResult,
    ModelInfo,
)
from app.services.microstrip_calc import calculate_patch_dimensions
from app.services.advanced_calc import (
    calculate_g1,
    calculate_edge_resistance,
    calculate_inset_feed_depth,
    calculate_feed_line_width,
    calculate_bandwidth_percent,
    calculate_directivity_dbi,
)

router = APIRouter(prefix="/api/v1/patch-antenna", tags=["Patch Antenna"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Simple health check endpoint for monitoring.",
)
async def health_check():
    """Return service health status."""
    return HealthResponse()


@router.post(
    "/calculate",
    response_model=PatchAntennaResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Calculate Patch Antenna Dimensions",
    description=(
        "Calculate the physical dimensions (Width & Length) of a rectangular "
        "microstrip patch antenna using the Transmission Line Model (Balanis). "
        "Optionally compute advanced parameters (edge resistance, inset feed, "
        "bandwidth, directivity) when advanced mode is enabled."
    ),
)
async def calculate_patch_antenna(request: PatchAntennaRequest):
    """Main calculation endpoint.

    1. Converts input units to SI (Hz, meters)
    2. Runs core calculations (pure functions)
    3. Optionally runs advanced calculations
    4. Returns all results with warnings and model info
    """
    # --- Convert inputs to SI ---
    try:
        freq_hz = frequency_to_hz(request.frequency, request.frequency_unit.value)
        height_m = length_to_meters(
            request.substrate_height, request.substrate_height_unit.value
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    eps_r = request.dielectric_constant

    # --- Core calculations ---
    try:
        result = calculate_patch_dimensions(freq_hz, eps_r, height_m)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    # --- Build response ---
    input_echo = InputEcho(
        frequency_hz=freq_hz,
        dielectric_constant=eps_r,
        substrate_height_m=height_m,
    )

    main_result = MainResult(
        width_mm=round(meters_to_mm(result.width_m), 4),
        length_mm=round(meters_to_mm(result.length_m), 4),
        effective_dielectric_constant=round(result.effective_dielectric_constant, 4),
        length_extension_mm=round(meters_to_mm(result.length_extension_m), 4),
        effective_length_mm=round(meters_to_mm(result.effective_length_m), 4),
        free_space_wavelength_mm=round(meters_to_mm(result.free_space_wavelength_m), 4),
        guided_wavelength_mm=round(meters_to_mm(result.guided_wavelength_m), 4),
        recommended_ground_plane=RecommendedGroundPlane(
            length_mm=round(meters_to_mm(result.ground_plane_length_m), 4),
            width_mm=round(meters_to_mm(result.ground_plane_width_m), 4),
        ),
    )

    # --- Advanced calculations (if enabled) ---
    advanced_result = None
    if request.advanced.enabled:
        try:
            lambda0_m = result.free_space_wavelength_m
            w_over_lambda0 = result.width_m / lambda0_m

            # G1 and Rin
            g1 = calculate_g1(result.width_m, lambda0_m)
            rin = calculate_edge_resistance(g1)

            # Inset feed depth
            inset_depth_mm = None
            if request.advanced.use_inset_feed:
                try:
                    y0 = calculate_inset_feed_depth(
                        result.length_m,
                        request.advanced.feed_impedance,
                        rin,
                    )
                    inset_depth_mm = round(meters_to_mm(y0), 4)
                except ValueError as e:
                    result.warnings.append(f"Inset feed calculation: {str(e)}")

            # Feed line width
            feed_width = calculate_feed_line_width(
                request.advanced.feed_impedance, eps_r, height_m
            )

            # Bandwidth
            bw_percent = calculate_bandwidth_percent(
                eps_r, result.width_m, result.length_m, height_m, lambda0_m
            )

            # Directivity
            directivity = calculate_directivity_dbi(result.width_m, lambda0_m)

            # Directivity warning
            if w_over_lambda0 > 0.35:
                result.warnings.append(
                    f"W/λ0 = {w_over_lambda0:.3f} > 0.35. "
                    f"Directivity estimate accuracy decreases for W/λ0 > 0.35."
                )

            advanced_result = AdvancedResult(
                conductance_g1=round(g1, 6),
                edge_resistance_ohm=round(rin, 2),
                inset_feed_depth_mm=inset_depth_mm,
                feed_line_width_mm=round(meters_to_mm(feed_width), 4),
                bandwidth_percent=round(bw_percent, 3),
                directivity_dbi=round(directivity, 3),
                w_over_lambda0=round(w_over_lambda0, 4),
            )
        except Exception as e:
            result.warnings.append(
                f"Advanced calculation error: {str(e)}. "
                f"Core results are still valid."
            )

    return PatchAntennaResponse(
        input_echo=input_echo,
        result=main_result,
        advanced_result=advanced_result,
        warnings=result.warnings,
        model_info=ModelInfo(),
    )
