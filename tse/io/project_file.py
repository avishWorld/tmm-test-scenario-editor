"""
Project file I/O for saving and loading scenarios.

Requirements:
- TSE-FUNC-111: Save project to file
- TSE-FUNC-112: Load project from file
- TSE-FUNC-162: File format versioning
- TSE-DATA-010: JSON file format
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from tse.models.scenario import Scenario
from tse.models.target import Target
from tse.models.own_ship import OwnShip
from tse.models.waypoint import Waypoint
from tse.models.geo import GeoPosition, VesselDimensions
from tse.models.sensor import SensorConfiguration, SensorDropout, SensorType


class ProjectFile:
    """
    Handles saving and loading of project files (.tse format).

    File format: JSON with versioning
    Extension: .tse (Test Scenario Editor)

    Requirements: TSE-FUNC-111, TSE-FUNC-112, TSE-FUNC-162
    """

    # Current file format version
    FORMAT_VERSION = "1.0"

    @staticmethod
    def save_project(scenario: Scenario, filepath: str) -> bool:
        """
        Save scenario to project file.

        Args:
            scenario: Scenario to save
            filepath: Output file path

        Returns:
            True if save successful, False otherwise

        Requirements: TSE-FUNC-111
        """
        try:
            # Convert scenario to dictionary
            project_data = ProjectFile._scenario_to_dict(scenario)

            # Add metadata
            project_data["_metadata"] = {
                "version": ProjectFile.FORMAT_VERSION,
                "saved_at": datetime.now().isoformat(),
                "application": "TMM Test Scenario Editor"
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Save failed: {e}")
            return False

    @staticmethod
    def load_project(filepath: str) -> Tuple[Optional[Scenario], Optional[str]]:
        """
        Load scenario from project file.

        Args:
            filepath: Project file path

        Returns:
            Tuple of (Scenario object or None, error message or None)

        Requirements: TSE-FUNC-112
        """
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Check version
            metadata = project_data.get("_metadata", {})
            version = metadata.get("version", "unknown")

            if version != ProjectFile.FORMAT_VERSION:
                print(f"Warning: File version {version}, current version {ProjectFile.FORMAT_VERSION}")

            # Convert to scenario
            scenario = ProjectFile._dict_to_scenario(project_data)

            return (scenario, None)

        except FileNotFoundError:
            return (None, f"File not found: {filepath}")

        except json.JSONDecodeError as e:
            return (None, f"Invalid JSON: {e}")

        except Exception as e:
            return (None, f"Load error: {e}")

    @staticmethod
    def _scenario_to_dict(scenario: Scenario) -> Dict[str, Any]:
        """Convert Scenario object to dictionary."""
        data = {
            "scenario_id": scenario.scenario_id,
            "title": scenario.title,
            "description": scenario.description,
            "duration_sec": scenario.duration_sec,
            "coordinate_system": scenario.coordinate_system
        }

        # Add Own Ship
        if hasattr(scenario, 'own_ship') and scenario.own_ship:
            data["own_ship"] = ProjectFile._own_ship_to_dict(scenario.own_ship)

        # Add Targets
        if hasattr(scenario, 'targets') and scenario.targets:
            data["targets"] = [ProjectFile._target_to_dict(t) for t in scenario.targets]

        return data

    @staticmethod
    def _own_ship_to_dict(own_ship: OwnShip) -> Dict[str, Any]:
        """Convert OwnShip to dictionary."""
        data = {
            "position": {
                "latitude": own_ship.position.latitude,
                "longitude": own_ship.position.longitude
            },
            "speed_knots": own_ship.speed_knots,
            "course_deg": own_ship.course_deg
        }

        if own_ship.sensors:
            data["sensors"] = ProjectFile._sensors_to_dict(own_ship.sensors)

        return data

    @staticmethod
    def _target_to_dict(target: Target) -> Dict[str, Any]:
        """Convert Target to dictionary."""
        data = {
            "target_id": target.target_id,
            "name": target.name,
            "relative_range_m": target.relative_range_m,
            "relative_bearing_deg": target.relative_bearing_deg,
            "speed_knots": target.speed_knots,
            "course_deg": target.course_deg,
            "vessel_type": target.vessel_type.value if hasattr(target.vessel_type, 'value') else str(target.vessel_type),
            "mmsi": target.mmsi
        }

        if target.position:
            data["position"] = {
                "latitude": target.position.latitude,
                "longitude": target.position.longitude
            }

        if target.dimensions:
            data["dimensions"] = {
                "length": target.dimensions.length,
                "width": target.dimensions.width,
                "height": target.dimensions.height
            }

        if hasattr(target, 'ais_class') and target.ais_class:
            data["ais_class"] = target.ais_class.value if hasattr(target.ais_class, 'value') else str(target.ais_class)

        if hasattr(target, 'nav_status') and target.nav_status:
            data["nav_status"] = target.nav_status.value if hasattr(target.nav_status, 'value') else str(target.nav_status)

        if target.sensors:
            data["sensors"] = ProjectFile._sensors_to_dict(target.sensors)

        if hasattr(target, 'route') and target.route:
            data["route"] = [ProjectFile._waypoint_to_dict(wp) for wp in target.route]

        if hasattr(target, 'dropouts') and target.dropouts:
            data["dropouts"] = [ProjectFile._dropout_to_dict(d) for d in target.dropouts]

        return data

    @staticmethod
    def _waypoint_to_dict(waypoint: Waypoint) -> Dict[str, Any]:
        """Convert Waypoint to dictionary."""
        data = {
            "time_sec": waypoint.time_sec,
            "speed_knots": waypoint.speed_knots,
            "course_deg": waypoint.course_deg
        }

        if waypoint.position:
            data["position"] = {
                "latitude": waypoint.position.latitude,
                "longitude": waypoint.position.longitude
            }

        return data

    @staticmethod
    def _sensors_to_dict(sensors: SensorConfiguration) -> Dict[str, Any]:
        """Convert SensorConfiguration to dictionary."""
        return {
            "ais_enabled": sensors.ais_enabled,
            "radar_a_enabled": sensors.radar_a_enabled,
            "radar_b_enabled": sensors.radar_b_enabled,
            "eo_enabled": sensors.eo_enabled
        }

    @staticmethod
    def _dropout_to_dict(dropout: SensorDropout) -> Dict[str, Any]:
        """Convert SensorDropout to dictionary."""
        return {
            "sensor_type": dropout.sensor_type.value if hasattr(dropout.sensor_type, 'value') else str(dropout.sensor_type),
            "start_time_sec": dropout.start_time_sec,
            "end_time_sec": dropout.end_time_sec
        }

    @staticmethod
    def _dict_to_scenario(data: Dict[str, Any]) -> Scenario:
        """Convert dictionary to Scenario object."""
        scenario = Scenario(
            scenario_id=data.get("scenario_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            duration_sec=data.get("duration_sec", 60),
            coordinate_system=data.get("coordinate_system", "geodetic")
        )

        # Load Own Ship
        if "own_ship" in data:
            scenario.own_ship = ProjectFile._dict_to_own_ship(data["own_ship"])

        # Load Targets
        if "targets" in data:
            scenario.targets = [ProjectFile._dict_to_target(t) for t in data["targets"]]

        return scenario

    @staticmethod
    def _dict_to_own_ship(data: Dict[str, Any]) -> OwnShip:
        """Convert dictionary to OwnShip."""
        position = GeoPosition(
            latitude=data["position"]["latitude"],
            longitude=data["position"]["longitude"]
        )

        own_ship = OwnShip(
            position=position,
            speed_knots=data.get("speed_knots", 0.0),
            course_deg=data.get("course_deg", 0.0)
        )

        if "sensors" in data:
            own_ship.sensors = ProjectFile._dict_to_sensors(data["sensors"])

        return own_ship

    @staticmethod
    def _dict_to_target(data: Dict[str, Any]) -> Target:
        """Convert dictionary to Target."""
        from tse.models.target import VesselType, AISClass, NavigationStatus

        # Parse vessel type
        vessel_type_str = data.get("vessel_type", "Medium_Cargo")
        vessel_type = VesselType[vessel_type_str.upper()] if hasattr(VesselType, vessel_type_str.upper()) else VesselType.MEDIUM_CARGO

        target = Target(
            target_id=data.get("target_id", ""),
            name=data.get("name", ""),
            relative_range_m=data.get("relative_range_m", 1000.0),
            relative_bearing_deg=data.get("relative_bearing_deg", 0.0),
            speed_knots=data.get("speed_knots", 0.0),
            course_deg=data.get("course_deg", 0.0),
            vessel_type=vessel_type,
            mmsi=data.get("mmsi", 0)
        )

        # Load position
        if "position" in data:
            target.position = GeoPosition(
                latitude=data["position"]["latitude"],
                longitude=data["position"]["longitude"]
            )

        # Load dimensions
        if "dimensions" in data:
            target.dimensions = VesselDimensions(
                length=data["dimensions"]["length"],
                width=data["dimensions"]["width"],
                height=data["dimensions"]["height"]
            )

        # Load AIS class
        if "ais_class" in data:
            ais_class_str = data["ais_class"]
            if ais_class_str == "A":
                target.ais_class = AISClass.CLASS_A
            elif ais_class_str == "B":
                target.ais_class = AISClass.CLASS_B
            else:
                target.ais_class = AISClass.NONE

        # Load navigation status
        if "nav_status" in data:
            target.nav_status = NavigationStatus[data["nav_status"].upper().replace(" ", "_")]

        # Load sensors
        if "sensors" in data:
            target.sensors = ProjectFile._dict_to_sensors(data["sensors"])

        # Load route
        if "route" in data:
            target.route = [ProjectFile._dict_to_waypoint(wp) for wp in data["route"]]

        # Load dropouts
        if "dropouts" in data:
            target.dropouts = [ProjectFile._dict_to_dropout(d) for d in data["dropouts"]]

        return target

    @staticmethod
    def _dict_to_waypoint(data: Dict[str, Any]) -> Waypoint:
        """Convert dictionary to Waypoint."""
        waypoint = Waypoint(
            time_sec=data.get("time_sec", 0.0),
            speed_knots=data.get("speed_knots", 0.0),
            course_deg=data.get("course_deg", 0.0)
        )

        if "position" in data:
            waypoint.position = GeoPosition(
                latitude=data["position"]["latitude"],
                longitude=data["position"]["longitude"]
            )

        return waypoint

    @staticmethod
    def _dict_to_sensors(data: Dict[str, Any]) -> SensorConfiguration:
        """Convert dictionary to SensorConfiguration."""
        return SensorConfiguration(
            ais_enabled=data.get("ais_enabled", True),
            radar_a_enabled=data.get("radar_a_enabled", True),
            radar_b_enabled=data.get("radar_b_enabled", True),
            eo_enabled=data.get("eo_enabled", True)
        )

    @staticmethod
    def _dict_to_dropout(data: Dict[str, Any]) -> SensorDropout:
        """Convert dictionary to SensorDropout."""
        sensor_type_str = data.get("sensor_type", "AIS")
        sensor_type = SensorType[sensor_type_str.upper()]

        return SensorDropout(
            sensor_type=sensor_type,
            start_time_sec=data.get("start_time_sec", 0.0),
            end_time_sec=data.get("end_time_sec", 60.0)
        )
