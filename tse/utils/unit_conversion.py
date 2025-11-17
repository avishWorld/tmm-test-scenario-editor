"""
Unit conversion utilities.

Requirements:
- TSE-FUNC-083: Speed conversion (knots ↔ m/s)
"""

# Conversion constants
KNOTS_TO_MPS = 0.51444  # 1 knot = 0.51444 m/s
MPS_TO_KNOTS = 1.0 / KNOTS_TO_MPS

METERS_TO_NAUTICAL_MILES = 1.0 / 1852.0
NAUTICAL_MILES_TO_METERS = 1852.0


def knots_to_mps(speed_knots: float) -> float:
    """
    Convert speed from knots to meters per second.

    Args:
        speed_knots: Speed in knots

    Returns:
        Speed in meters per second

    Requirements: TSE-FUNC-083
    """
    return speed_knots * KNOTS_TO_MPS


def mps_to_knots(speed_mps: float) -> float:
    """
    Convert speed from meters per second to knots.

    Args:
        speed_mps: Speed in meters per second

    Returns:
        Speed in knots
    """
    return speed_mps * MPS_TO_KNOTS


def meters_to_nautical_miles(distance_m: float) -> float:
    """
    Convert distance from meters to nautical miles.

    Args:
        distance_m: Distance in meters

    Returns:
        Distance in nautical miles
    """
    return distance_m * METERS_TO_NAUTICAL_MILES


def nautical_miles_to_meters(distance_nm: float) -> float:
    """
    Convert distance from nautical miles to meters.

    Args:
        distance_nm: Distance in nautical miles

    Returns:
        Distance in meters
    """
    return distance_nm * NAUTICAL_MILES_TO_METERS
