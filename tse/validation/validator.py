"""
Main validation engine for scenarios and components.

Requirements:
- TSE-FUNC-040: Comprehensive scenario validation
- TSE-FUNC-041: Real-time validation feedback
- TSE-FUNC-042: Validation error reporting
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from tse.models.scenario import Scenario
from tse.models.target import Target
from tse.models.own_ship import OwnShip
from tse.validation.route_validator import RouteValidator, ValidationIssue
from tse.validation.dropout_validator import DropoutValidator


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    ERROR = "error"      # Critical issue, scenario cannot be used
    WARNING = "warning"  # Non-critical issue, scenario may work but with issues
    INFO = "info"        # Informational message


@dataclass
class ValidationResult:
    """
    Result of validation operation.

    Attributes:
        is_valid: True if no errors found
        issues: List of validation issues
        error_count: Number of errors
        warning_count: Number of warnings
    """
    is_valid: bool
    issues: List[ValidationIssue]
    error_count: int = 0
    warning_count: int = 0

    def __post_init__(self):
        """Calculate counts from issues."""
        self.error_count = sum(1 for i in self.issues if i.severity == "error")
        self.warning_count = sum(1 for i in self.issues if i.severity == "warning")
        self.is_valid = self.error_count == 0

    def get_summary(self) -> str:
        """Get validation summary string."""
        if self.is_valid and self.warning_count == 0:
            return "✓ Validation passed"
        elif self.is_valid:
            return f"✓ Validation passed with {self.warning_count} warning(s)"
        else:
            return f"✗ Validation failed: {self.error_count} error(s), {self.warning_count} warning(s)"

    def get_errors(self) -> List[ValidationIssue]:
        """Get only error issues."""
        return [i for i in self.issues if i.severity == "error"]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning issues."""
        return [i for i in self.issues if i.severity == "warning"]


