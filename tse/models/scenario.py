"""
Scenario data model.

Requirements:
- TSE-FUNC-001: Scenario ID (alphanumeric, max 64 chars)
- TSE-FUNC-002: Scenario title (UTF-8, max 128 chars)
- TSE-FUNC-003: Scenario description (UTF-8, max 512 chars)
- TSE-FUNC-004: Simulation duration (10-86400 seconds)
- TSE-FUNC-005: Coordinate system (WGS84)
"""

from dataclasses import dataclass, field
from typing import List, Optional
# from .own_ship import OwnShip  # Will be imported when implemented
# from .target import Target  # Will be imported when implemented


@dataclass
class Scenario:
    """
    Represents a complete test scenario.

    Attributes:
        scenario_id: Unique scenario identifier (max 64 chars)
        title: Human-readable title (max 128 chars)
        description: Detailed description (max 512 chars)
        duration_sec: Simulation duration in seconds [10, 86400]
        coordinate_system: Coordinate system (always "geodetic" for WGS84)
        own_ship: Own Ship configuration
        targets: List of targets in the scenario
        validation_results: Latest validation report

    Requirements: TSE-FUNC-001 to TSE-FUNC-005
    """
    scenario_id: str = ""
    title: str = ""
    description: str = ""
    duration_sec: int = 60
    coordinate_system: str = "geodetic"
    # own_ship: Optional[OwnShip] = None
    # targets: List[Target] = field(default_factory=list)
    # validation_results: Optional[ValidationReport] = None

    def __post_init__(self):
        """Validate scenario parameters."""
        # TSE-FUNC-001: Scenario ID validation
        if len(self.scenario_id) > 64:
            raise ValueError(f"Scenario ID too long: {len(self.scenario_id)} > 64 chars")

        # TSE-FUNC-002: Title validation
        if len(self.title) > 128:
            raise ValueError(f"Title too long: {len(self.title)} > 128 chars")

        # TSE-FUNC-003: Description validation
        if len(self.description) > 512:
            raise ValueError(f"Description too long: {len(self.description)} > 512 chars")

        # TSE-FUNC-004: Duration validation (10s to 24 hours)
        if not 10 <= self.duration_sec <= 86400:
            raise ValueError(f"Duration {self.duration_sec}s out of range [10, 86400]")

        # TSE-FUNC-005: Coordinate system
        if self.coordinate_system != "geodetic":
            raise ValueError(f"Unsupported coordinate system: {self.coordinate_system}")
