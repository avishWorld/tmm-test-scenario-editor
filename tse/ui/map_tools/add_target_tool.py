"""
Add Target tool for interactive target placement on map.

Requirements:
- TSE-FUNC-066: Add target by clicking map
- TSE-FUNC-021: Relative positioning (range, bearing)
- TSE-FUNC-022: Automatic coordinate transformation
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Tuple

from tse.models.target import Target, VesselType
from tse.models.geo import GeoPosition
from tse.models.own_ship import OwnShip
from tse.utils.geo_calc import haversine_distance, forward_azimuth


class AddTargetTool(QObject):
    """
    Interactive tool for adding targets to the scenario via map clicks.

    Features:
    - Click map to place target
    - Automatic calculation of range and bearing from Own Ship
    - Real-time position updates
    - Target preview on hover

    Requirements: TSE-FUNC-066, TSE-FUNC-021, TSE-FUNC-022
    """

    # Signals
    target_added = pyqtSignal(Target)  # Emitted when target is placed
    preview_position = pyqtSignal(float, float)  # Emitted on mouse move

    def __init__(self, parent=None):
        """Initialize Add Target tool."""
        super().__init__(parent)

        self._active = False
        self._own_ship: Optional[OwnShip] = None
        self._default_vessel_type = VesselType.MEDIUM_CARGO
        self._next_target_id = 1

    def set_own_ship(self, own_ship: OwnShip):
        """
        Set Own Ship for relative positioning calculations.

        Args:
            own_ship: Own Ship object
        """
        self._own_ship = own_ship

    def set_active(self, active: bool):
        """
        Activate or deactivate the tool.

        Args:
            active: True to activate, False to deactivate
        """
        self._active = active

    def is_active(self) -> bool:
        """Check if tool is active."""
        return self._active

    def set_default_vessel_type(self, vessel_type: VesselType):
        """
        Set default vessel type for new targets.

        Args:
            vessel_type: Vessel type
        """
        self._default_vessel_type = vessel_type

    def handle_map_click(self, lat: float, lon: float) -> Optional[Target]:
        """
        Handle map click event to add target.

        Args:
            lat: Clicked latitude
            lon: Clicked longitude

        Returns:
            Created Target object or None if failed

        Requirements: TSE-FUNC-066
        """
        if not self._active or not self._own_ship:
            return None

        # Calculate range and bearing from Own Ship
        range_m, bearing_deg = self._calculate_relative_position(lat, lon)

        # Create new target
        target = self._create_target(lat, lon, range_m, bearing_deg)

        # Emit signal
        self.target_added.emit(target)

        # Increment target ID counter
        self._next_target_id += 1

        return target

    def handle_mouse_move(self, lat: float, lon: float):
        """
        Handle mouse move for preview.

        Args:
            lat: Mouse latitude
            lon: Mouse longitude
        """
        if self._active:
            self.preview_position.emit(lat, lon)

    def _calculate_relative_position(self, target_lat: float, target_lon: float) -> Tuple[float, float]:
        """
        Calculate range and bearing from Own Ship to target position.

        Args:
            target_lat: Target latitude
            target_lon: Target longitude

        Returns:
            Tuple of (range_m, bearing_deg)

        Requirements: TSE-FUNC-021, TSE-FUNC-022
        """
        if not self._own_ship or not self._own_ship.position:
            return (1000.0, 0.0)  # Default values

        own_lat = self._own_ship.position.latitude
        own_lon = self._own_ship.position.longitude

        # Calculate distance using Haversine formula
        range_m = haversine_distance(own_lat, own_lon, target_lat, target_lon)

        # Calculate bearing
        bearing_deg = forward_azimuth(own_lat, own_lon, target_lat, target_lon)

        return (range_m, bearing_deg)

    def _create_target(self, lat: float, lon: float, range_m: float, bearing_deg: float) -> Target:
        """
        Create a new target object.

        Args:
            lat: Target latitude
            lon: Target longitude
            range_m: Range from Own Ship in meters
            bearing_deg: Bearing from Own Ship in degrees

        Returns:
            New Target object
        """
        target_id = f"T{self._next_target_id}"
        name = f"Target {self._next_target_id}"

        target = Target(
            target_id=target_id,
            name=name,
            position=GeoPosition(latitude=lat, longitude=lon),
            relative_range_m=range_m,
            relative_bearing_deg=bearing_deg,
            speed_knots=0.0,  # Default: stationary
            course_deg=0.0,
            vessel_type=self._default_vessel_type,
            mmsi=self._generate_mmsi()
        )

        return target

    def _generate_mmsi(self) -> int:
        """
        Generate a unique MMSI number for the target.

        Returns:
            9-digit MMSI number

        Requirements: TSE-FUNC-028
        """
        # Generate MMSI in test range (starting with 970-979 for testing)
        # Format: 970XXXXXX where XXXXXX is a sequence number
        base_mmsi = 970000000
        return base_mmsi + self._next_target_id

    def reset_target_counter(self):
        """Reset the target ID counter to 1."""
        self._next_target_id = 1
