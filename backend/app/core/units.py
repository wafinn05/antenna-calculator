"""
Microstrip Patch Antenna Calculator — Unit Conversion

Explicit unit conversion functions for frequency and length.
Internal calculation base units: Hz (frequency), meters (length).
"""


# =============================================================================
# Frequency → Hz
# =============================================================================

_FREQ_TO_HZ: dict[str, float] = {
    "Hz": 1.0,
    "kHz": 1.0e3,
    "MHz": 1.0e6,
    "GHz": 1.0e9,
}


def frequency_to_hz(value: float, unit: str) -> float:
    """Convert a frequency value from the given unit to Hz.

    Args:
        value: Numeric frequency value (must be > 0).
        unit: One of 'Hz', 'kHz', 'MHz', 'GHz'.

    Returns:
        Frequency in Hz.

    Raises:
        ValueError: If unit is not supported.
    """
    if unit not in _FREQ_TO_HZ:
        raise ValueError(
            f"Unsupported frequency unit '{unit}'. "
            f"Supported: {list(_FREQ_TO_HZ.keys())}"
        )
    return value * _FREQ_TO_HZ[unit]


def hz_to_frequency(value_hz: float, unit: str) -> float:
    """Convert Hz to the target frequency unit."""
    if unit not in _FREQ_TO_HZ:
        raise ValueError(f"Unsupported frequency unit '{unit}'.")
    return value_hz / _FREQ_TO_HZ[unit]


# =============================================================================
# Length → meters
# =============================================================================

_LENGTH_TO_M: dict[str, float] = {
    "m": 1.0,
    "cm": 1.0e-2,
    "mm": 1.0e-3,
    "um": 1.0e-6,
    "inch": 0.0254,
    "mil": 0.0000254,  # 1 mil = 1/1000 inch
}


def length_to_meters(value: float, unit: str) -> float:
    """Convert a length value from the given unit to meters.

    Args:
        value: Numeric length value (must be > 0 for physical dimensions).
        unit: One of 'mm', 'cm', 'm', 'inch', 'mil', 'um'.

    Returns:
        Length in meters.

    Raises:
        ValueError: If unit is not supported.
    """
    if unit not in _LENGTH_TO_M:
        raise ValueError(
            f"Unsupported length unit '{unit}'. "
            f"Supported: {list(_LENGTH_TO_M.keys())}"
        )
    return value * _LENGTH_TO_M[unit]


def meters_to_length(value_m: float, unit: str) -> float:
    """Convert meters to the target length unit."""
    if unit not in _LENGTH_TO_M:
        raise ValueError(f"Unsupported length unit '{unit}'.")
    return value_m / _LENGTH_TO_M[unit]


def meters_to_mm(value_m: float) -> float:
    """Convenience: meters → millimeters."""
    return value_m * 1000.0