class ScenarioValidator:
    """
    Main validation engine for scenarios.

    Coordinates all validation subsystems and provides
    comprehensive scenario validation.

    Requirements: TSE-FUNC-040, TSE-FUNC-041, TSE-FUNC-042
    """

    def __init__(self):
        """Initialize validator."""
        self._route_validator = RouteValidator()
        self._dropout_validator = DropoutValidator()

    def validate_scenario(self, scenario: Scenario) -> ValidationResult:
        """
        Validate entire scenario.

        Args:
            scenario: Scenario to validate

        Returns:
            ValidationResult with all issues

        Requirements: TSE-FUNC-040
        """
        issues = []

        # Validate scenario metadata
        issues.extend(self._validate_scenario_metadata(scenario))

        # Validate Own Ship
        if hasattr(scenario, 'own_ship') and scenario.own_ship:
            issues.extend(self._validate_own_ship(scenario.own_ship, scenario))
        else:
            issues.append(ValidationIssue(
                severity="error",
                component="Scenario",
                message="Scenario must have an Own Ship defined"
            ))

        # Validate targets
        if hasattr(scenario, 'targets') and scenario.targets:
            for i, target in enumerate(scenario.targets):
                issues.extend(self._validate_target(target, scenario, i))

            # Check for duplicate target IDs
            issues.extend(self._validate_unique_target_ids(scenario.targets))
        else:
            issues.append(ValidationIssue(
                severity="warning",
                component="Scenario",
                message="Scenario has no targets defined"
            ))

        return ValidationResult(is_valid=True, issues=issues)

    def validate_target(self, target: Target, scenario: Optional[Scenario] = None) -> ValidationResult:
        """
        Validate individual target.

        Args:
            target: Target to validate
            scenario: Parent scenario (for context-aware validation)

        Returns:
            ValidationResult for target
        """
        issues = self._validate_target(target, scenario)
        return ValidationResult(is_valid=True, issues=issues)

    def validate_own_ship(self, own_ship: OwnShip, scenario: Optional[Scenario] = None) -> ValidationResult:
        """
        Validate Own Ship.

        Args:
            own_ship: Own Ship to validate
            scenario: Parent scenario (for context-aware validation)

        Returns:
            ValidationResult for Own Ship
        """
        issues = self._validate_own_ship(own_ship, scenario)
        return ValidationResult(is_valid=True, issues=issues)

    def _validate_scenario_metadata(self, scenario: Scenario) -> List[ValidationIssue]:
        """Validate scenario metadata."""
        issues = []

        # Validate ID
        if not scenario.scenario_id or not scenario.scenario_id.strip():
            issues.append(ValidationIssue(
                severity="error",
                component="Scenario",
                message="Scenario ID is required"
            ))

        # Validate title
        if not scenario.title or not scenario.title.strip():
            issues.append(ValidationIssue(
                severity="error",
                component="Scenario",
                message="Scenario title is required"
            ))

        # Validate duration
        if scenario.duration_sec < 10:
            issues.append(ValidationIssue(
                severity="error",
                component="Scenario",
                message=f"Duration must be at least 10 seconds (got {scenario.duration_sec})"
            ))
        elif scenario.duration_sec > 86400:
            issues.append(ValidationIssue(
                severity="warning",
                component="Scenario",
                message=f"Duration is very long ({scenario.duration_sec} seconds = {scenario.duration_sec/3600:.1f} hours)"
            ))

        return issues

    def _validate_own_ship(self, own_ship: OwnShip, scenario: Optional[Scenario]) -> List[ValidationIssue]:
        """Validate Own Ship."""
        issues = []

        # Validate position
        if not own_ship.position:
            issues.append(ValidationIssue(
                severity="error",
                component="Own Ship",
                message="Own Ship must have a position defined"
            ))
        else:
            # Validate latitude
            if not -90 <= own_ship.position.latitude <= 90:
                issues.append(ValidationIssue(
                    severity="error",
                    component="Own Ship",
                    message=f"Invalid latitude: {own_ship.position.latitude} (must be -90 to 90)"
                ))

            # Validate longitude
            if not -180 <= own_ship.position.longitude <= 180:
                issues.append(ValidationIssue(
                    severity="error",
                    component="Own Ship",
                    message=f"Invalid longitude: {own_ship.position.longitude} (must be -180 to 180)"
                ))

        # Validate speed
        if own_ship.speed_knots < 0:
            issues.append(ValidationIssue(
                severity="error",
                component="Own Ship",
                message=f"Speed cannot be negative (got {own_ship.speed_knots} kts)"
            ))
        elif own_ship.speed_knots > 40:
            issues.append(ValidationIssue(
                severity="warning",
                component="Own Ship",
                message=f"Speed is very high ({own_ship.speed_knots} kts)"
            ))

        # Validate course
        if not 0 <= own_ship.course_deg < 360:
            issues.append(ValidationIssue(
                severity="error",
                component="Own Ship",
                message=f"Course must be 0-360 degrees (got {own_ship.course_deg})"
            ))

        # Validate sensors
        if hasattr(own_ship, 'sensors') and own_ship.sensors:
            # Check if all sensors are disabled
            if not any([
                own_ship.sensors.ais_enabled,
                own_ship.sensors.radar_a_enabled,
                own_ship.sensors.radar_b_enabled,
                own_ship.sensors.eo_enabled
            ]):
                issues.append(ValidationIssue(
                    severity="warning",
                    component="Own Ship",
                    message="All sensors are disabled"
                ))

        return issues

    def _validate_target(self, target: Target, scenario: Optional[Scenario], index: int = 0) -> List[ValidationIssue]:
        """Validate individual target."""
        issues = []
        component_name = f"Target {index + 1} ({target.target_id})"

        # Validate ID
        if not target.target_id or not target.target_id.strip():
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message="Target ID is required"
            ))

        # Validate name
        if not target.name or not target.name.strip():
            issues.append(ValidationIssue(
                severity="warning",
                component=component_name,
                message="Target name is empty"
            ))

        # Validate relative positioning
        if target.relative_range_m < 40:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Range too small: {target.relative_range_m}m (minimum 40m)"
            ))
        elif target.relative_range_m > 20000:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Range too large: {target.relative_range_m}m (maximum 20,000m)"
            ))

        if not 0 <= target.relative_bearing_deg < 360:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Invalid bearing: {target.relative_bearing_deg}° (must be 0-360)"
            ))

        # Validate speed
        if target.speed_knots < 0:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Speed cannot be negative (got {target.speed_knots} kts)"
            ))
        elif target.speed_knots > 40:
            issues.append(ValidationIssue(
                severity="warning",
                component=component_name,
                message=f"Speed is very high ({target.speed_knots} kts)"
            ))

        # Validate course
        if not 0 <= target.course_deg < 360:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Course must be 0-360 degrees (got {target.course_deg})"
            ))

        # Validate MMSI
        if not 100000000 <= target.mmsi <= 999999999:
            issues.append(ValidationIssue(
                severity="error",
                component=component_name,
                message=f"Invalid MMSI: {target.mmsi} (must be 9 digits)"
            ))

        # Validate route if present
        if hasattr(target, 'route') and target.route:
            route_issues = self._route_validator.validate_route(target.route, scenario)
            for issue in route_issues:
                issues.append(ValidationIssue(
                    severity=issue.severity,
                    component=f"{component_name} - Route",
                    message=issue.message,
                    field=issue.field
                ))

        # Validate dropouts if present
        if hasattr(target, 'dropouts') and target.dropouts and scenario:
            dropout_issues = self._dropout_validator.validate_dropouts(
                target.dropouts,
                scenario.duration_sec
            )
            for issue in dropout_issues:
                issues.append(ValidationIssue(
                    severity=issue.severity,
                    component=f"{component_name} - Dropouts",
                    message=issue.message,
                    field=issue.field
                ))

        return issues

    def _validate_unique_target_ids(self, targets: List[Target]) -> List[ValidationIssue]:
        """Validate that all target IDs are unique."""
        issues = []
        seen_ids = {}

        for i, target in enumerate(targets):
            target_id = target.target_id

            if target_id in seen_ids:
                issues.append(ValidationIssue(
                    severity="error",
                    component="Scenario",
                    message=f"Duplicate target ID '{target_id}' found at positions {seen_ids[target_id]} and {i + 1}"
                ))
            else:
                seen_ids[target_id] = i + 1

        return issues

    def quick_validate(self, scenario: Scenario) -> bool:
        """
        Quick validation check (errors only, no warnings).

        Args:
            scenario: Scenario to validate

        Returns:
            True if no errors, False if errors found
        """
        result = self.validate_scenario(scenario)
        return result.is_valid

    def get_validation_summary(self, scenario: Scenario) -> str:
        """
        Get human-readable validation summary.

        Args:
            scenario: Scenario to validate

        Returns:
            Summary string
        """
        result = self.validate_scenario(scenario)
        return result.get_summary()
