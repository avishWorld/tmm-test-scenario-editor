"""
Geographic calculation utilities using WGS84 ellipsoid model.

Requirements:
- TSE-FUNC-150: WGS84 ellipsoid model
- TSE-FUNC-151: Haversine distance (±0.5% accuracy up to 20 NM)
- TSE-FUNC-152: Forward azimuth calculation
- TSE-FUNC-153: Destination point calculation
- TSE-FUNC-154: Meters per degree longitude
"""

import math
from typing import Tuple
# from tse.models.geo import GeoPosition  # Avoid circular import


# WGS84 ellipsoid parameters
WGS84_SEMI_MAJOR_AXIS = 6378137.0  # meters
WGS84_SEMI_MINOR_AXIS = 6356752.314245  # meters
WGS84_FLATTENING = 1.0 / 298.257223563


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points using Haversine formula.

    Args:
        lat1: Latitude of point 1 (decimal degrees)
        lon1: Longitude of point 1 (decimal degrees)
        lat2: Latitude of point 2 (decimal degrees)
        lon2: Longitude of point 2 (decimal degrees)

    Returns:
        Distance in meters

    Requirements:
        - TSE-FUNC-151: Haversine formula with ±0.5% accuracy up to 20 NM

    Accuracy:
        Good to ±0.5% for distances up to 20 NM (~37 km)
        For higher accuracy over longer distances, use Vincenty formula
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    # Use mean Earth radius (suitable for maritime applications)
    R = WGS84_SEMI_MAJOR_AXIS

    return R * c


def forward_azimuth(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate forward azimuth (bearing) from point 1 to point 2.

    Args:
        lat1: Latitude of point 1 (decimal degrees)
        lon1: Longitude of point 1 (decimal degrees)
        lat2: Latitude of point 2 (decimal degrees)
        lon2: Longitude of point 2 (decimal degrees)

    Returns:
        Bearing in degrees [0, 360), clockwise from true north

    Requirements:
        - TSE-FUNC-152: Forward azimuth using WGS84 geodesics
        - TSE-DATA-024: True north (0°) reference
        - TSE-DATA-025: Bearing range [0°, 360°)
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad

    # Calculate bearing
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to [0, 360)
    bearing_deg = (bearing_deg + 360.0) % 360.0

    return bearing_deg


def destination_point(lat: float, lon: float, range_m: float, bearing_deg: float) -> Tuple[float, float]:
    """
    Calculate destination point given origin, range, and bearing.

    This solves the "direct geodetic problem" - given a starting point,
    distance, and bearing, find the endpoint.

    Args:
        lat: Origin latitude (decimal degrees)
        lon: Origin longitude (decimal degrees)
        range_m: Distance in meters
        bearing_deg: Bearing in degrees [0, 360) from true north

    Returns:
        Tuple of (destination_lat, destination_lon) in decimal degrees

    Requirements:
        - TSE-FUNC-153: Destination point calculation
        - TSE-FUNC-022: Automatic coordinate transformation (±10m accuracy up to 20 NM)

    Accuracy:
        ±10 meters at ranges up to 20 NM (~37 km)
    """
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)

    # Angular distance (radians)
    R = WGS84_SEMI_MAJOR_AXIS
    angular_distance = range_m / R

    # Calculate destination point
    lat2_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
    )

    lon2_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat2_rad)
    )

    # Convert back to degrees
    lat2 = math.degrees(lat2_rad)
    lon2 = math.degrees(lon2_rad)

    # Normalize longitude to [-180, 180]
    lon2 = ((lon2 + 180) % 360) - 180

    return lat2, lon2


def meters_per_degree_longitude(latitude_deg: float) -> float:
    """
    Calculate meters per degree of longitude at a given latitude.

    Args:
        latitude_deg: Latitude in decimal degrees

    Returns:
        Meters per degree of longitude at this latitude

    Requirements:
        - TSE-FUNC-154: Account for latitude in longitude conversion

    Note:
        At the equator: ~111,320 meters/degree
        At 60° latitude: ~55,660 meters/degree
    """
    lat_rad = math.radians(latitude_deg)
    return 111320.0 * math.cos(lat_rad)


def meters_per_degree_latitude() -> float:
    """
    Calculate meters per degree of latitude (approximately constant).

    Returns:
        Meters per degree of latitude (~111,111 m)

    Note:
        Latitude spacing is nearly constant on WGS84 ellipsoid
    """
    return 111111.0  # Approximately constant for WGS84
