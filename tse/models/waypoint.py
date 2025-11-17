"""
Waypoint data model.

Requirements:
- TSE-FUNC-040: Unlimited waypoints per target
- TSE-FUNC-041: WP1 at Time=0, matching initial position
- TSE-FUNC-042: Waypoint parameters (time, position, speed, course)
"""

from dataclasses import dataclass
from typing import Optional
from .geo import GeoPosition


@dataclass
class Waypoint:
    """
    Represents a waypoint in a target's route.

    Attributes:
        index: Sequential waypoint index (0-based)
        time_sec: Time of arrival (seconds from scenario start)
        position: Absolute geographic position (derived from relative)
        relative_range_m: Range from Own Ship at this waypoint
        relative_bearing_deg: Bearing from Own Ship at this waypoint
        speed_knots: Target speed at this waypoint
        course_deg: Target course at this waypoint

    Requirements: TSE-FUNC-040 to TSE-FUNC-042
    """
    index: int
    time_sec: float
    position: Optional[GeoPosition] = None
    relative_range_m: float = 0.0
    relative_bearing_deg: float = 0.0
    speed_knots: float = 0.0
    course_deg: float = 0.0

    def __post_init__(self):
        """Validate waypoint parameters."""
        if self.time_sec < 0:
            raise ValueError(f"Waypoint time {self.time_sec} must be >= 0")

        if not 0.0 <= self.relative_bearing_deg < 360.0:
            raise ValueError(f"Bearing {self.relative_bearing_deg}° out of range [0, 360)")

        if not 0.0 <= self.speed_knots <= 40.0:
            raise ValueError(f"Speed {self.speed_knots} out of range [0, 40] knots")

        if not 0.0 <= self.course_deg < 360.0:
            raise ValueError(f"Course {self.course_deg}° out of range [0, 360)")
