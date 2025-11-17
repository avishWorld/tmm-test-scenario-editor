"""
Route and waypoint validation.

Requirements:
- TSE-FUNC-041: WP1 validation (time=0, initial position)
- TSE-FUNC-044: Waypoint timing validation
- TSE-FUNC-105: Route reachability validation
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from tse.models.waypoint import Waypoint
from tse.models.target import Target
from tse.logic.route_calculator import RouteCalculator


@dataclass
class ValidationIssue:
    """
    Represents a validation issue.

    Attributes:
        severity: 'error', 'warning', or 'info'
        code: Unique issue code
        message: Human-readable message
        waypoint_index: Index of problematic waypoint (if applicable)
    """
    severity: str  # 'error', 'warning', 'info'
    code: str
    message: str
    waypoint_index: Optional[int] = None


class RouteValidator:
    """
    Validates routes and waypoints against requirements.

    Requirements: TSE-FUNC-041, TSE-FUNC-044, TSE-FUNC-105
    """

    # Maximum vessel speed (knots)
    MAX_SPEED_KNOTS = 40.0

    # Minimum time between waypoints (seconds)
    MIN_TIME_DELTA = 1.0

    @staticmethod
    def validate_route(waypoints: List[Waypoint], target: Optional[Target] = None) -> List[ValidationIssue]:
        """
        Validate a complete route.

        Args:
            waypoints: List of waypoints to validate
            target: Optional target object for additional validation

        Returns:
            List of validation issues (empty if valid)

        Requirements: TSE-FUNC-041, TSE-FUNC-044, TSE-FUNC-105
        """
        issues = []

        if not waypoints:
            return issues  # Empty route is valid

        # Validate WP1 special requirements
        issues.extend(RouteValidator._validate_wp1(waypoints[0]))

        # Validate waypoint ordering
        issues.extend(RouteValidator._validate_waypoint_order(waypoints))

        # Validate timing
        issues.extend(RouteValidator._validate_timing(waypoints))

        # Validate reachability
        issues.extend(RouteValidator._validate_reachability(waypoints))

        # Validate positions
        issues.extend(RouteValidator._validate_positions(waypoints))

        # Validate speeds
        issues.extend(RouteValidator._validate_speeds(waypoints, target))

        return issues

    @staticmethod
    def _validate_wp1(wp1: Waypoint) -> List[ValidationIssue]:
        """
        Validate WP1 special requirements.

        Requirements: TSE-FUNC-041
        - WP1 must have time = 0
        - WP1 represents initial position
        """
        issues = []

        if wp1.time_sec != 0.0:
            issues.append(ValidationIssue(
                severity='error',
                code='WP1_TIME_NOT_ZERO',
                message=f'WP1 time must be 0 seconds (found: {wp1.time_sec}s)',
                waypoint_index=0
            ))

        if not wp1.position:
            issues.append(ValidationIssue(
                severity='error',
                code='WP1_NO_POSITION',
                message='WP1 must have a valid position',
                waypoint_index=0
            ))

        return issues

    @staticmethod
    def _validate_waypoint_order(waypoints: List[Waypoint]) -> List[ValidationIssue]:
        """
        Validate that waypoints are ordered by time.

        Requirements: TSE-FUNC-044
        """
        issues = []

        for i in range(len(waypoints) - 1):
            if waypoints[i].time_sec >= waypoints[i + 1].time_sec:
                issues.append(ValidationIssue(
                    severity='error',
                    code='WAYPOINT_TIME_ORDER',
                    message=f'WP{i+1} time ({waypoints[i].time_sec}s) must be less than WP{i+2} time ({waypoints[i+1].time_sec}s)',
                    waypoint_index=i + 1
                ))

        return issues

    @staticmethod
    def _validate_timing(waypoints: List[Waypoint]) -> List[ValidationIssue]:
        """
        Validate waypoint timing constraints.

        Requirements: TSE-FUNC-044
        """
        issues = []

        for i in range(len(waypoints) - 1):
            time_delta = waypoints[i + 1].time_sec - waypoints[i].time_sec

            if time_delta < RouteValidator.MIN_TIME_DELTA:
                issues.append(ValidationIssue(
                    severity='warning',
                    code='WAYPOINT_TIME_TOO_CLOSE',
                    message=f'WP{i+1} to WP{i+2}: Time delta ({time_delta}s) is very short (< {RouteValidator.MIN_TIME_DELTA}s)',
                    waypoint_index=i + 1
                ))

        return issues

    @staticmethod
    def _validate_reachability(waypoints: List[Waypoint]) -> List[ValidationIssue]:
        """
        Validate that route is physically reachable.

        Requirements: TSE-FUNC-105
        """
        issues = []

        is_reachable, unreachable_idx = RouteCalculator.is_route_reachable(
            waypoints,
            RouteValidator.MAX_SPEED_KNOTS
        )

        if not is_reachable and unreachable_idx is not None:
            required_speed = RouteCalculator.calculate_required_speed(
                waypoints[unreachable_idx - 1],
                waypoints[unreachable_idx]
            )

            issues.append(ValidationIssue(
                severity='error',
                code='ROUTE_UNREACHABLE',
                message=f'WP{unreachable_idx} to WP{unreachable_idx+1}: Required speed ({required_speed:.1f} kts) exceeds maximum ({RouteValidator.MAX_SPEED_KNOTS} kts)',
                waypoint_index=unreachable_idx
            ))

        return issues

    @staticmethod
    def _validate_positions(waypoints: List[Waypoint]) -> List[ValidationIssue]:
        """Validate that all waypoints have valid positions."""
        issues = []

        for i, wp in enumerate(waypoints):
            if not wp.position:
                issues.append(ValidationIssue(
                    severity='error',
                    code='WAYPOINT_NO_POSITION',
                    message=f'WP{i+1} has no position',
                    waypoint_index=i
                ))
            else:
                # Validate latitude range
                if not -90.0 <= wp.position.latitude <= 90.0:
                    issues.append(ValidationIssue(
                        severity='error',
                        code='INVALID_LATITUDE',
                        message=f'WP{i+1} latitude ({wp.position.latitude}°) out of range [-90, 90]',
                        waypoint_index=i
                    ))

                # Validate longitude range
                if not -180.0 <= wp.position.longitude <= 180.0:
                    issues.append(ValidationIssue(
                        severity='error',
                        code='INVALID_LONGITUDE',
                        message=f'WP{i+1} longitude ({wp.position.longitude}°) out of range [-180, 180]',
                        waypoint_index=i
                    ))

        return issues

    @staticmethod
    def _validate_speeds(waypoints: List[Waypoint], target: Optional[Target] = None) -> List[ValidationIssue]:
        """Validate waypoint speeds."""
        issues = []

        for i, wp in enumerate(waypoints):
            if not 0.0 <= wp.speed_knots <= RouteValidator.MAX_SPEED_KNOTS:
                issues.append(ValidationIssue(
                    severity='error',
                    code='INVALID_SPEED',
                    message=f'WP{i+1} speed ({wp.speed_knots} kts) out of range [0, {RouteValidator.MAX_SPEED_KNOTS}]',
                    waypoint_index=i
                ))

            if not 0.0 <= wp.course_deg < 360.0:
                issues.append(ValidationIssue(
                    severity='error',
                    code='INVALID_COURSE',
                    message=f'WP{i+1} course ({wp.course_deg}°) out of range [0, 360)',
                    waypoint_index=i
                ))

        return issues

    @staticmethod
    def has_errors(issues: List[ValidationIssue]) -> bool:
        """
        Check if validation issues contain any errors.

        Args:
            issues: List of validation issues

        Returns:
            True if any error-severity issues exist
        """
        return any(issue.severity == 'error' for issue in issues)

    @staticmethod
    def has_warnings(issues: List[ValidationIssue]) -> bool:
        """
        Check if validation issues contain any warnings.

        Args:
            issues: List of validation issues

        Returns:
            True if any warning-severity issues exist
        """
        return any(issue.severity == 'warning' for issue in issues)

    @staticmethod
    def format_issues(issues: List[ValidationIssue]) -> str:
        """
        Format validation issues for display.

        Args:
            issues: List of validation issues

        Returns:
            Formatted string
        """
        if not issues:
            return "✓ Route is valid"

        lines = []
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']

        if errors:
            lines.append(f"❌ {len(errors)} Error(s):")
            for issue in errors:
                lines.append(f"  • {issue.message}")

        if warnings:
            lines.append(f"⚠️  {len(warnings)} Warning(s):")
            for issue in warnings:
                lines.append(f"  • {issue.message}")

        return "\n".join(lines)
