"""
Scenario properties dialog for editing scenario metadata.

Requirements:
- TSE-FUNC-010: Scenario configuration
- TSE-FUNC-011: Scenario metadata editing
- TSE-UI-041: OK/Cancel/Apply buttons
- TSE-UI-042: Field validation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QPushButton,
    QLabel, QGroupBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from typing import Optional

from tse.models.scenario import Scenario


class ScenarioPropertiesDialog(QDialog):
    """
    Dialog for editing scenario properties.

    Features:
    - Scenario identification (ID, title)
    - Description text area
    - Duration configuration
    - Coordinate system selection
    - Validation

    Requirements: TSE-FUNC-010, TSE-FUNC-011
    """

    def __init__(self, scenario: Optional[Scenario] = None, parent=None):
        """
        Initialize scenario properties dialog.

        Args:
            scenario: Existing scenario to edit (None for new)
            parent: Parent widget
        """
        super().__init__(parent)

        self._scenario = scenario

        # Initialize UI
        self._init_ui()

        # Populate if editing
        if self._scenario:
            self._populate_fields()

    def _init_ui(self):
        """Initialize user interface."""
        title = "Edit Scenario Properties" if self._scenario else "New Scenario"
        self.setWindowTitle(title)
        self.setMinimumWidth(600)

        # Main layout
        layout = QVBoxLayout()

        # Form sections
        layout.addWidget(self._create_identification_group())
        layout.addWidget(self._create_description_group())
        layout.addWidget(self._create_duration_group())
        layout.addWidget(self._create_coordinate_system_group())

        # Validation message
        self._validation_label = QLabel()
        self._validation_label.setWordWrap(True)
        self._validation_label.setStyleSheet("color: red; font-weight: bold;")
        self._validation_label.hide()
        layout.addWidget(self._validation_label)

        # Buttons
        layout.addWidget(self._create_buttons())

        self.setLayout(layout)

    def _create_identification_group(self) -> QGroupBox:
        """Create identification input group."""
        group = QGroupBox("Identification")
        form = QFormLayout()

        # Scenario ID
        self._id_edit = QLineEdit()
        default_id = "SCN001" if not self._scenario else self._scenario.scenario_id
        self._id_edit.setText(default_id)
        self._id_edit.setMaxLength(64)
        form.addRow("Scenario ID:", self._id_edit)

        # Title
        self._title_edit = QLineEdit()
        default_title = "New Scenario" if not self._scenario else self._scenario.title
        self._title_edit.setText(default_title)
        self._title_edit.setMaxLength(256)
        form.addRow("Title:", self._title_edit)

        group.setLayout(form)
        return group

    def _create_description_group(self) -> QGroupBox:
        """Create description input group."""
        group = QGroupBox("Description")
        layout = QVBoxLayout()

        # Description text area
        self._description_edit = QTextEdit()
        default_description = "Test scenario for TMM" if not self._scenario else self._scenario.description
        self._description_edit.setPlainText(default_description)
        self._description_edit.setMaximumHeight(100)
        layout.addWidget(self._description_edit)

        group.setLayout(layout)
        return group

    def _create_duration_group(self) -> QGroupBox:
        """Create duration configuration group."""
        group = QGroupBox("Duration")
        form = QFormLayout()

        # Duration in seconds
        duration_layout = QHBoxLayout()

        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(10, 86400)  # 10 seconds to 24 hours
        self._duration_spin.setValue(300 if not self._scenario else self._scenario.duration_sec)
        self._duration_spin.setSuffix(" sec")
        self._duration_spin.valueChanged.connect(self._on_duration_changed)
        duration_layout.addWidget(self._duration_spin)

        # Minutes helper
        self._minutes_label = QLabel()
        self._update_minutes_label()
        duration_layout.addWidget(self._minutes_label)

        duration_layout.addStretch()

        form.addRow("Duration:", duration_layout)

        # Common durations
        shortcuts_layout = QHBoxLayout()
        shortcuts_label = QLabel("Quick set:")
        shortcuts_layout.addWidget(shortcuts_label)

        for minutes in [5, 10, 15, 30, 60]:
            btn = QPushButton(f"{minutes} min")
            btn.clicked.connect(lambda checked, m=minutes: self._set_duration_minutes(m))
            shortcuts_layout.addWidget(btn)

        shortcuts_layout.addStretch()
        form.addRow("", shortcuts_layout)

        group.setLayout(form)
        return group

    def _create_coordinate_system_group(self) -> QGroupBox:
        """Create coordinate system selection group."""
        group = QGroupBox("Coordinate System")
        form = QFormLayout()

        # Coordinate system combo
        self._coordinate_system_combo = QComboBox()
        self._coordinate_system_combo.addItem("Geodetic (WGS84)", "geodetic")
        self._coordinate_system_combo.addItem("Cartesian (Local)", "cartesian")

        # Set current value
        if self._scenario:
            coord_system = getattr(self._scenario, 'coordinate_system', 'geodetic')
            index = 0 if coord_system == "geodetic" else 1
            self._coordinate_system_combo.setCurrentIndex(index)

        form.addRow("Coordinate System:", self._coordinate_system_combo)

        # Help text
        help_label = QLabel("Geodetic: Geographic coordinates (lat/lon)\nCartesian: Local XY coordinates")
        help_label.setStyleSheet("color: gray; font-size: 9pt;")
        form.addRow("", help_label)

        group.setLayout(form)
        return group

    def _create_buttons(self) -> QWidget:
        """Create dialog buttons."""
        widget = QWidget()
        layout = QHBoxLayout()

        # OK button
        self._ok_button = QPushButton("OK")
        self._ok_button.clicked.connect(self._on_ok)
        self._ok_button.setDefault(True)
        layout.addWidget(self._ok_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        # Apply button (for editing)
        if self._scenario:
            apply_button = QPushButton("Apply")
            apply_button.clicked.connect(self._on_apply)
            layout.addWidget(apply_button)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _populate_fields(self):
        """Populate fields from existing scenario."""
        if not self._scenario:
            return

        self._id_edit.setText(self._scenario.scenario_id)
        self._title_edit.setText(self._scenario.title)
        self._description_edit.setPlainText(self._scenario.description)
        self._duration_spin.setValue(self._scenario.duration_sec)

        # Set coordinate system
        coord_system = getattr(self._scenario, 'coordinate_system', 'geodetic')
        index = 0 if coord_system == "geodetic" else 1
        self._coordinate_system_combo.setCurrentIndex(index)

    def _on_duration_changed(self):
        """Handle duration change."""
        self._update_minutes_label()

    def _update_minutes_label(self):
        """Update minutes helper label."""
        seconds = self._duration_spin.value()
        minutes = seconds / 60.0

        if seconds % 60 == 0:
            self._minutes_label.setText(f"({int(minutes)} min)")
        else:
            self._minutes_label.setText(f"({minutes:.1f} min)")

    def _set_duration_minutes(self, minutes: int):
        """Set duration in minutes."""
        self._duration_spin.setValue(minutes * 60)

    def _validate_inputs(self) -> bool:
        """Validate input fields."""
        self._validation_label.hide()
        errors = []

        # Validate ID
        if not self._id_edit.text().strip():
            errors.append("Scenario ID is required")

        # Validate title
        if not self._title_edit.text().strip():
            errors.append("Title is required")

        # Validate duration
        duration = self._duration_spin.value()
        if duration < 10:
            errors.append("Duration must be at least 10 seconds")

        # Show errors
        if errors:
            self._validation_label.setText("\n".join(errors))
            self._validation_label.show()
            return False

        return True

    def _on_ok(self):
        """Handle OK button."""
        if self._validate_inputs():
            self.accept()

    def _on_apply(self):
        """Handle Apply button."""
        if self._validate_inputs() and self._scenario:
            self._update_scenario(self._scenario)
            QMessageBox.information(
                self,
                "Applied",
                "Scenario properties have been updated"
            )

    def _update_scenario(self, scenario: Scenario):
        """Update scenario from form fields."""
        scenario.scenario_id = self._id_edit.text().strip()
        scenario.title = self._title_edit.text().strip()
        scenario.description = self._description_edit.toPlainText().strip()
        scenario.duration_sec = self._duration_spin.value()
        scenario.coordinate_system = self._coordinate_system_combo.currentData()

    def get_scenario_properties(self) -> dict:
        """
        Get scenario properties from dialog inputs.

        Returns:
            Dictionary with scenario properties
        """
        return {
            'scenario_id': self._id_edit.text().strip(),
            'title': self._title_edit.text().strip(),
            'description': self._description_edit.toPlainText().strip(),
            'duration_sec': self._duration_spin.value(),
            'coordinate_system': self._coordinate_system_combo.currentData()
        }

    @staticmethod
    def create_scenario(parent=None) -> Optional[dict]:
        """
        Show dialog to create a new scenario.

        Args:
            parent: Parent widget

        Returns:
            Dictionary with scenario properties or None if cancelled
        """
        dialog = ScenarioPropertiesDialog(None, parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_scenario_properties()

        return None

    @staticmethod
    def edit_scenario(scenario: Scenario, parent=None) -> bool:
        """
        Show dialog to edit an existing scenario.

        Args:
            scenario: Scenario to edit
            parent: Parent widget

        Returns:
            True if changes accepted, False if cancelled
        """
        dialog = ScenarioPropertiesDialog(scenario, parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog._update_scenario(scenario)
            return True

        return False
