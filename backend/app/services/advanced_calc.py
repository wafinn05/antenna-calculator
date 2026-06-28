"""
Microstrip Patch Antenna Calculator — Advanced Calculations (Phase 2)

Approximate/estimated formulas for advanced antenna parameters.
All results from this module MUST be labeled as "Approximate" in the UI.

These are NOT simulation-grade results — they are first-order estimates
useful for initial design exploration only.

References:
    - Section 2.8 of the project specification
    - Balanis, "Antenna Theory", 4th Ed., Ch.14 (cavity model approximations)
    - Hammerstad & Jensen, IEEE MTT-S 1980 (microstrip line synthesis)
"""

import math

from app.core.constants import SPEED_OF_LIGHT


# =============================================================================
# a) Input Edge Resistance (Cavity Model Approximation)
# =============================================================================


def calculate_g1(width_m: float, lambda0_m: float) -> float:
    """Calculate radiation conductance G1 of a single slot.

    Formula (Section 2.8a):
        G1 = (1/90) * (W/λ0)^2          if W/λ0 < 1/10
        G1 = (1/120) * (W/λ0)           if W/λ0 ≥ 1/10

    Note: This is an approximation. Precise calculation requires
    numerical integration of Bessel functions (beyond scope of
    this calculator).

    Args:
        width_m: Patch width in meters.
        lambda0_m: Free-space wavelength in meters.

    Returns:
        Conductance G1 in Siemens.
    """
    w_over_lambda0 = width_m / lambda0_m

    if w_over_lambda0 < 0.1:
        return (1.0 / 90.0) * w_over_lambda0**2
    else:
        return (1.0 / 120.0) * w_over_lambda0


def calculate_edge_resistance(g1: float) -> float:
    """Calculate input edge resistance Rin.

    Formula (Section 2.8a):
        Rin ≈ 1 / (2 * G1)

    This neglects mutual conductance G12 between the two radiating
    slots — it is a first-order approximation only.

    Args:
        g1: Radiation conductance of a single slot (Siemens).

    Returns:
        Input edge resistance in Ohms.
    """
    if g1 <= 0:
        return float("inf")
    return 1.0 / (2.0 * g1)


# =============================================================================
# b) Inset Feed Depth
# =============================================================================


def calculate_inset_feed_depth(
    length_m: float, z0: float, rin: float
) -> float:
    """Calculate inset feed depth (y0) for impedance matching.

    Formula (Section 2.8b):
        y0 = (L / π) * arccos(sqrt(Z0 / Rin))

    Args:
        length_m: Physical patch length in meters.
        z0: Target impedance in Ohms (typically 50).
        rin: Edge input resistance in Ohms.

    Returns:
        Inset feed depth in meters.

    Raises:
        ValueError: If Z0 > Rin (cannot match to lower impedance
                    than edge resistance with inset feed).
    """
    if z0 > rin:
        raise ValueError(
            f"Target impedance Z0 = {z0}Ω exceeds edge resistance "
            f"Rin ≈ {rin:.1f}Ω. Inset feed cannot match to an impedance "
            f"higher than the edge resistance."
        )

    return (length_m / math.pi) * math.acos(math.sqrt(z0 / rin))


# =============================================================================
# c) Microstrip Feed Line Width (Hammerstad-Jensen Synthesis)
# =============================================================================


def calculate_feed_line_width(
    z0: float, eps_r: float, height_m: float
) -> float:
    """Calculate microstrip feed line width for a target impedance.

    Hammerstad-Jensen synthesis formula (Section 2.8c):

    For W/h > 2:
        A = Z0/60 * sqrt((εr+1)/2) + ((εr-1)/(εr+1)) * (0.23 + 0.11/εr)
        W/h = 8*exp(A) / (exp(2A) - 2)

    For W/h ≤ 2:
        B = 377π / (2*Z0*sqrt(εr))
        W/h = (2/π) * [B - 1 - ln(2B-1) + ((εr-1)/(2εr)) * (ln(B-1) + 0.39 - 0.61/εr)]

    Strategy: compute both, use the one whose result is consistent
    with its own domain assumption.

    Args:
        z0: Target characteristic impedance in Ohms.
        eps_r: Relative dielectric constant.
        height_m: Substrate height in meters.

    Returns:
        Feed line width in meters.
    """
    # Try the W/h > 2 formula first
    a = (z0 / 60.0) * math.sqrt((eps_r + 1.0) / 2.0) + (
        (eps_r - 1.0) / (eps_r + 1.0)
    ) * (0.23 + 0.11 / eps_r)

    w_over_h_formula1 = 8.0 * math.exp(a) / (math.exp(2.0 * a) - 2.0)

    if w_over_h_formula1 < 2.0:
        # Result is consistent with the W/h < 2 domain, use formula 1
        return w_over_h_formula1 * height_m

    # Use W/h ≤ 2 formula (which applies when w_over_h > 2)
    b = 377.0 * math.pi / (2.0 * z0 * math.sqrt(eps_r))

    w_over_h_formula2 = (2.0 / math.pi) * (
        b
        - 1.0
        - math.log(2.0 * b - 1.0)
        + ((eps_r - 1.0) / (2.0 * eps_r))
        * (math.log(b - 1.0) + 0.39 - 0.61 / eps_r)
    )

    return w_over_h_formula2 * height_m


# =============================================================================
# d) Bandwidth Estimation
# =============================================================================


def calculate_bandwidth_percent(
    eps_r: float,
    width_m: float,
    length_m: float,
    height_m: float,
    lambda0_m: float,
) -> float:
    """Estimate bandwidth as a percentage (rough industry rule of thumb).

    Formula (Section 2.8d):
        BW(%) ≈ 3.77 * ((εr - 1)/εr²) * (W/L) * (h/λ0) * 100

    This is a rough estimate only. Actual bandwidth depends heavily
    on feed matching and fabrication tolerances.

    Args:
        eps_r: Relative dielectric constant.
        width_m: Patch width in meters.
        length_m: Patch length in meters.
        height_m: Substrate height in meters.
        lambda0_m: Free-space wavelength in meters.

    Returns:
        Estimated bandwidth in percent.
    """
    return (
        3.77
        * ((eps_r - 1.0) / (eps_r**2))
        * (width_m / length_m)
        * (height_m / lambda0_m)
        * 100.0
    )


# =============================================================================
# e) Directivity Estimation
# =============================================================================


def calculate_directivity_dbi(width_m: float, lambda0_m: float) -> float:
    """Estimate directivity in dBi (cavity model approximation).

    Formula (Section 2.8e):
        D0 ≈ 10 * log10(6.6 * (W/λ0))     for W/λ0 ≤ 0.35

    For W/λ0 > 0.35, this formula becomes less accurate.
    Always labeled as approximate.

    Args:
        width_m: Patch width in meters.
        lambda0_m: Free-space wavelength in meters.

    Returns:
        Estimated directivity in dBi.
    """
    w_over_lambda0 = width_m / lambda0_m
    return 10.0 * math.log10(6.6 * w_over_lambda0)
