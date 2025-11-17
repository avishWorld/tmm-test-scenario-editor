"""
Waypoint properties dialog for creating and editing waypoints.

Requirements:
- TSE-FUNC-042: Waypoint configuration dialog
- TSE-UI-041: OK/Cancel/Apply buttons
- TSE-UI-042: Field validation with visual feedback
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QPushButton, QLabel,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from typing import Optional

from tse.models.waypoint import Waypoint
from tse.models.geo import GeoPosition


class WaypointPropertiesDialog(QDialog):
    """
    Dialog for editing waypoint properties.

    Features:
    - Input fields for all waypoint properties
    - Real-time validation with visual feedback
    - OK/Cancel/Apply buttons
    - Support for creating new or editing existing waypoints

    Requirements: TSE-FUNC-042, TSE-UI-041, TSE-UI-042
    """

    def __init__(self, waypoint: Optional[Waypoint] = None, waypoint_number: int = 1,
                 is_wp1: bool = False, parent=None):
        """
        Initialize waypoint properties dialog.

        Args:
            waypoint: Existing waypoint to edit (None for new waypoint)
            waypoint_number: Waypoint number for display
            is_wp1: True if this is WP1 (special constraints)
            parent: Parent widget
        """
        super().__init__(parent)

        self._waypoint = waypoint
        self._waypoint_number = waypoint_number
        self._is_wp1 = is_wp1

        # Initialize UI
        self._init_ui()

        # Populate fields if editing existing waypoint
        if self._waypoint:
            self._populate_fields()

        # Apply WP1 constraints
        if self._is_wp1:
            self._apply_wp1_constraints()

    def _init_ui(self):
        """Initialize user interface."""
        title = f"Waypoint {self._waypoint_number} Properties"
        if self._is_wp1:
            title += " (Initial Position)"
        self.setWindowTitle(title)

        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout()

        # Create form sections
        layout.addWidget(self._create_timing_group())
        layout.addWidget(self._create_position_group())
        layout.addWidget(self._create_kinematics_group())

        # Validation message
        self._validation_label = QLabel()
        self._validation_label.setWordWrap(True)
        self._validation_label.setStyleSheet("color: red; font-weight: bold;")
        self._validation_label.hide()
        layout.addWidget(self._validation_label)

        # Buttons
        layout.addWidget(self._create_buttons())

        self.setLayout(layout)

    def _create_timing_group(self) -> QGroupBox:
        """Create timing input group."""
        group = QGroupBox("Timing")
        form = QFormLayout()

        # Time
        self._time_spin = QDoubleSpinBox()
        self._time_spin.setRange(0.0, 86400.0)  # 0 to 24 hours
        self._time_spin.setDecimals(1)
        self._time_spin.setSuffix(" s")
        self._time_spin.setValue(0.0)
        self._time_spin.valueChanged.connect(self._validate_inputs)
        form.addRow("Time:", self._time_spin)

        group.setLayout(form)
        return group

    def _create_position_group(self) -> QGroupBox:
        """Create position input group."""
        group = QGroupBox("Position (WGS84)")
        form = QFormLayout()

        # Latitude
        self._lat_spin = QDoubleSpinBox()
        self._lat_spin.setRange(-90.0, 90.0)
        self._lat_spin.setDecimals(6)
        self._lat_spin.setSuffix(" °N")
        self._lat_spin.setValue(32.08)  # Default: Haifa
        self._lat_spin.valueChanged.connect(self._validate_inputs)
        form.addRow("Latitude:", self._lat_spin)

        # Longitude
        self._lon_spin = QDoubleSpinBox()
        self._lon_spin.setRange(-180.0, 180.0)
        self._lon_spin.setDecimals(6)
        self._lon_spin.setSuffix(" °E")
        self._lon_spin.setValue(34.78)  # Default: Haifa
        self._lon_spin.valueChanged.connect(self._validate_inputs)
        form.addRow("Longitude:", self._lon_spin)

        group.setLayout(form)
        return group

    def _create_kinematics_group(self) -> QGroupBox:
        """Create kinematics input group."""
        group = QGroupBox("Kinematics")
        form = QFormLayout()

        # Speed
        self._speed_spin = QDoubleSpinBox()
        self._speed_spin.setRange(0.0, 40.0)
        self._speed_spin.setDecimals(1)
        self._speed_spin.setSuffix(" kts")
        self._speed_spin.setValue(0.0)
        self._speed_spin.valueChanged.connect(self._validate_inputs)
        form.addRow("Speed:", self._speed_spin)

        # Course
        self._course_spin = QDoubleSpinBox()
        self._course_spin.setRange(0.0, 359.9)
        self._course_spin.setDecimals(1)
        self._course_spin.setSuffix(" °")
        self._course_spin.setValue(0.0)
        self._course_spin.setWrapping(True)  # Wrap around at 360°
        self._course_spin.valueChanged.connect(self._validate_inputs)
        form.addRow("Course:", self._course_spin)

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

        # Apply button (for editing mode)
        if self._waypoint:
            apply_button = QPushButton("Apply")
            apply_button.clicked.connect(self._on_apply)
            layout.addWidget(apply_button)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _populate_fields(self):
        """Populate fields from existing waypoint."""
        if not self._waypoint:
            return

        self._time_spin.setValue(self._waypoint.time_sec)

        if self._waypoint.position:
            self._lat_spin.setValue(self._waypoint.position.latitude)
            self._lon_spin.setValue(self._waypoint.position.longitude)

        self._speed_spin.setValue(self._waypoint.speed_knots)
        self._course_spin.setValue(self._waypoint.course_deg)

    def _apply_wp1_constraints(self):
        """
        Apply WP1 special constraints.

        Requirements: TSE-FUNC-041
        - WP1 time must be 0
        """
        if self._is_wp1:
            self._time_spin.setValue(0.0)
            self._time_spin.setEnabled(False)
            self._time_spin.setToolTip("WP1 time is always 0 seconds")

    def _validate_inputs(self) -> bool:
        """
        Validate input fields.

        Returns:
            True if all inputs are valid

        Requirements: TSE-UI-042
        """
        # Clear previous validation message
        self._validation_label.hide()

        errors = []

        # Validate time
        time_val = self._time_spin.value()
        if self._is_wp1 and time_val != 0.0:
            errors.append("WP1 time must be 0 seconds")

        # Validate latitude
        lat_val = self._lat_spin.value()
        if not -90.0 <= lat_val <= 90.0:
            errors.append("Latitude must be in range [-90, 90]")

        # Validate longitude
        lon_val = self._lon_spin.value()
        if not -180.0 <= lon_val <= 180.0:
            errors.append("Longitude must be in range [-180, 180]")

        # Validate speed
        speed_val = self._speed_spin.value()
        if not 0.0 <= speed_val <= 40.0:
            errors.append("Speed must be in range [0, 40] knots")

        # Validate course
        course_val = self._course_spin.value()
        if not 0.0 <= course_val < 360.0:
            errors.append("Course must be in range [0, 360)")

        # Show validation errors
        if errors:
            self._validation_label.setText("\n".join(errors))
            self._validation_label.show()
            self._ok_button.setEnabled(False)
            return False
        else:
            self._ok_button.setEnabled(True)
            return True

    def _on_ok(self):
        """Handle OK button click."""
        if self._validate_inputs():
            self.accept()

    def _on_apply(self):
        """Handle Apply button click."""
        if self._validate_inputs():
            # Update waypoint object
            if self._waypoint:
                self._update_waypoint(self._waypoint)

    def _update_waypoint(self, waypoint: Waypoint):
        """Update waypoint object from form fields."""
        waypoint.time_sec = self._time_spin.value()
        waypoint.position = GeoPosition(
            latitude=self._lat_spin.value(),
            longitude=self._lon_spin.value()
        )
        waypoint.speed_knots = self._speed_spin.value()
        waypoint.course_deg = self._course_spin.value()

    def get_waypoint(self) -> Waypoint:
        """
        Get waypoint from dialog inputs.

        Returns:
            Waypoint object with values from form
        """
        waypoint = Waypoint(
            time_sec=self._time_spin.value(),
            position=GeoPosition(
                latitude=self._lat_spin.value(),
                longitude=self._lon_spin.value()
            ),
            speed_knots=self._speed_spin.value(),
            course_deg=self._course_spin.value()
        )
        return waypoint

    @staticmethod
    def create_waypoint(waypoint_number: int = 1, is_wp1: bool = False, parent=None) -> Optional[Waypoint]:
        """
        Show dialog to create a new waypoint.

        Args:
            waypoint_number: Waypoint number for display
            is_wp1: True if this is WP1
            parent: Parent widget

        Returns:
            New Waypoint object or None if cancelled
        """
        dialog = WaypointPropertiesDialog(
            waypoint=None,
            waypoint_number=waypoint_number,
            is_wp1=is_wp1,
            parent=parent
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_waypoint()

        return None

    @staticmethod
    def edit_waypoint(waypoint: Waypoint, waypoint_number: int = 1,
                     is_wp1: bool = False, parent=None) -> bool:
        """
        Show dialog to edit an existing waypoint.

        Args:
            waypoint: Waypoint to edit
            waypoint_number: Waypoint number for display
            is_wp1: True if this is WP1
            parent: Parent widget

        Returns:
            True if changes were accepted, False if cancelled
        """
        dialog = WaypointPropertiesDialog(
            waypoint=waypoint,
            waypoint_number=waypoint_number,
            is_wp1=is_wp1,
            parent=parent
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog._update_waypoint(waypoint)
            return True

        return False
