"""
Target data model.

Requirements:
- TSE-FUNC-020: Unlimited targets support
- TSE-FUNC-021: Relative positioning (range, bearing)
- TSE-FUNC-022: Automatic absolute coordinate calculation
- TSE-FUNC-023: Unique Target ID auto-assignment
- TSE-FUNC-024: Target speed (0-40 knots)
- TSE-FUNC-025: Target course (0-360°)
- TSE-FUNC-026: Predefined vessel types
- TSE-FUNC-028: MMSI auto-generation
- TSE-FUNC-029: AIS class (A, B, or None)
"""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import Enum
from .geo import GeoPosition, VesselDimensions
from .sensor import SensorConfiguration, SensorDropout

if TYPE_CHECKING:
    from .waypoint import Waypoint


class VesselType(Enum):
    """
    Predefined vessel types with default dimensions.

    Requirements: TSE-FUNC-026
    """
    SMALL_BOAT = "Small_Boat"  # 10-30m
    MEDIUM_CARGO = "Medium_Cargo"  # 50-100m
    LARGE_CARGO = "Large_Cargo"  # 150-250m
    TANKER = "Tanker"  # 200-350m
    NAVIGATION_BUOY = "Navigation_Buoy"  # 5m
    CUSTOM = "Custom"


class AISClass(Enum):
    """AIS class enumeration."""
    CLASS_A = "A"
    CLASS_B = "B"
    NONE = "None"


class NavigationStatus(Enum):
    """
    Navigation status enumeration.

    Requirements: TSE-FUNC-030
    """
    MOORED = "Moored"
    AT_ANCHOR = "At anchor"
    UNDER_WAY_USING_ENGINE = "Under way using engine"
    NOT_UNDER_COMMAND = "Not under command"


@dataclass
class Target:
    """
    Represents a maritime target in the scenario.

    Attributes:
        target_id: Unique identifier (e.g., "T1", "T2")
        name: Human-readable target name
        position: Absolute geographic position (derived from relative)
        relative_range_m: Range from Own Ship in meters
        relative_bearing_deg: Bearing from Own Ship in degrees
        speed_knots: Target speed in knots [0, 40]
        course_deg: Target course in degrees [0, 360]
        vessel_type: Type of vessel
        dimensions: Physical dimensions
        mmsi: Maritime Mobile Service Identity (9 digits)
        ais_class: AIS class (A, B, or None)
        nav_status: Navigation status
        route: List of waypoints for moving targets
        sensors: Sensor configuration
        dropouts: List of sensor dropouts

    Requirements: TSE-FUNC-020 to TSE-FUNC-030
    """
    target_id: str = ""
    name: str = ""
    position: Optional[GeoPosition] = None
    relative_range_m: float = 1000.0
    relative_bearing_deg: float = 0.0
    speed_knots: float = 0.0
    course_deg: float = 0.0
    vessel_type: VesselType = VesselType.MEDIUM_CARGO
    dimensions: Optional[VesselDimensions] = None
    mmsi: int = 0
    ais_class: AISClass = AISClass.CLASS_A
    nav_status: NavigationStatus = NavigationStatus.UNDER_WAY_USING_ENGINE
    route: List["Waypoint"] = field(default_factory=list)
    sensors: SensorConfiguration = field(default_factory=SensorConfiguration)
    dropouts: List[SensorDropout] = field(default_factory=list)

    def __post_init__(self):
        """Validate target parameters."""
        # TSE-FUNC-021: Relative positioning validation
        if not 40.0 <= self.relative_range_m <= 20000.0:
            raise ValueError(f"Range {self.relative_range_m}m out of range [40, 20000]")

        if not 0.0 <= self.relative_bearing_deg < 360.0:
            raise ValueError(f"Bearing {self.relative_bearing_deg}° out of range [0, 360)")

        # TSE-FUNC-024: Speed validation
        if not 0.0 <= self.speed_knots <= 40.0:
            raise ValueError(f"Speed {self.speed_knots} out of range [0, 40] knots")

        # TSE-FUNC-025: Course validation
        if not 0.0 <= self.course_deg < 360.0:
            raise ValueError(f"Course {self.course_deg}° out of range [0, 360)")

        # Default dimensions based on vessel type
        if self.dimensions is None:
            self.dimensions = self._get_default_dimensions()

    def _get_default_dimensions(self) -> VesselDimensions:
        """
        Get default dimensions for vessel type.

        Requirements: TSE-FUNC-026
        """
        defaults = {
            VesselType.SMALL_BOAT: (20.0, 5.0, 3.0),
            VesselType.MEDIUM_CARGO: (75.0, 12.0, 8.0),
            VesselType.LARGE_CARGO: (200.0, 30.0, 15.0),
            VesselType.TANKER: (275.0, 45.0, 20.0),
            VesselType.NAVIGATION_BUOY: (5.0, 5.0, 2.0),
            VesselType.CUSTOM: (50.0, 10.0, 5.0),
        }

        length, width, height = defaults.get(self.vessel_type, (50.0, 10.0, 5.0))
        return VesselDimensions(length, width, height)
