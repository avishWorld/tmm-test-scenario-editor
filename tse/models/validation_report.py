"""
Validation report data model.

Requirements:
- TSE-FUNC-108: Validation report with severity levels
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class ValidationSeverity(Enum):
    """
    Validation message severity levels.

    Requirements: TSE-FUNC-108
    """
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"


@dataclass
class ValidationMessage:
    """
    Represents a single validation message.

    Attributes:
        severity: Message severity level
        code: Validation rule code (e.g., "TSE-FUNC-100")
        message: Human-readable message
        location: Location of the issue (e.g., "Target T1", "Waypoint 3")
    """
    severity: ValidationSeverity
    code: str
    message: str
    location: str = ""


@dataclass
class ValidationReport:
    """
    Complete validation report for a scenario.

    Attributes:
        messages: List of validation messages
        has_errors: True if any ERROR-level messages exist
        has_warnings: True if any WARNING-level messages exist

    Requirements: TSE-FUNC-108
    """
    messages: List[ValidationMessage] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return any(msg.severity == ValidationSeverity.ERROR for msg in self.messages)

    @property
    def has_warnings(self) -> bool:
        """Check if report contains any warnings."""
        return any(msg.severity == ValidationSeverity.WARNING for msg in self.messages)

    @property
    def error_count(self) -> int:
        """Count of error messages."""
        return sum(1 for msg in self.messages if msg.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning messages."""
        return sum(1 for msg in self.messages if msg.severity == ValidationSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Count of info messages."""
        return sum(1 for msg in self.messages if msg.severity == ValidationSeverity.INFO)

    def add_error(self, code: str, message: str, location: str = ""):
        """Add an error message."""
        self.messages.append(ValidationMessage(ValidationSeverity.ERROR, code, message, location))

    def add_warning(self, code: str, message: str, location: str = ""):
        """Add a warning message."""
        self.messages.append(ValidationMessage(ValidationSeverity.WARNING, code, message, location))

    def add_info(self, code: str, message: str, location: str = ""):
        """Add an info message."""
        self.messages.append(ValidationMessage(ValidationSeverity.INFO, code, message, location))
