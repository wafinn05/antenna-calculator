"""
Microstrip Patch Antenna Calculator — Core Constants

Physical constants, material presets, and model validity ranges
used throughout the calculation engine.
"""

import math

# =============================================================================
# Physical Constants
# =============================================================================

# Speed of light in vacuum (m/s) — precise value per NIST
SPEED_OF_LIGHT: float = 299_792_458.0

# Speed of light approximate (m/s) — for matching simpler reference calculators
SPEED_OF_LIGHT_APPROX: float = 3.0e8

# =============================================================================
# Model Validity Ranges (Transmission Line Model — Balanis)
# =============================================================================

# Dielectric constant valid range for Transmission Line Model
EPSILON_R_MIN: float = 2.0
EPSILON_R_MAX: float = 10.0

# Soft warning threshold for εr (still works but less common in literature)
EPSILON_R_SOFT_MAX: float = 12.0

# Maximum h/λ0 ratio for thin substrate assumption
H_LAMBDA0_MAX: float = 0.05

# Minimum physical εr (must be > 1 for any real dielectric substrate)
EPSILON_R_PHYSICAL_MIN: float = 1.0

# =============================================================================
# Preset Material Library
# =============================================================================

MATERIAL_PRESETS: dict[str, dict] = {
    "FR4": {
        "epsilon_r": 4.4,
        "description": "FR4 (standard PCB)",
        "typical_heights_mm": [0.8, 1.0, 1.6],
    },
    "RT_DUROID_5880": {
        "epsilon_r": 2.2,
        "description": "Rogers RT/duroid 5880",
        "typical_heights_mm": [0.508, 0.787, 1.575],
    },
    "RT_DUROID_6010": {
        "epsilon_r": 10.2,
        "description": "Rogers RT/duroid 6010",
        "typical_heights_mm": [0.254, 0.635, 1.27],
    },
    "RO4003C": {
        "epsilon_r": 3.38,
        "description": "Rogers RO4003C",
        "typical_heights_mm": [0.203, 0.508, 0.813],
    },
    "ALUMINA": {
        "epsilon_r": 9.8,
        "description": "Alumina (Al₂O₃)",
        "typical_heights_mm": [0.254, 0.635, 1.27],
    },
    "AIR_FOAM": {
        "epsilon_r": 1.06,
        "description": "Air / Foam (≈1.06)",
        "typical_heights_mm": [1.0, 2.0, 3.0],
    },
}

# =============================================================================
# Supported Unit Enums (string values for API)
# =============================================================================

FREQUENCY_UNITS = ("Hz", "kHz", "MHz", "GHz")
LENGTH_UNITS = ("mm", "cm", "m", "inch", "mil", "um")

# =============================================================================
# Ground Plane Margin Multiplier
# =============================================================================

# Standard rule of thumb: ground plane = patch + 6h on each side (Balanis)
GROUND_PLANE_MARGIN_FACTOR: int = 6
