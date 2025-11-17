"""
Project file save/load functionality.

This module handles saving and loading TSE project files in JSON format.

Requirements:
- TSE-FUNC-111: Save project to file
- TSE-FUNC-112: Load project from file
- TSE-FUNC-113: Project file versioning
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

from ..models import (
    Scenario,
    OwnShip,
    Target,
    Waypoint,
    GeoPosition,
    VesselDimensions,
    SensorConfiguration,
    SensorDropout,
    VesselType,
    AISClass,
    NavigationStatus,
    SensorType,
)


# Project file format version
PROJECT_FILE_VERSION = "1.0"


def _serialize_scenario(scenario: Scenario) -> Dict[str, Any]:
    """
    Convert Scenario object to JSON-serializable dictionary.

    Args:
        scenario: Scenario object to serialize

    Returns:
        Dictionary representation of scenario
    """
    data = {
        "scenario_id": scenario.scenario_id,
        "title": scenario.title,
        "description": scenario.description,
        "duration_sec": scenario.duration_sec,
        "coordinate_system": scenario.coordinate_system,
        "own_ship": None,
        "targets": [],
    }

    # Serialize Own Ship
    if scenario.own_ship:
        data["own_ship"] = {
            "position": {
                "latitude_deg": scenario.own_ship.position.latitude_deg,
                "longitude_deg": scenario.own_ship.position.longitude_deg,
            },
            "speed_knots": scenario.own_ship.speed_knots,
            "course_deg": scenario.own_ship.course_deg,
            "sensors": {
                "ais_enabled": scenario.own_ship.sensors.ais_enabled,
                "radar_a_enabled": scenario.own_ship.sensors.radar_a_enabled,
                "radar_b_enabled": scenario.own_ship.sensors.radar_b_enabled,
                "eo_enabled": scenario.own_ship.sensors.eo_enabled,
            },
        }

    # Serialize Targets
    for target in scenario.targets:
        target_data = {
            "target_id": target.target_id,
            "name": target.name,
            "position": None if target.position is None else {
                "latitude_deg": target.position.latitude_deg,
                "longitude_deg": target.position.longitude_deg,
            },
            "relative_range_m": target.relative_range_m,
            "relative_bearing_deg": target.relative_bearing_deg,
            "speed_knots": target.speed_knots,
            "course_deg": target.course_deg,
            "vessel_type": target.vessel_type.value,
            "dimensions": {
                "length_m": target.dimensions.length_m,
                "width_m": target.dimensions.width_m,
                "height_m": target.dimensions.height_m,
            },
            "mmsi": target.mmsi,
            "ais_class": target.ais_class.value,
            "nav_status": target.nav_status.value,
            "route": [],
            "sensors": {
                "ais_enabled": target.sensors.ais_enabled,
                "radar_a_enabled": target.sensors.radar_a_enabled,
                "radar_b_enabled": target.sensors.radar_b_enabled,
                "eo_enabled": target.sensors.eo_enabled,
            },
            "dropouts": [],
        }

        # Serialize route waypoints
        for waypoint in target.route:
            target_data["route"].append({
                "index": waypoint.index,
                "time_sec": waypoint.time_sec,
                "position": {
                    "latitude_deg": waypoint.position.latitude_deg,
                    "longitude_deg": waypoint.position.longitude_deg,
                },
                "relative_range_m": waypoint.relative_range_m,
                "relative_bearing_deg": waypoint.relative_bearing_deg,
                "speed_knots": waypoint.speed_knots,
                "course_deg": waypoint.course_deg,
            })

        # Serialize sensor dropouts
        for dropout in target.dropouts:
            target_data["dropouts"].append({
                "sensor_type": dropout.sensor_type.value,
                "start_time_sec": dropout.start_time_sec,
                "end_time_sec": dropout.end_time_sec,
                "dropout_index": dropout.dropout_index,
            })

        data["targets"].append(target_data)

    return data


def _deserialize_scenario(data: Dict[str, Any]) -> Scenario:
    """
    Convert JSON dictionary to Scenario object.

    Args:
        data: Dictionary representation of scenario

    Returns:
        Scenario object
    """
    scenario = Scenario(
        scenario_id=data["scenario_id"],
        title=data["title"],
        description=data["description"],
        duration_sec=data["duration_sec"],
        coordinate_system=data.get("coordinate_system", "geodetic"),
    )

    # Deserialize Own Ship
    if data.get("own_ship"):
        own_ship_data = data["own_ship"]
        scenario.own_ship = OwnShip(
            position=GeoPosition(
                latitude_deg=own_ship_data["position"]["latitude_deg"],
                longitude_deg=own_ship_data["position"]["longitude_deg"],
            ),
            speed_knots=own_ship_data["speed_knots"],
            course_deg=own_ship_data["course_deg"],
            sensors=SensorConfiguration(
                ais_enabled=own_ship_data["sensors"]["ais_enabled"],
                radar_a_enabled=own_ship_data["sensors"]["radar_a_enabled"],
                radar_b_enabled=own_ship_data["sensors"]["radar_b_enabled"],
                eo_enabled=own_ship_data["sensors"]["eo_enabled"],
            ),
        )

    # Deserialize Targets
    for target_data in data.get("targets", []):
        target = Target(
            target_id=target_data["target_id"],
            name=target_data["name"],
            position=None if target_data["position"] is None else GeoPosition(
                latitude_deg=target_data["position"]["latitude_deg"],
                longitude_deg=target_data["position"]["longitude_deg"],
            ),
            relative_range_m=target_data["relative_range_m"],
            relative_bearing_deg=target_data["relative_bearing_deg"],
            speed_knots=target_data["speed_knots"],
            course_deg=target_data["course_deg"],
            vessel_type=VesselType(target_data["vessel_type"]),
            dimensions=VesselDimensions(
                length_m=target_data["dimensions"]["length_m"],
                width_m=target_data["dimensions"]["width_m"],
                height_m=target_data["dimensions"]["height_m"],
            ),
            mmsi=target_data["mmsi"],
            ais_class=AISClass(target_data["ais_class"]),
            nav_status=NavigationStatus(target_data["nav_status"]),
            sensors=SensorConfiguration(
                ais_enabled=target_data["sensors"]["ais_enabled"],
                radar_a_enabled=target_data["sensors"]["radar_a_enabled"],
                radar_b_enabled=target_data["sensors"]["radar_b_enabled"],
                eo_enabled=target_data["sensors"]["eo_enabled"],
            ),
        )

        # Deserialize route waypoints
        for waypoint_data in target_data.get("route", []):
            waypoint = Waypoint(
                index=waypoint_data["index"],
                time_sec=waypoint_data["time_sec"],
                position=GeoPosition(
                    latitude_deg=waypoint_data["position"]["latitude_deg"],
                    longitude_deg=waypoint_data["position"]["longitude_deg"],
                ),
                relative_range_m=waypoint_data["relative_range_m"],
                relative_bearing_deg=waypoint_data["relative_bearing_deg"],
                speed_knots=waypoint_data["speed_knots"],
                course_deg=waypoint_data["course_deg"],
            )
            target.route.append(waypoint)

        # Deserialize sensor dropouts
        for dropout_data in target_data.get("dropouts", []):
            dropout = SensorDropout(
                sensor_type=SensorType(dropout_data["sensor_type"]),
                start_time_sec=dropout_data["start_time_sec"],
                end_time_sec=dropout_data["end_time_sec"],
                dropout_index=dropout_data["dropout_index"],
            )
            target.dropouts.append(dropout)

        scenario.targets.append(target)

    return scenario


def save_project(scenario: Scenario, file_path: str) -> None:
    """
    Save scenario to project file.

    The project file is a JSON file with metadata and scenario data.

    Args:
        scenario: Scenario object to save
        file_path: Path to save file (should end with .tse)

    Raises:
        ValueError: If file_path is invalid
        IOError: If file cannot be written

    Requirements: TSE-FUNC-111, TSE-FUNC-113
    """
    path = Path(file_path)

    # Ensure .tse extension
    if path.suffix != ".tse":
        path = path.with_suffix(".tse")

    # Create project file structure
    project_data = {
        "file_format": "TSE Project File",
        "version": PROJECT_FILE_VERSION,
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "scenario": _serialize_scenario(scenario),
    }

    # Write to file with pretty formatting
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Failed to save project to {path}: {e}")


def load_project(file_path: str) -> Scenario:
    """
    Load scenario from project file.

    Args:
        file_path: Path to project file (.tse)

    Returns:
        Scenario object loaded from file

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is invalid or version incompatible
        IOError: If file cannot be read

    Requirements: TSE-FUNC-112, TSE-FUNC-113
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")

    # Read and parse JSON
    try:
        with open(path, "r", encoding="utf-8") as f:
            project_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in project file: {e}")
    except Exception as e:
        raise IOError(f"Failed to read project file: {e}")

    # Validate file format
    if project_data.get("file_format") != "TSE Project File":
        raise ValueError("Not a valid TSE project file")

    # Check version compatibility
    version = project_data.get("version", "1.0")
    if version != PROJECT_FILE_VERSION:
        # For now, only support exact version match
        # In future, could add migration logic
        raise ValueError(
            f"Incompatible project file version: {version} "
            f"(expected {PROJECT_FILE_VERSION})"
        )

    # Deserialize scenario
    try:
        scenario = _deserialize_scenario(project_data["scenario"])
        return scenario
    except Exception as e:
        raise ValueError(f"Failed to parse scenario data: {e}")


def get_project_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata from project file without loading full scenario.

    Args:
        file_path: Path to project file (.tse)

    Returns:
        Dictionary with metadata (version, created_at, modified_at, title, etc.)

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            project_data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to read project file: {e}")

    return {
        "file_format": project_data.get("file_format"),
        "version": project_data.get("version"),
        "created_at": project_data.get("created_at"),
        "modified_at": project_data.get("modified_at"),
        "scenario_id": project_data.get("scenario", {}).get("scenario_id"),
        "title": project_data.get("scenario", {}).get("title"),
        "description": project_data.get("scenario", {}).get("description"),
    }
