"""
Utility functions and helper modules.
"""

from .id_generator import (
    MMSIGenerator,
    TargetIDGenerator,
    generate_mmsi,
    generate_target_id,
    mark_mmsi_used,
    mark_target_id_used,
    reset_generators,
)
from .geo_calc import (
    haversine_distance,
    forward_azimuth,
    destination_point,
    meters_per_degree_longitude,
    meters_per_degree_latitude,
)
from .unit_conversion import (
    knots_to_mps,
    mps_to_knots,
    meters_to_nautical_miles,
    nautical_miles_to_meters,
)

__all__ = [
    # ID Generators
    "MMSIGenerator",
    "TargetIDGenerator",
    "generate_mmsi",
    "generate_target_id",
    "mark_mmsi_used",
    "mark_target_id_used",
    "reset_generators",
    # Geographic Calculations
    "haversine_distance",
    "forward_azimuth",
    "destination_point",
    "meters_per_degree_longitude",
    "meters_per_degree_latitude",
    # Unit Conversions
    "knots_to_mps",
    "mps_to_knots",
    "meters_to_nautical_miles",
    "nautical_miles_to_meters",
]
