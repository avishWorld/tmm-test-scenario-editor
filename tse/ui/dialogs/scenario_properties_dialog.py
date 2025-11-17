"""
Scenario Properties Dialog.

Allows users to edit scenario metadata and basic properties.

Requirements:
- TSE-FUNC-001: Scenario ID (alphanumeric, max 64 chars)
- TSE-FUNC-002: Scenario title (UTF-8, max 128 chars)
- TSE-FUNC-003: Scenario description (UTF-8, max 512 chars)
- TSE-FUNC-004: Simulation duration (10-86400 seconds)
- TSE-FUNC-005: Coordinate system (WGS84)
- TSE-UI-042: Field validation with visual feedback
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QDialogButtonBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from ...models import Scenario


class ValidatedLineEdit(QLineEdit):
    """Line edit with validation feedback."""

    def __init__(self, max_length: int = None, parent=None):
        super().__init__(parent)
        self.max_length = max_length
        if max_length:
            self.setMaxLength(max_length)
        self.textChanged.connect(self._on_text_changed)
        self._is_valid = True

    def _on_text_changed(self):
        """Update validation state when text changes."""
        if self.max_length:
            remaining = self.max_length - len(self.text())
            if remaining < 10:
                self.setToolTip(f"{remaining} characters remaining")
            else:
                self.setToolTip("")

    def set_valid(self, valid: bool, message: str = ""):
        """Set validation state with visual feedback (TSE-UI-042)."""
        self._is_valid = valid
        palette = self.palette()

        if not valid:
            # Red border for invalid
            self.setStyleSheet("QLineEdit { border: 2px solid red; }")
            self.setToolTip(message)
        else:
            # Default style for valid
            self.setStyleSheet("")
            if not message:
                self.setToolTip("")
            else:
                self.setToolTip(message)

    def is_valid(self) -> bool:
        """Check if field is valid."""
        return self._is_valid


class ValidatedTextEdit(QTextEdit):
    """Text edit with validation feedback."""

    def __init__(self, max_length: int = None, parent=None):
        super().__init__(parent)
        self.max_length = max_length
        self.textChanged.connect(self._on_text_changed)
        self._is_valid = True

    def _on_text_changed(self):
        """Update character count when text changes."""
        if self.max_length:
            current = len(self.toPlainText())
            remaining = self.max_length - current

            if current > self.max_length:
                # Truncate to max length
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                text = self.toPlainText()[:self.max_length]
                self.setPlainText(text)
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)

            if remaining < 50:
                self.setToolTip(f"{remaining} characters remaining")
            else:
                self.setToolTip("")

    def set_valid(self, valid: bool, message: str = ""):
        """Set validation state with visual feedback (TSE-UI-042)."""
        self._is_valid = valid

        if not valid:
            self.setStyleSheet("QTextEdit { border: 2px solid red; }")
            self.setToolTip(message)
        else:
            self.setStyleSheet("")
            if not message:
                self.setToolTip("")
            else:
                self.setToolTip(message)

    def is_valid(self) -> bool:
        """Check if field is valid."""
        return self._is_valid


class ScenarioPropertiesDialog(QDialog):
    """
    Dialog for editing scenario properties.

    Requirements: TSE-FUNC-001 to TSE-FUNC-005, TSE-UI-042
    """

    def __init__(self, scenario: Scenario = None, parent=None):
        """
        Initialize the dialog.

        Args:
            scenario: Scenario to edit (None to create new)
            parent: Parent widget
        """
        super().__init__(parent)
        self.scenario = scenario
        self._init_ui()

        if scenario:
            self._load_from_scenario()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Scenario Properties")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Basic Properties Group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)

        # Scenario ID (TSE-FUNC-001)
        self.id_edit = ValidatedLineEdit(max_length=64)
        self.id_edit.setPlaceholderText("e.g., SCENARIO_001")
        basic_layout.addRow("Scenario ID*:", self.id_edit)

        # Title (TSE-FUNC-002)
        self.title_edit = ValidatedLineEdit(max_length=128)
        self.title_edit.setPlaceholderText("e.g., Basic Fusion Test")
        basic_layout.addRow("Title*:", self.title_edit)

        # Description (TSE-FUNC-003)
        self.description_edit = ValidatedTextEdit(max_length=512)
        self.description_edit.setPlaceholderText("Enter scenario description...")
        self.description_edit.setMaximumHeight(100)
        basic_layout.addRow("Description:", self.description_edit)

        layout.addWidget(basic_group)

        # Simulation Parameters Group
        sim_group = QGroupBox("Simulation Parameters")
        sim_layout = QFormLayout(sim_group)

        # Duration (TSE-FUNC-004)
        duration_layout = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 86400)
        self.duration_spin.setValue(300)
        self.duration_spin.setSuffix(" seconds")
        self.duration_spin.setToolTip("Simulation duration: 10s to 24 hours (86400s)")
        duration_layout.addWidget(self.duration_spin)

        # Duration helper label
        self.duration_label = QLabel()
        self.duration_spin.valueChanged.connect(self._update_duration_label)
        self._update_duration_label(self.duration_spin.value())
        duration_layout.addWidget(self.duration_label)
        duration_layout.addStretch()

        sim_layout.addRow("Duration*:", duration_layout)

        # Coordinate System (TSE-FUNC-005)
        self.coord_system_combo = QComboBox()
        self.coord_system_combo.addItem("WGS84 (Geodetic)", "geodetic")
        self.coord_system_combo.setEnabled(False)  # Always WGS84
        self.coord_system_combo.setToolTip("Coordinate system (always WGS84)")
        sim_layout.addRow("Coordinate System:", self.coord_system_combo)

        layout.addWidget(sim_group)

        # Info label
        info_label = QLabel("* Required fields")
        info_label.setStyleSheet("QLabel { color: gray; font-style: italic; }")
        layout.addWidget(info_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_duration_label(self, seconds: int):
        """Update duration helper label."""
        minutes = seconds // 60
        hours = minutes // 60

        if hours > 0:
            self.duration_label.setText(f"({hours}h {minutes % 60}m)")
        elif minutes > 0:
            self.duration_label.setText(f"({minutes}m)")
        else:
            self.duration_label.setText("")

    def _load_from_scenario(self):
        """Load values from scenario."""
        if self.scenario:
            self.id_edit.setText(self.scenario.scenario_id)
            self.title_edit.setText(self.scenario.title)
            self.description_edit.setPlainText(self.scenario.description)
            self.duration_spin.setValue(self.scenario.duration_sec)

    def _validate(self) -> bool:
        """
        Validate all fields.

        Returns:
            True if all fields are valid

        Requirements: TSE-UI-042 (visual feedback)
        """
        is_valid = True

        # Validate Scenario ID (TSE-FUNC-001)
        scenario_id = self.id_edit.text().strip()
        if not scenario_id:
            self.id_edit.set_valid(False, "Scenario ID is required")
            is_valid = False
        elif len(scenario_id) > 64:
            self.id_edit.set_valid(False, "Scenario ID too long (max 64 characters)")
            is_valid = False
        else:
            self.id_edit.set_valid(True)

        # Validate Title (TSE-FUNC-002)
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.set_valid(False, "Title is required")
            is_valid = False
        elif len(title) > 128:
            self.title_edit.set_valid(False, "Title too long (max 128 characters)")
            is_valid = False
        else:
            self.title_edit.set_valid(True)

        # Validate Description (TSE-FUNC-003)
        description = self.description_edit.toPlainText().strip()
        if len(description) > 512:
            self.description_edit.set_valid(False, "Description too long (max 512 characters)")
            is_valid = False
        else:
            self.description_edit.set_valid(True)

        # Duration is automatically validated by QSpinBox range

        return is_valid

    def _accept(self):
        """Accept the dialog if validation passes."""
        if self._validate():
            self.accept()

    def get_scenario(self) -> Scenario:
        """
        Get the scenario with updated values.

        Returns:
            Scenario object with values from dialog
        """
        if self.scenario:
            # Update existing scenario
            self.scenario.scenario_id = self.id_edit.text().strip()
            self.scenario.title = self.title_edit.text().strip()
            self.scenario.description = self.description_edit.toPlainText().strip()
            self.scenario.duration_sec = self.duration_spin.value()
            return self.scenario
        else:
            # Create new scenario
            return Scenario(
                scenario_id=self.id_edit.text().strip(),
                title=self.title_edit.text().strip(),
                description=self.description_edit.toPlainText().strip(),
                duration_sec=self.duration_spin.value(),
                coordinate_system="geodetic"
            )
