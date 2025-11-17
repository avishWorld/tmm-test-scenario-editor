"""
JSON export functionality for simulator input.

This module exports TSE scenarios to the JSON format required by the
TMM CDA simulator.

Requirements:
- TSE-FUNC-080: Export to JSON
- TSE-FUNC-081: JSON includes all target data
- TSE-FUNC-082: JSON includes waypoint routes
- TSE-FUNC-083: JSON uses correct units
- TSE-FUNC-084: JSON includes sensor configurations
- TSE-FUNC-085: JSON includes dropout schedules
- TSE-FUNC-086: JSON format matches simulator spec v0.6.0+
- TSE-INTF-020: JSON schema validation
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from ..models import Scenario, Target, Waypoint
from ..utils import knots_to_mps


def _export_target(target: Target, own_ship_lat: float, own_ship_lon: float) -> Dict[str, Any]:
    """
    Export a single target to simulator JSON format.

    Args:
        target: Target object to export
        own_ship_lat: Own Ship latitude for reference
        own_ship_lon: Own Ship longitude for reference

    Returns:
        Dictionary representation for simulator
    """
    target_data = {
        "id": target.target_id,
        "name": target.name,
        "type": target.vessel_type.value,
        "mmsi": target.mmsi if target.mmsi > 0 else None,
        "ais_class": target.ais_class.value if target.ais_class.value != "None" else None,
        "navigation_status": target.nav_status.value,
        "position": {
            "latitude": target.position.latitude_deg if target.position else own_ship_lat,
            "longitude": target.position.longitude_deg if target.position else own_ship_lon,
        },
        "kinematics": {
            "speed_mps": knots_to_mps(target.speed_knots),
            "course_deg": target.course_deg,
        },
        "dimensions": {
            "length_m": target.dimensions.length_m,
            "width_m": target.dimensions.width_m,
            "height_m": target.dimensions.height_m,
            "a_m": target.dimensions.a_m,
            "b_m": target.dimensions.b_m,
            "c_m": target.dimensions.c_m,
            "d_m": target.dimensions.d_m,
        },
        "sensors": {
            "ais": target.sensors.ais_enabled,
            "radar_a": target.sensors.radar_a_enabled,
            "radar_b": target.sensors.radar_b_enabled,
            "eo": target.sensors.eo_enabled,
        },
        "route": [],
        "sensor_dropouts": [],
    }

    # Export waypoints
    for waypoint in target.route:
        target_data["route"].append({
            "index": waypoint.index,
            "time_sec": waypoint.time_sec,
            "position": {
                "latitude": waypoint.position.latitude_deg,
                "longitude": waypoint.position.longitude_deg,
            },
            "kinematics": {
                "speed_mps": knots_to_mps(waypoint.speed_knots),
                "course_deg": waypoint.course_deg,
            },
        })

    # Export sensor dropouts
    for dropout in target.dropouts:
        target_data["sensor_dropouts"].append({
            "sensor_type": dropout.sensor_type.value,
            "start_time_sec": dropout.start_time_sec,
            "end_time_sec": dropout.end_time_sec if dropout.end_time_sec != -1 else None,
            "index": dropout.dropout_index,
        })

    return target_data


def export_to_json(scenario: Scenario, file_path: str, pretty: bool = True) -> None:
    """
    Export scenario to simulator JSON format.

    Args:
        scenario: Scenario object to export
        file_path: Path to output JSON file
        pretty: If True, format JSON with indentation (default: True)

    Raises:
        ValueError: If scenario is invalid or missing required data
        IOError: If file cannot be written

    Requirements: TSE-FUNC-080 to TSE-FUNC-086
    """
    if not scenario.own_ship:
        raise ValueError("Scenario must have Own Ship defined")

    # Build simulator input JSON structure
    simulator_data = {
        "file_format": "TMM CDA Simulator Input",
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "scenario": {
            "id": scenario.scenario_id,
            "title": scenario.title,
            "description": scenario.description,
            "duration_sec": scenario.duration_sec,
            "coordinate_system": "WGS84",
        },
        "own_ship": {
            "position": {
                "latitude": scenario.own_ship.position.latitude_deg,
                "longitude": scenario.own_ship.position.longitude_deg,
            },
            "kinematics": {
                "speed_mps": knots_to_mps(scenario.own_ship.speed_knots),
                "course_deg": scenario.own_ship.course_deg,
            },
            "sensors": {
                "ais": scenario.own_ship.sensors.ais_enabled,
                "radar_a": scenario.own_ship.sensors.radar_a_enabled,
                "radar_b": scenario.own_ship.sensors.radar_b_enabled,
                "eo": scenario.own_ship.sensors.eo_enabled,
            },
        },
        "targets": [],
    }

    # Export all targets
    for target in scenario.targets:
        target_data = _export_target(
            target,
            scenario.own_ship.position.latitude_deg,
            scenario.own_ship.position.longitude_deg,
        )
        simulator_data["targets"].append(target_data)

    # Write to file
    path = Path(file_path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(simulator_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(simulator_data, f, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Failed to write JSON file: {e}")


def export_to_string(scenario: Scenario, pretty: bool = True) -> str:
    """
    Export scenario to simulator JSON string.

    Args:
        scenario: Scenario object to export
        pretty: If True, format JSON with indentation (default: True)

    Returns:
        JSON string representation

    Raises:
        ValueError: If scenario is invalid or missing required data
    """
    if not scenario.own_ship:
        raise ValueError("Scenario must have Own Ship defined")

    # Build simulator input JSON structure (same as export_to_json)
    simulator_data = {
        "file_format": "TMM CDA Simulator Input",
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "scenario": {
            "id": scenario.scenario_id,
            "title": scenario.title,
            "description": scenario.description,
            "duration_sec": scenario.duration_sec,
            "coordinate_system": "WGS84",
        },
        "own_ship": {
            "position": {
                "latitude": scenario.own_ship.position.latitude_deg,
                "longitude": scenario.own_ship.position.longitude_deg,
            },
            "kinematics": {
                "speed_mps": knots_to_mps(scenario.own_ship.speed_knots),
                "course_deg": scenario.own_ship.course_deg,
            },
            "sensors": {
                "ais": scenario.own_ship.sensors.ais_enabled,
                "radar_a": scenario.own_ship.sensors.radar_a_enabled,
                "radar_b": scenario.own_ship.sensors.radar_b_enabled,
                "eo": scenario.own_ship.sensors.eo_enabled,
            },
        },
        "targets": [],
    }

    # Export all targets
    for target in scenario.targets:
        target_data = _export_target(
            target,
            scenario.own_ship.position.latitude_deg,
            scenario.own_ship.position.longitude_deg,
        )
        simulator_data["targets"].append(target_data)

    # Return as string
    if pretty:
        return json.dumps(simulator_data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(simulator_data, ensure_ascii=False)


def get_export_summary(scenario: Scenario) -> Dict[str, Any]:
    """
    Get summary of what would be exported.

    Useful for preview/validation before actual export.

    Args:
        scenario: Scenario to analyze

    Returns:
        Dictionary with export statistics
    """
    if not scenario.own_ship:
        return {
            "valid": False,
            "error": "No Own Ship defined",
        }

    total_waypoints = sum(len(target.route) for target in scenario.targets)
    total_dropouts = sum(len(target.dropouts) for target in scenario.targets)

    targets_with_routes = sum(1 for target in scenario.targets if len(target.route) > 0)
    targets_with_dropouts = sum(1 for target in scenario.targets if len(target.dropouts) > 0)

    return {
        "valid": True,
        "scenario_id": scenario.scenario_id,
        "duration_sec": scenario.duration_sec,
        "target_count": len(scenario.targets),
        "total_waypoints": total_waypoints,
        "total_dropouts": total_dropouts,
        "targets_with_routes": targets_with_routes,
        "targets_with_dropouts": targets_with_dropouts,
        "own_ship_position": {
            "lat": scenario.own_ship.position.latitude_deg,
            "lon": scenario.own_ship.position.longitude_deg,
        },
    }
