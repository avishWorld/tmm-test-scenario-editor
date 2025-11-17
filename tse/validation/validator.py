"""
Scenario validation engine.

This module provides comprehensive validation of TSE scenarios against
all business rules and constraints.

Requirements:
- TSE-FUNC-100: Unique Target ID validation
- TSE-FUNC-101: Unique MMSI validation
- TSE-FUNC-102: Minimum proximity validation (≥40m)
- TSE-FUNC-103: Maximum range validation (≤20km)
- TSE-FUNC-104: Speed and course validation
- TSE-FUNC-105: Waypoint time ordering validation
- TSE-FUNC-106: Sensor dropout overlap detection
- TSE-FUNC-107: Route reachability validation
- TSE-FUNC-108: Generate validation report
- TSE-FUNC-109: Real-time validation during editing
"""

from typing import Set, List, Dict, Tuple
from ..models import (
    Scenario,
    Target,
    Waypoint,
    ValidationReport,
    ValidationMessage,
    ValidationSeverity,
    SensorDropout,
)
from ..utils import haversine_distance


class ScenarioValidator:
    """
    Main validator class for TSE scenarios.

    Validates scenarios against all business rules and generates
    detailed validation reports.

    Requirements: TSE-FUNC-100 to TSE-FUNC-109
    """

    def __init__(self):
        """Initialize the validator."""
        self.report = ValidationReport()

    def validate(self, scenario: Scenario) -> ValidationReport:
        """
        Validate a complete scenario.

        Args:
            scenario: Scenario to validate

        Returns:
            ValidationReport with all validation messages

        Requirements: TSE-FUNC-108
        """
        self.report = ValidationReport()

        # Basic scenario validation
        self._validate_scenario_basics(scenario)

        # Own Ship validation
        self._validate_own_ship(scenario)

        # Target validation
        if scenario.own_ship:
            self._validate_targets(scenario)
            self._validate_unique_ids(scenario)
            self._validate_unique_mmsi(scenario)
            self._validate_proximity(scenario)

        return self.report

    def _validate_scenario_basics(self, scenario: Scenario) -> None:
        """Validate basic scenario properties."""
        if not scenario.scenario_id:
            self.report.add_error(
                "TSE-FUNC-001",
                "Scenario ID is required",
                "Scenario"
            )

        if not scenario.title:
            self.report.add_warning(
                "TSE-FUNC-002",
                "Scenario title is empty",
                "Scenario"
            )

        if scenario.duration_sec < 10 or scenario.duration_sec > 86400:
            self.report.add_error(
                "TSE-FUNC-004",
                f"Duration {scenario.duration_sec}s out of range [10, 86400]",
                "Scenario"
            )

    def _validate_own_ship(self, scenario: Scenario) -> None:
        """Validate Own Ship configuration."""
        if not scenario.own_ship:
            self.report.add_error(
                "TSE-FUNC-010",
                "Own Ship is required for scenario",
                "Scenario"
            )
            return

        # Validate position
        own_ship = scenario.own_ship
        if not own_ship.position:
            self.report.add_error(
                "TSE-FUNC-010",
                "Own Ship position is required",
                "Own Ship"
            )

        # Validate speed
        if not 0.0 <= own_ship.speed_knots <= 40.0:
            self.report.add_error(
                "TSE-FUNC-011",
                f"Own Ship speed {own_ship.speed_knots} out of range [0, 40] knots",
                "Own Ship"
            )

        # Validate course
        if not 0.0 <= own_ship.course_deg < 360.0:
            self.report.add_error(
                "TSE-FUNC-012",
                f"Own Ship course {own_ship.course_deg}° out of range [0, 360)",
                "Own Ship"
            )

        # Validate sensor configuration
        if not own_ship.sensors:
            self.report.add_warning(
                "TSE-FUNC-013",
                "Own Ship has no sensor configuration",
                "Own Ship"
            )
        elif not any([
            own_ship.sensors.ais_enabled,
            own_ship.sensors.radar_a_enabled,
            own_ship.sensors.radar_b_enabled,
            own_ship.sensors.eo_enabled
        ]):
            self.report.add_warning(
                "TSE-FUNC-013",
                "Own Ship has all sensors disabled",
                "Own Ship"
            )

    def _validate_targets(self, scenario: Scenario) -> None:
        """Validate all targets in scenario."""
        if len(scenario.targets) == 0:
            self.report.add_warning(
                "TSE-FUNC-020",
                "Scenario has no targets",
                "Scenario"
            )
            return

        for target in scenario.targets:
            self._validate_target(target, scenario)

    def _validate_target(self, target: Target, scenario: Scenario) -> None:
        """Validate a single target."""
        location = f"Target {target.target_id}"

        # Validate target ID
        if not target.target_id:
            self.report.add_error(
                "TSE-FUNC-023",
                "Target ID is required",
                location
            )

        # Validate position or relative coordinates
        if not target.position and scenario.own_ship:
            # Check relative coordinates are valid
            if not 40.0 <= target.relative_range_m <= 20000.0:
                self.report.add_error(
                    "TSE-FUNC-021",
                    f"Relative range {target.relative_range_m}m out of range [40, 20000]",
                    location
                )

            if not 0.0 <= target.relative_bearing_deg < 360.0:
                self.report.add_error(
                    "TSE-FUNC-021",
                    f"Relative bearing {target.relative_bearing_deg}° out of range [0, 360)",
                    location
                )

        # Validate speed
        if not 0.0 <= target.speed_knots <= 40.0:
            self.report.add_error(
                "TSE-FUNC-024",
                f"Speed {target.speed_knots} out of range [0, 40] knots",
                location
            )

        # Validate course
        if not 0.0 <= target.course_deg < 360.0:
            self.report.add_error(
                "TSE-FUNC-025",
                f"Course {target.course_deg}° out of range [0, 360)",
                location
            )

        # Validate MMSI if present
        if target.mmsi != 0:
            if not 100000000 <= target.mmsi <= 999999999:
                self.report.add_error(
                    "TSE-FUNC-028",
                    f"MMSI {target.mmsi} is not a valid 9-digit number",
                    location
                )

        # Validate dimensions
        if not target.dimensions:
            self.report.add_warning(
                "TSE-FUNC-026",
                "Target has no dimensions defined",
                location
            )

        # Validate route waypoints
        if len(target.route) > 0:
            self._validate_route(target, scenario)

        # Validate sensor dropouts
        if len(target.dropouts) > 0:
            self._validate_dropouts(target, scenario)

    def _validate_route(self, target: Target, scenario: Scenario) -> None:
        """Validate target route waypoints."""
        location = f"Target {target.target_id} Route"

        if len(target.route) == 0:
            return

        # Check waypoint time ordering (TSE-FUNC-105)
        for i, waypoint in enumerate(target.route):
            # Validate time is within scenario duration
            if waypoint.time_sec > scenario.duration_sec:
                self.report.add_error(
                    "TSE-FUNC-105",
                    f"Waypoint {i} time {waypoint.time_sec}s exceeds scenario duration {scenario.duration_sec}s",
                    location
                )

            # Validate time ordering
            if i > 0:
                prev_waypoint = target.route[i - 1]
                if waypoint.time_sec <= prev_waypoint.time_sec:
                    self.report.add_error(
                        "TSE-FUNC-105",
                        f"Waypoint {i} time {waypoint.time_sec}s not greater than previous {prev_waypoint.time_sec}s",
                        location
                    )

            # Validate waypoint kinematics
            if not 0.0 <= waypoint.speed_knots <= 40.0:
                self.report.add_error(
                    "TSE-FUNC-104",
                    f"Waypoint {i} speed {waypoint.speed_knots} out of range [0, 40] knots",
                    location
                )

            if not 0.0 <= waypoint.course_deg < 360.0:
                self.report.add_error(
                    "TSE-FUNC-104",
                    f"Waypoint {i} course {waypoint.course_deg}° out of range [0, 360)",
                    location
                )

        # Validate route reachability (TSE-FUNC-107)
        self._validate_route_reachability(target, scenario)

    def _validate_route_reachability(self, target: Target, scenario: Scenario) -> None:
        """Validate that route waypoints are reachable given time and speed."""
        location = f"Target {target.target_id} Route"

        if len(target.route) < 2:
            return

        for i in range(1, len(target.route)):
            prev_wp = target.route[i - 1]
            curr_wp = target.route[i]

            # Calculate distance between waypoints
            distance_m = haversine_distance(
                prev_wp.position.latitude_deg,
                prev_wp.position.longitude_deg,
                curr_wp.position.latitude_deg,
                curr_wp.position.longitude_deg
            )

            # Calculate time available
            time_available_sec = curr_wp.time_sec - prev_wp.time_sec

            if time_available_sec <= 0:
                continue  # Already caught by time ordering check

            # Calculate required speed (assume average speed between waypoints)
            avg_speed_knots = (prev_wp.speed_knots + curr_wp.speed_knots) / 2.0
            avg_speed_mps = avg_speed_knots * 0.51444  # knots to m/s

            # Calculate distance reachable in available time
            max_distance_m = avg_speed_mps * time_available_sec

            # Check if waypoint is reachable (with 10% tolerance)
            if distance_m > max_distance_m * 1.1:
                self.report.add_warning(
                    "TSE-FUNC-107",
                    f"Waypoint {i} may not be reachable: {distance_m:.0f}m in {time_available_sec:.0f}s "
                    f"requires {(distance_m / time_available_sec) * 1.944:.1f} knots (avg speed: {avg_speed_knots:.1f} knots)",
                    location
                )

    def _validate_dropouts(self, target: Target, scenario: Scenario) -> None:
        """Validate sensor dropouts."""
        location = f"Target {target.target_id} Dropouts"

        # Validate each dropout
        for i, dropout in enumerate(target.dropouts):
            # Validate times
            if dropout.start_time_sec < 0:
                self.report.add_error(
                    "TSE-FUNC-050",
                    f"Dropout {i} start time {dropout.start_time_sec}s is negative",
                    location
                )

            if dropout.end_time_sec != -1 and dropout.end_time_sec <= dropout.start_time_sec:
                self.report.add_error(
                    "TSE-FUNC-050",
                    f"Dropout {i} end time {dropout.end_time_sec}s not greater than start time {dropout.start_time_sec}s",
                    location
                )

            if dropout.start_time_sec > scenario.duration_sec:
                self.report.add_warning(
                    "TSE-FUNC-050",
                    f"Dropout {i} starts after scenario ends",
                    location
                )

        # Check for overlapping dropouts (TSE-FUNC-106)
        self._validate_dropout_overlaps(target)

    def _validate_dropout_overlaps(self, target: Target) -> None:
        """Check for overlapping sensor dropouts."""
        location = f"Target {target.target_id} Dropouts"

        # Group dropouts by sensor type
        by_sensor: Dict[str, List[SensorDropout]] = {}
        for dropout in target.dropouts:
            sensor_type = dropout.sensor_type.value
            if sensor_type not in by_sensor:
                by_sensor[sensor_type] = []
            by_sensor[sensor_type].append(dropout)

        # Check for overlaps within each sensor type
        for sensor_type, dropouts in by_sensor.items():
            for i, dropout1 in enumerate(dropouts):
                for j, dropout2 in enumerate(dropouts):
                    if i >= j:
                        continue

                    if dropout1.overlaps_with(dropout2):
                        self.report.add_error(
                            "TSE-FUNC-106",
                            f"{sensor_type} dropout {dropout1.dropout_index} overlaps with dropout {dropout2.dropout_index}",
                            location
                        )

    def _validate_unique_ids(self, scenario: Scenario) -> None:
        """Validate that all target IDs are unique (TSE-FUNC-100)."""
        seen_ids: Set[str] = set()
        duplicates: Set[str] = set()

        for target in scenario.targets:
            if target.target_id in seen_ids:
                duplicates.add(target.target_id)
            seen_ids.add(target.target_id)

        for target_id in duplicates:
            self.report.add_error(
                "TSE-FUNC-100",
                f"Duplicate Target ID: {target_id}",
                "Scenario"
            )

    def _validate_unique_mmsi(self, scenario: Scenario) -> None:
        """Validate that all MMSI numbers are unique (TSE-FUNC-101)."""
        seen_mmsi: Set[int] = set()
        duplicates: Set[int] = set()

        for target in scenario.targets:
            if target.mmsi == 0:
                continue  # Skip unassigned MMSI

            if target.mmsi in seen_mmsi:
                duplicates.add(target.mmsi)
            seen_mmsi.add(target.mmsi)

        for mmsi in duplicates:
            self.report.add_error(
                "TSE-FUNC-101",
                f"Duplicate MMSI: {mmsi}",
                "Scenario"
            )

    def _validate_proximity(self, scenario: Scenario) -> None:
        """Validate target proximity constraints (TSE-FUNC-102, TSE-FUNC-103)."""
        if not scenario.own_ship or not scenario.own_ship.position:
            return

        own_pos = scenario.own_ship.position

        # Check each target's proximity to Own Ship
        for target in scenario.targets:
            if not target.position:
                continue

            distance_m = haversine_distance(
                own_pos.latitude_deg,
                own_pos.longitude_deg,
                target.position.latitude_deg,
                target.position.longitude_deg
            )

            location = f"Target {target.target_id}"

            # Minimum proximity (TSE-FUNC-102)
            if distance_m < 40.0:
                self.report.add_error(
                    "TSE-FUNC-102",
                    f"Target too close to Own Ship: {distance_m:.1f}m < 40m minimum",
                    location
                )

            # Maximum range (TSE-FUNC-103)
            if distance_m > 20000.0:
                self.report.add_warning(
                    "TSE-FUNC-103",
                    f"Target beyond maximum range: {distance_m:.1f}m > 20km",
                    location
                )

        # Check target-to-target proximity
        for i, target1 in enumerate(scenario.targets):
            if not target1.position:
                continue

            for j, target2 in enumerate(scenario.targets):
                if i >= j or not target2.position:
                    continue

                distance_m = haversine_distance(
                    target1.position.latitude_deg,
                    target1.position.longitude_deg,
                    target2.position.latitude_deg,
                    target2.position.longitude_deg
                )

                # Warn if targets are very close
                if distance_m < 100.0:
                    self.report.add_warning(
                        "TSE-FUNC-102",
                        f"Targets {target1.target_id} and {target2.target_id} are very close: {distance_m:.1f}m",
                        "Scenario"
                    )


def validate_scenario(scenario: Scenario) -> ValidationReport:
    """
    Convenience function to validate a scenario.

    Args:
        scenario: Scenario to validate

    Returns:
        ValidationReport with all validation messages

    Requirements: TSE-FUNC-108
    """
    validator = ScenarioValidator()
    return validator.validate(scenario)
