"""
Microstrip Patch Antenna Calculator — Core Calculation Engine

Pure functions implementing the Transmission Line Model (Balanis, 4th Ed., Ch.14)
for rectangular microstrip patch antenna dimension calculations.

All functions are pure (input → output, no side effects).
Internal units: SI (meters, Hz).

Formulas Reference:
    - Section 2.1–2.7 of the project specification
    - C. A. Balanis, "Antenna Theory: Analysis and Design", 4th Edition, Ch.14
    - E. O. Hammerstad, "Equations for Microstrip Circuit Design", 1975
"""

import math
from dataclasses import dataclass, field

from app.core.constants import (
    SPEED_OF_LIGHT,
    EPSILON_R_MIN,
    EPSILON_R_MAX,
    EPSILON_R_PHYSICAL_MIN,
    EPSILON_R_SOFT_MAX,
    H_LAMBDA0_MAX,
    GROUND_PLANE_MARGIN_FACTOR,
)


# =============================================================================
# Data classes for structured results
# =============================================================================


@dataclass
class PatchResult:
    """Complete result of patch antenna dimension calculations."""

    # Primary outputs
    width_m: float
    length_m: float

    # Intermediate values
    effective_dielectric_constant: float
    length_extension_m: float
    effective_length_m: float

    # Derived wavelengths
    free_space_wavelength_m: float
    guided_wavelength_m: float

    # Ground plane recommendations
    ground_plane_length_m: float
    ground_plane_width_m: float

    # Validation info
    w_over_h: float
    h_over_lambda0: float

    # Warnings
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# Input Validation
# =============================================================================


def validate_inputs(freq_hz: float, eps_r: float, height_m: float) -> list[str]:
    """Validate physical inputs and return list of error messages.

    Raises ValueError for hard-invalid inputs (non-physical).
    Returns warning strings for soft-invalid inputs (model accuracy concerns).

    Args:
        freq_hz: Resonant frequency in Hz (must be > 0).
        eps_r: Relative dielectric constant (must be > 1).
        height_m: Substrate height in meters (must be > 0).

    Returns:
        List of warning strings (may be empty).

    Raises:
        ValueError: If any input is physically impossible.
    """
    # Hard validation — these are physical impossibilities
    if freq_hz <= 0:
        raise ValueError(
            "Frequency must be greater than 0. "
            "A zero or negative resonant frequency is not physical."
        )

    if eps_r <= EPSILON_R_PHYSICAL_MIN:
        raise ValueError(
            f"Dielectric constant (εr) must be greater than {EPSILON_R_PHYSICAL_MIN}. "
            f"εr ≤ 1 is not physical for a dielectric substrate. "
            f"Received: εr = {eps_r}"
        )

    if height_m <= 0:
        raise ValueError(
            "Substrate height must be greater than 0. "
            "A zero or negative height is not physical."
        )

    # Soft validation — model accuracy warnings
    warnings: list[str] = []

    if eps_r < EPSILON_R_MIN or eps_r > EPSILON_R_MAX:
        warnings.append(
            f"εr = {eps_r} is outside the recommended range for the "
            f"Transmission Line Model ({EPSILON_R_MIN}–{EPSILON_R_MAX}). "
            f"Results may have reduced accuracy. "
            f"Consider validating with EM simulation (CST/HFSS/AWR)."
        )

    if eps_r > EPSILON_R_SOFT_MAX:
        warnings.append(
            f"εr = {eps_r} is well outside the common range in literature. "
            f"Model accuracy may be significantly degraded."
        )

    return warnings


# =============================================================================
# Core Calculation Functions (Section 2.1 – 2.7)
# =============================================================================


def calculate_width(freq_hz: float, eps_r: float, c: float = SPEED_OF_LIGHT) -> float:
    """Calculate patch antenna width (W) for optimal radiation efficiency.

    Formula (Section 2.1 — Balanis):
        W = c / (2 * f_r) * sqrt(2 / (εr + 1))

    This width corresponds to the dominant mode (TM010) and provides
    optimal radiation efficiency by averaging between εr and free space.

    Args:
        freq_hz: Resonant frequency in Hz.
        eps_r: Relative dielectric constant of substrate.
        c: Speed of light in m/s (default: precise value 299792458).

    Returns:
        Patch width in meters.
    """
    return (c / (2.0 * freq_hz)) * math.sqrt(2.0 / (eps_r + 1.0))


