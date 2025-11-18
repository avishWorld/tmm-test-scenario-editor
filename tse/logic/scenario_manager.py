"""
Scenario manager for handling scenario lifecycle.

Requirements:
- TSE-FUNC-110: New scenario creation
- TSE-FUNC-111: Save project
- TSE-FUNC-112: Load project
- TSE-FUNC-113: Save As
- TSE-FUNC-114: Unsaved changes handling
- TSE-FUNC-115: Recent files list
"""

from pathlib import Path
from typing import Optional, List
from PyQt6.QtCore import QSettings

from tse.models.scenario import Scenario
from tse.models.own_ship import OwnShip
from tse.models.geo import GeoPosition
from tse.io.project_file import ProjectFile


class ScenarioManager:
    """
    Manages scenario lifecycle: New, Open, Save, Recent Files.

    Requirements: TSE-FUNC-110 to TSE-FUNC-115
    """

    # Maximum number of recent files to remember
    MAX_RECENT_FILES = 10

    def __init__(self):
        """Initialize scenario manager."""
        self._current_scenario: Optional[Scenario] = None
        self._current_filepath: Optional[str] = None
        self._modified = False

        # Settings for recent files
        self._settings = QSettings('TMM', 'TestScenarioEditor')

    def create_new_scenario(self, scenario_id: str = "SCN001", title: str = "New Scenario") -> Scenario:
        """
        Create a new empty scenario.

        Args:
            scenario_id: Scenario ID
            title: Scenario title

        Returns:
            New Scenario object

        Requirements: TSE-FUNC-110
        """
        # Create default Own Ship at Haifa coordinates
        own_ship = OwnShip(
            position=GeoPosition(latitude=32.08, longitude=34.78),
            speed_knots=0.0,
            course_deg=0.0
        )

        # Create scenario
        scenario = Scenario(
            scenario_id=scenario_id,
            title=title,
            description="Test scenario for TMM",
            duration_sec=300  # 5 minutes default
        )

        scenario.own_ship = own_ship
        scenario.targets = []

        # Set as current scenario
        self._current_scenario = scenario
        self._current_filepath = None
        self._modified = False

        return scenario

    def save_project(self, filepath: Optional[str] = None) -> bool:
        """
        Save current scenario to file.

        Args:
            filepath: File path (None = use current filepath)

        Returns:
            True if save successful

        Requirements: TSE-FUNC-111
        """
        if not self._current_scenario:
            return False

        # Use current filepath if not specified
        if filepath is None:
            if self._current_filepath is None:
                return False  # Need to use Save As
            filepath = self._current_filepath

        # Save
        success = ProjectFile.save_project(self._current_scenario, filepath)

        if success:
            self._current_filepath = filepath
            self._modified = False
            self._add_to_recent_files(filepath)

        return success

    def load_project(self, filepath: str) -> tuple[bool, Optional[str]]:
        """
        Load scenario from file.

        Args:
            filepath: File path to load

        Returns:
            Tuple of (success, error_message)

        Requirements: TSE-FUNC-112
        """
        scenario, error = ProjectFile.load_project(filepath)

        if scenario:
            self._current_scenario = scenario
            self._current_filepath = filepath
            self._modified = False
            self._add_to_recent_files(filepath)
            return (True, None)
        else:
            return (False, error)

    def save_as(self, filepath: str) -> bool:
        """
        Save scenario to new file path.

        Args:
            filepath: New file path

        Returns:
            True if save successful

        Requirements: TSE-FUNC-113
        """
        return self.save_project(filepath)

    def get_current_scenario(self) -> Optional[Scenario]:
        """Get current scenario."""
        return self._current_scenario

    def set_current_scenario(self, scenario: Scenario):
        """
        Set current scenario.

        Args:
            scenario: Scenario to set as current
        """
        self._current_scenario = scenario
        self._modified = True

    def get_current_filepath(self) -> Optional[str]:
        """Get current file path."""
        return self._current_filepath

    def is_modified(self) -> bool:
        """Check if scenario has unsaved changes."""
        return self._modified

    def set_modified(self, modified: bool = True):
        """
        Set modified state.

        Args:
            modified: True if modified, False otherwise

        Requirements: TSE-FUNC-114
        """
        self._modified = modified

    def has_current_scenario(self) -> bool:
        """Check if there is a current scenario."""
        return self._current_scenario is not None

    def get_recent_files(self) -> List[str]:
        """
        Get list of recent files.

        Returns:
            List of recent file paths

        Requirements: TSE-FUNC-115
        """
        recent = self._settings.value("recent_files", [])
        if not isinstance(recent, list):
            recent = []

        # Filter out non-existent files
        recent = [f for f in recent if Path(f).exists()]

        return recent[:self.MAX_RECENT_FILES]

    def _add_to_recent_files(self, filepath: str):
        """
        Add file to recent files list.

        Args:
            filepath: File path to add

        Requirements: TSE-FUNC-115
        """
        recent = self.get_recent_files()

        # Remove if already in list
        if filepath in recent:
            recent.remove(filepath)

        # Add to front
        recent.insert(0, filepath)

        # Limit to MAX_RECENT_FILES
        recent = recent[:self.MAX_RECENT_FILES]

        # Save
        self._settings.setValue("recent_files", recent)

    def clear_recent_files(self):
        """Clear recent files list."""
        self._settings.setValue("recent_files", [])

    def get_scenario_title(self) -> str:
        """Get current scenario title or 'Untitled'."""
        if self._current_scenario and hasattr(self._current_scenario, 'title'):
            return self._current_scenario.title
        return "Untitled"

    def needs_save(self) -> bool:
        """
        Check if scenario needs saving.

        Returns:
            True if has unsaved changes

        Requirements: TSE-FUNC-114
        """
        return self._modified and self._current_scenario is not None
