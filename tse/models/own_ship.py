"""
Own Ship data model.

Requirements:
- TSE-FUNC-010: Own Ship position (lat/lon)
- TSE-FUNC-011: Own Ship speed (0-40 knots)
- TSE-FUNC-012: Own Ship course (0-360°)
- TSE-FUNC-013: Own Ship sensor suite configuration
"""

from dataclasses import dataclass, field
from .geo import GeoPosition
from .sensor import SensorConfiguration


@dataclass
class OwnShip:
    """
    Represents the Own Ship (reference vessel).

    Own Ship is the vessel carrying the CDA system, from which all
    relative measurements are made.

    Attributes:
        position: Geographic position (WGS84)
        speed_knots: Initial speed in knots [0, 40]
        course_deg: Initial course in degrees [0, 360]
        sensors: Available sensor suite

    Requirements: TSE-FUNC-010 to TSE-FUNC-013
    """
    position: GeoPosition
    speed_knots: float = 0.0
    course_deg: float = 0.0
    sensors: SensorConfiguration = field(default_factory=SensorConfiguration)

    def __post_init__(self):
        """Validate Own Ship parameters."""
        # TSE-FUNC-011: Speed validation
        if not 0.0 <= self.speed_knots <= 40.0:
            raise ValueError(f"Own Ship speed {self.speed_knots} out of range [0, 40] knots")

        # TSE-FUNC-012: Course validation
        if not 0.0 <= self.course_deg < 360.0:
            raise ValueError(f"Own Ship course {self.course_deg} out of range [0, 360)")