def calculate_eps_eff(
    width_m: float, height_m: float, eps_r: float
) -> tuple[float, list[str]]:
    """Calculate effective dielectric constant (ε_eff) using Hammerstad formula.

    Formula (Section 2.2 — Hammerstad, valid for W/h > 1):
        ε_eff = (εr + 1)/2 + (εr - 1)/2 * [1 + 12*(h/W)]^(-1/2)

    Args:
        width_m: Patch width in meters.
        height_m: Substrate height in meters.
        eps_r: Relative dielectric constant.

    Returns:
        Tuple of (ε_eff value, list of warning strings).
        Warning is generated if W/h < 1 (model less accurate).
    """
    warnings: list[str] = []
    w_over_h = width_m / height_m

    if w_over_h < 1.0:
        warnings.append(
            f"W/h = {w_over_h:.2f} < 1. The Hammerstad formula for ε_eff "
            f"used here is optimized for W/h > 1. Results may be less accurate. "
            f"Please re-check input parameters."
        )

    eps_eff = (eps_r + 1.0) / 2.0 + (eps_r - 1.0) / 2.0 * (
        1.0 + 12.0 * (height_m / width_m)
    ) ** (-0.5)

    return eps_eff, warnings


def calculate_delta_l(
    width_m: float, height_m: float, eps_eff: float
) -> float:
    """Calculate fringing length extension (ΔL).

    Formula (Section 2.3 — Hammerstad):
        ΔL / h = 0.412 * [(ε_eff + 0.3) * (W/h + 0.264)] /
                          [(ε_eff - 0.258) * (W/h + 0.8)]
        ΔL = h * (ΔL/h)

    Args:
        width_m: Patch width in meters.
        height_m: Substrate height in meters.
        eps_eff: Effective dielectric constant.

    Returns:
        Length extension ΔL in meters.
    """
    w_over_h = width_m / height_m

    delta_l_over_h = 0.412 * (
        (eps_eff + 0.3) * (w_over_h + 0.264)
    ) / (
        (eps_eff - 0.258) * (w_over_h + 0.8)
    )

    return height_m * delta_l_over_h


def calculate_effective_length(
    freq_hz: float, eps_eff: float, c: float = SPEED_OF_LIGHT
) -> float:
    """Calculate effective length (L_eff) of the patch.

    Formula (Section 2.4 — Balanis):
        L_eff = c / (2 * f_r * sqrt(ε_eff))

    Args:
        freq_hz: Resonant frequency in Hz.
        eps_eff: Effective dielectric constant.
        c: Speed of light in m/s.

    Returns:
        Effective length in meters.
    """
    return c / (2.0 * freq_hz * math.sqrt(eps_eff))


def calculate_physical_length(effective_length_m: float, delta_l_m: float) -> float:
    """Calculate physical length (L) of the patch.

    Formula (Section 2.5 — Balanis):
        L = L_eff - 2 * ΔL

    This is the FINAL physical dimension to fabricate.

    Args:
        effective_length_m: Effective length in meters.
        delta_l_m: Length extension (ΔL) in meters.

    Returns:
        Physical patch length in meters.
    """
    return effective_length_m - 2.0 * delta_l_m


def calculate_free_space_wavelength(
    freq_hz: float, c: float = SPEED_OF_LIGHT
) -> float:
    """Calculate free-space wavelength (λ0).

    Formula (Section 2.7):
        λ0 = c / f_r

    Args:
        freq_hz: Frequency in Hz.
        c: Speed of light in m/s.

    Returns:
        Free-space wavelength in meters.
    """
    return c / freq_hz


