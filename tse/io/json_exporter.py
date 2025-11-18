"""
JSON exporter for generating simulator input files.

Requirements:
- TSE-FUNC-080: Export scenario to JSON
- TSE-FUNC-081: Top-level structure generation
- TSE-FUNC-082: Boats array generation
- TSE-FUNC-083: Unit conversion (knots → m/s)
- TSE-FUNC-084: Dimension calculations (a, b, c, d)
- TSE-FUNC-085: Sensor configuration export
- TSE-FUNC-086: Color assignment logic
- TSE-FUNC-087: JSON pretty-printing
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from tse.models.scenario import Scenario
from tse.models.target import Target
from tse.models.own_ship import OwnShip
from tse.models.waypoint import Waypoint
from tse.models.sensor import SensorConfiguration, SensorDropout, SensorType
from tse.utils.unit_conversion import knots_to_ms


class JSONExporter:
    """
    Exports scenarios to JSON format for the simulator.

    Requirements: TSE-FUNC-080 to TSE-FUNC-087
    """

    # Default color palette for targets
    DEFAULT_COLORS = [
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
        "#FFA500",  # Orange
        "#800080",  # Purple
        "#FFC0CB",  # Pink
        "#A52A2A",  # Brown
    ]

    # Own Ship color
    OWN_SHIP_COLOR = "#0066CC"  # Blue

    def __init__(self):
        """Initialize JSON exporter."""
        self._color_index = 0

    def export_scenario(self, scenario: Scenario, filepath: str) -> bool:
        """
        Export scenario to JSON file.

        Args:
            scenario: Scenario to export
            filepath: Output file path

        Returns:
            True if export successful, False otherwise

        Requirements: TSE-FUNC-080
        """
        try:
            # Generate JSON structure
            json_data = self.generate_json(scenario)

            # Write to file with pretty-printing
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def generate_json(self, scenario: Scenario) -> Dict[str, Any]:
        """
        Generate JSON structure from scenario.

        Args:
            scenario: Scenario object

        Returns:
            Dictionary representing JSON structure

        Requirements: TSE-FUNC-081
        """
        # Reset color index
        self._color_index = 0

        # Top-level structure
        json_data = {
            "duration": scenario.duration_sec,
            "boats": []
        }

        # Add Own Ship
        if hasattr(scenario, 'own_ship') and scenario.own_ship:
            own_ship_data = self._generate_own_ship(scenario.own_ship)
            json_data["boats"].append(own_ship_data)

        # Add Targets
        if hasattr(scenario, 'targets') and scenario.targets:
            for target in scenario.targets:
                target_data = self._generate_target(target)
                json_data["boats"].append(target_data)

        return json_data

    def _generate_own_ship(self, own_ship: OwnShip) -> Dict[str, Any]:
        """
        Generate Own Ship JSON structure.

        Args:
            own_ship: OwnShip object

        Returns:
            Dictionary for Own Ship
        """
        boat_data = {
            "id": "OWN_SHIP",
            "name": "Own Ship",
            "type": "Custom",
            "initial_position": {
                "latitude": own_ship.position.latitude,
                "longitude": own_ship.position.longitude
            },
            "initial_speed": knots_to_ms(own_ship.speed_knots),
            "initial_heading": own_ship.course_deg,
            "color": self.OWN_SHIP_COLOR,
            "sensors": self._generate_sensors(own_ship.sensors) if own_ship.sensors else self._generate_default_sensors()
        }

        return boat_data

    def _generate_target(self, target: Target) -> Dict[str, Any]:
        """
        Generate target JSON structure.

        Args:
            target: Target object

        Returns:
            Dictionary for target

        Requirements: TSE-FUNC-082
        """
        boat_data = {
            "id": target.target_id,
            "name": target.name,
            "type": target.vessel_type.value if hasattr(target.vessel_type, 'value') else str(target.vessel_type),
            "initial_position": {
                "latitude": target.position.latitude,
                "longitude": target.position.longitude
            },
            "initial_speed": knots_to_ms(target.speed_knots),  # TSE-FUNC-083
            "initial_heading": target.course_deg,
            "color": self._get_next_color(),  # TSE-FUNC-086
            "sensors": self._generate_sensors(target.sensors) if target.sensors else self._generate_default_sensors()
        }

        # Add MMSI if present
        if target.mmsi:
            boat_data["mmsi"] = target.mmsi

        # Add AIS class
        if hasattr(target, 'ais_class') and target.ais_class:
            ais_class_str = target.ais_class.value if hasattr(target.ais_class, 'value') else str(target.ais_class)
            boat_data["ais_class"] = ais_class_str

        # Add navigation status
        if hasattr(target, 'nav_status') and target.nav_status:
            nav_status_str = target.nav_status.value if hasattr(target.nav_status, 'value') else str(target.nav_status)
            boat_data["navigation_status"] = nav_status_str

        # Add dimensions (TSE-FUNC-084)
        if target.dimensions:
            boat_data["dimensions"] = self._calculate_dimensions(target.dimensions)

        # Add route if present
        if hasattr(target, 'route') and target.route and len(target.route) > 0:
            boat_data["route"] = self._generate_route(target.route)

        return boat_data

    def _calculate_dimensions(self, dimensions) -> Dict[str, float]:
        """
        Calculate a, b, c, d dimensions from vessel dimensions.

        The reference point is at the center of the vessel.
        a = distance to bow (forward)
        b = distance to stern (aft)
        c = distance to port
        d = distance to starboard

        Args:
            dimensions: VesselDimensions object

        Returns:
            Dictionary with a, b, c, d values

        Requirements: TSE-FUNC-084
        """
        # Assuming reference point at center
        a = dimensions.length / 2.0  # to bow
        b = dimensions.length / 2.0  # to stern
        c = dimensions.width / 2.0   # to port
        d = dimensions.width / 2.0   # to starboard

        return {
            "a": round(a, 2),
            "b": round(b, 2),
            "c": round(c, 2),
            "d": round(d, 2)
        }

    def _generate_route(self, waypoints: List[Waypoint]) -> List[Dict[str, Any]]:
        """
        Generate route from waypoints.

        Args:
            waypoints: List of Waypoint objects

        Returns:
            List of waypoint dictionaries
        """
        route = []

        for wp in waypoints:
            if wp.position:
                wp_data = {
                    "time": wp.time_sec,
                    "position": {
                        "latitude": wp.position.latitude,
                        "longitude": wp.position.longitude
                    },
                    "speed": knots_to_ms(wp.speed_knots),
                    "heading": wp.course_deg
                }
                route.append(wp_data)

        return route

    def _generate_sensors(self, sensor_config: SensorConfiguration) -> Dict[str, Any]:
        """
        Generate sensor configuration.

        Args:
            sensor_config: SensorConfiguration object

        Returns:
            Dictionary with sensor configuration

        Requirements: TSE-FUNC-085
        """
        # Get dropouts per sensor type
        dropouts_by_sensor = {}
        if hasattr(sensor_config, 'dropouts') and sensor_config.dropouts:
            for dropout in sensor_config.dropouts:
                sensor_type = dropout.sensor_type
                if sensor_type not in dropouts_by_sensor:
                    dropouts_by_sensor[sensor_type] = []
                dropouts_by_sensor[sensor_type].append(dropout)

        sensors = {
            "ais": {
                "enabled": sensor_config.ais_enabled,
                "dropouts": self._generate_dropouts(dropouts_by_sensor.get(SensorType.AIS, []))
            },
            "radar_a": {
                "enabled": sensor_config.radar_a_enabled,
                "dropouts": self._generate_dropouts(dropouts_by_sensor.get(SensorType.RADAR_A, []))
            },
            "radar_b": {
                "enabled": sensor_config.radar_b_enabled,
                "dropouts": self._generate_dropouts(dropouts_by_sensor.get(SensorType.RADAR_B, []))
            },
            "eo": {
                "enabled": sensor_config.eo_enabled,
                "dropouts": self._generate_dropouts(dropouts_by_sensor.get(SensorType.EO, []))
            }
        }

        return sensors

    def _generate_default_sensors(self) -> Dict[str, Any]:
        """Generate default sensor configuration (all enabled, no dropouts)."""
        return {
            "ais": {"enabled": True, "dropouts": []},
            "radar_a": {"enabled": True, "dropouts": []},
            "radar_b": {"enabled": True, "dropouts": []},
            "eo": {"enabled": True, "dropouts": []}
        }

    def _generate_dropouts(self, dropouts: List[SensorDropout]) -> List[Dict[str, float]]:
        """
        Generate dropout schedule.

        Args:
            dropouts: List of SensorDropout objects

        Returns:
            List of dropout dictionaries
        """
        dropout_list = []

        for dropout in dropouts:
            dropout_data = {
                "start_time": dropout.start_time_sec,
                "end_time": dropout.end_time_sec
            }
            dropout_list.append(dropout_data)

        return dropout_list

    def _get_next_color(self) -> str:
        """
        Get next color from palette.

        Requirements: TSE-FUNC-086
        """
        color = self.DEFAULT_COLORS[self._color_index % len(self.DEFAULT_COLORS)]
        self._color_index += 1
        return color

    def export_to_string(self, scenario: Scenario, pretty: bool = True) -> str:
        """
        Export scenario to JSON string.

        Args:
            scenario: Scenario to export
            pretty: Whether to pretty-print

        Returns:
            JSON string

        Requirements: TSE-FUNC-087
        """
        json_data = self.generate_json(scenario)

        if pretty:
            return json.dumps(json_data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(json_data, ensure_ascii=False)
