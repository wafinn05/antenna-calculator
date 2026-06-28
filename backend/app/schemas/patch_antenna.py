"""
Microstrip Patch Antenna Calculator — Pydantic Schemas

Request/response models for the API with validation and documentation.
These models serve as the contract between frontend and backend.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Enums
# =============================================================================


class FrequencyUnit(str, Enum):
    """Supported frequency units."""
    Hz = "Hz"
    kHz = "kHz"
    MHz = "MHz"
    GHz = "GHz"


class LengthUnit(str, Enum):
    """Supported length units."""
    mm = "mm"
    cm = "cm"
    m = "m"
    inch = "inch"
    mil = "mil"
    um = "um"


# =============================================================================
# Request Models
# =============================================================================


class AdvancedConfig(BaseModel):
    """Configuration for advanced (Phase 2) calculations."""
    enabled: bool = Field(
        default=False,
        description="Enable advanced calculations (edge resistance, inset feed, etc.)"
    )
    feed_impedance: float = Field(
        default=50.0,
        gt=0,
        description="Target feed impedance in Ohms (default: 50Ω)"
    )
    use_inset_feed: bool = Field(
        default=False,
        description="Calculate inset feed depth for impedance matching"
    )


class PatchAntennaRequest(BaseModel):
    """Request body for patch antenna calculation.

    All inputs are validated before processing:
    - frequency must be > 0
    - dielectric_constant must be > 1 (physical constraint)
    - substrate_height must be > 0
    """
    frequency: float = Field(
        ...,
        gt=0,
        description="Resonant frequency value (must be > 0)",
        examples=[2.4]
    )
    frequency_unit: FrequencyUnit = Field(
        default=FrequencyUnit.GHz,
        description="Unit for the frequency value"
    )
    dielectric_constant: float = Field(
        ...,
        gt=1.0,
        description=(
            "Relative dielectric constant (εr) of the substrate. "
            "Must be > 1 for any physical dielectric material. "
            "Common values: FR4=4.4, RT/duroid 5880=2.2, Rogers RO4003C=3.38"
        ),
        examples=[4.4]
    )
    substrate_height: float = Field(
        ...,
        gt=0,
        description="Substrate height/thickness value (must be > 0)",
        examples=[1.6]
    )
    substrate_height_unit: LengthUnit = Field(
        default=LengthUnit.mm,
        description="Unit for the substrate height value"
    )
    advanced: AdvancedConfig = Field(
        default_factory=AdvancedConfig,
        description="Advanced calculation options (optional)"
    )


# =============================================================================
# Response Models
# =============================================================================


class InputEcho(BaseModel):
    """Echo of the converted input values (SI units) for transparency."""
    frequency_hz: float = Field(description="Frequency converted to Hz")
    dielectric_constant: float = Field(description="εr as provided")
    substrate_height_m: float = Field(description="Substrate height converted to meters")


class RecommendedGroundPlane(BaseModel):
    """Recommended ground plane dimensions (rule of thumb: patch + 6h per side)."""
    length_mm: float = Field(description="Ground plane length Lg = L + 6h (mm)")
    width_mm: float = Field(description="Ground plane width Wg = W + 6h (mm)")


class MainResult(BaseModel):
    """Primary calculation results — dimensions and derived values."""
    width_mm: float = Field(description="Patch width W (mm)")
    length_mm: float = Field(description="Patch physical length L (mm)")
    effective_dielectric_constant: float = Field(
        description="Effective dielectric constant ε_eff (dimensionless)"
    )
    length_extension_mm: float = Field(
        description="Fringing length extension ΔL (mm)"
    )
    effective_length_mm: float = Field(
        description="Effective length L_eff (mm)"
    )
    free_space_wavelength_mm: float = Field(
        description="Free-space wavelength λ0 (mm)"
    )
    guided_wavelength_mm: float = Field(
        description="Guided wavelength λg (mm)"
    )
    recommended_ground_plane: RecommendedGroundPlane = Field(
        description="Recommended ground plane dimensions"
    )


class AdvancedResult(BaseModel):
    """Advanced/estimated calculation results — clearly labeled approximate."""
    conductance_g1: float = Field(
        description="Radiation conductance G1 of a single slot (S) — approximate"
    )
    edge_resistance_ohm: float = Field(
        description="Input edge resistance Rin (Ω) — approximate, neglects G12"
    )
    inset_feed_depth_mm: Optional[float] = Field(
        default=None,
        description="Inset feed depth y0 (mm) — approximate, only if inset feed enabled"
    )
    feed_line_width_mm: float = Field(
        description="Microstrip feed line width for target impedance (mm)"
    )
    bandwidth_percent: float = Field(
        description="Estimated bandwidth (%) — rough industry estimate"
    )
    directivity_dbi: float = Field(
        description="Estimated directivity (dBi) — cavity model approximation"
    )
    w_over_lambda0: float = Field(
        description="W/λ0 ratio used in directivity/conductance calculations"
    )


class ModelInfo(BaseModel):
    """Information about the calculation model used."""
    model: str = Field(
        default="Transmission Line Model (Balanis, 4th Ed.)",
        description="Name of the analytical model"
    )
    valid_mode: str = Field(
        default="TM010 dominant mode",
        description="Antenna mode assumed by this model"
    )
    assumptions: str = Field(
        default="W/h > 1, thin substrate h/λ0 ≤ 0.05",
        description="Key assumptions of the model"
    )


class PatchAntennaResponse(BaseModel):
    """Complete response for a successful patch antenna calculation."""
    input_echo: InputEcho = Field(
        description="Echo of converted input values for verification"
    )
    result: MainResult = Field(
        description="Primary calculation results"
    )
    advanced_result: Optional[AdvancedResult] = Field(
        default=None,
        description="Advanced results (only if advanced mode enabled)"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of model validity warnings (empty if no issues)"
    )
    model_info: ModelInfo = Field(
        default_factory=ModelInfo,
        description="Information about the calculation model"
    )


class ErrorResponse(BaseModel):
    """Error response for validation failures."""
    error: str = Field(description="Error code (e.g., INVALID_INPUT)")
    detail: str = Field(description="Human-readable error description")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok")
    service: str = Field(default="microstrip-patch-antenna-calculator")
    version: str = Field(default="1.0.0")