def calculate_guided_wavelength(lambda0_m: float, eps_eff: float) -> float:
    """Calculate guided wavelength (λg).

    Formula (Section 2.7):
        λg = λ0 / sqrt(ε_eff)

    Args:
        lambda0_m: Free-space wavelength in meters.
        eps_eff: Effective dielectric constant.

    Returns:
        Guided wavelength in meters.
    """
    return lambda0_m / math.sqrt(eps_eff)


def calculate_ground_plane(
    length_m: float,
    width_m: float,
    height_m: float,
    margin_factor: int = GROUND_PLANE_MARGIN_FACTOR,
) -> tuple[float, float]:
    """Calculate recommended ground plane dimensions.

    Formula (Section 2.7 — rule of thumb, Balanis):
        Lg = L + 6*h
        Wg = W + 6*h

    Args:
        length_m: Patch physical length in meters.
        width_m: Patch width in meters.
        height_m: Substrate height in meters.
        margin_factor: Multiplier for height margin (default 6).

    Returns:
        Tuple of (Lg, Wg) in meters.
    """
    lg = length_m + margin_factor * height_m
    wg = width_m + margin_factor * height_m
    return lg, wg


# =============================================================================
# Orchestrator Function
# =============================================================================


def calculate_patch_dimensions(
    freq_hz: float,
    eps_r: float,
    height_m: float,
    c: float = SPEED_OF_LIGHT,
) -> PatchResult:
    """Orchestrator: compute all patch antenna dimensions and derived values.

    Calls all individual calculation functions in sequence, collects
    intermediate results, performs validity checks, and returns a
    complete PatchResult with warnings.

    Args:
        freq_hz: Resonant frequency in Hz.
        eps_r: Relative dielectric constant of substrate.
        height_m: Substrate height in meters.
        c: Speed of light in m/s (default: precise value).

    Returns:
        PatchResult with all calculated dimensions and warnings.

    Raises:
        ValueError: If inputs are physically impossible.
    """
    # Step 0: Validate inputs (raises ValueError for hard failures)
    warnings = validate_inputs(freq_hz, eps_r, height_m)

    # Step 1: Width (Section 2.1)
    width = calculate_width(freq_hz, eps_r, c)

    # Step 2: Effective dielectric constant (Section 2.2)
    eps_eff, eps_eff_warnings = calculate_eps_eff(width, height_m, eps_r)
    warnings.extend(eps_eff_warnings)

    # Step 3: Length extension (Section 2.3)
    delta_l = calculate_delta_l(width, height_m, eps_eff)

    # Step 4: Effective length (Section 2.4)
    l_eff = calculate_effective_length(freq_hz, eps_eff, c)

    # Step 5: Physical length (Section 2.5)
    length = calculate_physical_length(l_eff, delta_l)

    # Step 6: Derived wavelengths (Section 2.7)
    lambda0 = calculate_free_space_wavelength(freq_hz, c)
    lambda_g = calculate_guided_wavelength(lambda0, eps_eff)

    # Step 7: Ground plane (Section 2.7)
    lg, wg = calculate_ground_plane(length, width, height_m)

    # Step 8: Validity checks (Section 2.6)
    w_over_h = width / height_m
    h_over_lambda0 = height_m / lambda0

    if h_over_lambda0 > H_LAMBDA0_MAX:
        warnings.append(
            f"h/λ0 = {h_over_lambda0:.4f} exceeds the thin substrate limit "
            f"(≤ {H_LAMBDA0_MAX}). The Transmission Line Model assumes a "
            f"thin substrate; results may be inaccurate. "
            f"Consider validating with full-wave EM simulation."
        )

    return PatchResult(
        width_m=width,
        length_m=length,
        effective_dielectric_constant=eps_eff,
        length_extension_m=delta_l,
        effective_length_m=l_eff,
        free_space_wavelength_m=lambda0,
        guided_wavelength_m=lambda_g,
        ground_plane_length_m=lg,
        ground_plane_width_m=wg,
        w_over_h=w_over_h,
        h_over_lambda0=h_over_lambda0,
        warnings=warnings,
    )
