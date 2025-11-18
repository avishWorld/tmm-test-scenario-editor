"""
Dropout validation for sensor dropout schedules.

Requirements:
- TSE-FUNC-053: Dropout time range validation
- TSE-FUNC-054: Sensor type validation
- TSE-FUNC-106: Dropout overlap detection
- TSE-FUNC-143: Dropout within scenario duration
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from tse.models.sensor import SensorDropout, SensorType


@dataclass
class DropoutValidationIssue:
    """
    Represents a dropout validation issue.

    Attributes:
        severity: 'error', 'warning', or 'info'
        code: Unique issue code
        message: Human-readable message
        dropout_index: Index of problematic dropout (if applicable)
    """
    severity: str
    code: str
    message: str
    dropout_index: Optional[int] = None
    related_dropout_index: Optional[int] = None


class DropoutValidator:
    """
    Validates sensor dropout schedules.

    Requirements: TSE-FUNC-053, TSE-FUNC-054, TSE-FUNC-106, TSE-FUNC-143
    """

    # Minimum dropout duration (seconds)
    MIN_DROPOUT_DURATION = 1.0

    @staticmethod
    def validate_dropouts(dropouts: List[SensorDropout],
                         scenario_duration_sec: Optional[float] = None) -> List[DropoutValidationIssue]:
        """
        Validate a list of dropouts.

        Args:
            dropouts: List of SensorDropout objects
            scenario_duration_sec: Scenario duration for range checking

        Returns:
            List of validation issues (empty if valid)

        Requirements: TSE-FUNC-053, TSE-FUNC-054, TSE-FUNC-106, TSE-FUNC-143
        """
        issues = []

        if not dropouts:
            return issues

        # Validate individual dropouts
        for i, dropout in enumerate(dropouts):
            issues.extend(DropoutValidator._validate_dropout(dropout, i, scenario_duration_sec))

        # Validate for overlaps
        issues.extend(DropoutValidator._validate_overlaps(dropouts))

        return issues

    @staticmethod
    def _validate_dropout(dropout: SensorDropout, index: int,
                         scenario_duration_sec: Optional[float] = None) -> List[DropoutValidationIssue]:
        """
        Validate a single dropout.

        Args:
            dropout: Dropout to validate
            index: Dropout index
            scenario_duration_sec: Scenario duration

        Returns:
            List of validation issues
        """
        issues = []

        # Validate sensor type (TSE-FUNC-054)
        if not isinstance(dropout.sensor_type, SensorType):
            issues.append(DropoutValidationIssue(
                severity='error',
                code='INVALID_SENSOR_TYPE',
                message=f'Dropout {index+1}: Invalid sensor type',
                dropout_index=index
            ))

        # Validate time range (TSE-FUNC-053)
        if dropout.start_time_sec < 0:
            issues.append(DropoutValidationIssue(
                severity='error',
                code='NEGATIVE_START_TIME',
                message=f'Dropout {index+1}: Start time ({dropout.start_time_sec}s) cannot be negative',
                dropout_index=index
            ))

        if dropout.end_time_sec <= dropout.start_time_sec:
            issues.append(DropoutValidationIssue(
                severity='error',
                code='INVALID_TIME_RANGE',
                message=f'Dropout {index+1}: End time ({dropout.end_time_sec}s) must be greater than start time ({dropout.start_time_sec}s)',
                dropout_index=index
            ))

        # Validate duration
        duration = dropout.end_time_sec - dropout.start_time_sec
        if duration < DropoutValidator.MIN_DROPOUT_DURATION:
            issues.append(DropoutValidationIssue(
                severity='warning',
                code='SHORT_DROPOUT',
                message=f'Dropout {index+1}: Duration ({duration:.1f}s) is very short (< {DropoutValidator.MIN_DROPOUT_DURATION}s)',
                dropout_index=index
            ))

        # Validate within scenario duration (TSE-FUNC-143)
        if scenario_duration_sec is not None:
            if dropout.start_time_sec > scenario_duration_sec:
                issues.append(DropoutValidationIssue(
                    severity='error',
                    code='DROPOUT_BEYOND_SCENARIO',
                    message=f'Dropout {index+1}: Start time ({dropout.start_time_sec}s) exceeds scenario duration ({scenario_duration_sec}s)',
                    dropout_index=index
                ))

            if dropout.end_time_sec > scenario_duration_sec:
                issues.append(DropoutValidationIssue(
                    severity='warning',
                    code='DROPOUT_EXTENDS_BEYOND_SCENARIO',
                    message=f'Dropout {index+1}: End time ({dropout.end_time_sec}s) extends beyond scenario duration ({scenario_duration_sec}s)',
                    dropout_index=index
                ))

        return issues

    @staticmethod
    def _validate_overlaps(dropouts: List[SensorDropout]) -> List[DropoutValidationIssue]:
        """
        Validate for overlapping dropouts on the same sensor.

        Requirements: TSE-FUNC-106
        """
        issues = []

        # Group dropouts by sensor type
        by_sensor = {}
        for i, dropout in enumerate(dropouts):
            sensor_type = dropout.sensor_type
            if sensor_type not in by_sensor:
                by_sensor[sensor_type] = []
            by_sensor[sensor_type].append((i, dropout))

        # Check for overlaps within each sensor
        for sensor_type, sensor_dropouts in by_sensor.items():
            # Sort by start time
            sorted_dropouts = sorted(sensor_dropouts, key=lambda x: x[1].start_time_sec)

            for i in range(len(sorted_dropouts) - 1):
                idx1, dropout1 = sorted_dropouts[i]
                idx2, dropout2 = sorted_dropouts[i + 1]

                # Check if dropout1 end overlaps with dropout2 start
                if dropout1.end_time_sec > dropout2.start_time_sec:
                    sensor_name = sensor_type.value if hasattr(sensor_type, 'value') else str(sensor_type)

                    issues.append(DropoutValidationIssue(
                        severity='error',
                        code='DROPOUT_OVERLAP',
                        message=f'Dropouts {idx1+1} and {idx2+1} overlap on {sensor_name} '
                               f'({dropout1.end_time_sec}s > {dropout2.start_time_sec}s)',
                        dropout_index=idx1,
                        related_dropout_index=idx2
                    ))

        return issues

    @staticmethod
    def has_errors(issues: List[DropoutValidationIssue]) -> bool:
        """
        Check if validation issues contain any errors.

        Args:
            issues: List of validation issues

        Returns:
            True if any error-severity issues exist
        """
        return any(issue.severity == 'error' for issue in issues)

    @staticmethod
    def has_warnings(issues: List[DropoutValidationIssue]) -> bool:
        """
        Check if validation issues contain any warnings.

        Args:
            issues: List of validation issues

        Returns:
            True if any warning-severity issues exist
        """
        return any(issue.severity == 'warning' for issue in issues)

    @staticmethod
    def format_issues(issues: List[DropoutValidationIssue]) -> str:
        """
        Format validation issues for display.

        Args:
            issues: List of validation issues

        Returns:
            Formatted string
        """
        if not issues:
            return "✓ Dropout schedule is valid"

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

    @staticmethod
    def check_overlap(dropout1: SensorDropout, dropout2: SensorDropout) -> bool:
        """
        Check if two dropouts overlap.

        Args:
            dropout1: First dropout
            dropout2: Second dropout

        Returns:
            True if dropouts overlap on same sensor
        """
        # Must be same sensor
        if dropout1.sensor_type != dropout2.sensor_type:
            return False

        # Check time overlap
        return not (dropout1.end_time_sec <= dropout2.start_time_sec or
                   dropout2.end_time_sec <= dropout1.start_time_sec)

    @staticmethod
    def get_total_dropout_time(dropouts: List[SensorDropout],
                              sensor_type: Optional[SensorType] = None) -> float:
        """
        Calculate total dropout time for a sensor.

        Args:
            dropouts: List of dropouts
            sensor_type: Sensor type to calculate for (None = all sensors)

        Returns:
            Total dropout time in seconds
        """
        total = 0.0

        for dropout in dropouts:
            if sensor_type is None or dropout.sensor_type == sensor_type:
                total += dropout.end_time_sec - dropout.start_time_sec

        return total
