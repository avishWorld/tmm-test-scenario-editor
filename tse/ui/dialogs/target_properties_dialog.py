"""
Target properties dialog for creating and editing targets.

Requirements:
- TSE-FUNC-020: Target configuration
- TSE-FUNC-021: Relative positioning (range, bearing)
- TSE-FUNC-026: Vessel type selection
- TSE-FUNC-028: MMSI auto-generation
- TSE-UI-041: OK/Cancel/Apply buttons
- TSE-UI-042: Field validation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDoubleSpinBox, QComboBox, QPushButton,
    QLabel, QGroupBox, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
from typing import Optional

from tse.models.target import Target, VesselType, AISClass, NavigationStatus
from tse.models.geo import GeoPosition


class TargetPropertiesDialog(QDialog):
    """
    Dialog for editing target properties.

    Features:
    - Target identification (ID, name)
    - Relative positioning (range, bearing)
    - Kinematics (speed, course)
    - Vessel type selection
    - MMSI configuration
    - AIS class and navigation status

    Requirements: TSE-FUNC-020 to TSE-FUNC-030
    """

    def __init__(self, target: Optional[Target] = None, target_number: int = 1, parent=None):
        """
        Initialize target properties dialog.

        Args:
            target: Existing target to edit (None for new)
            target_number: Target number for default ID
            parent: Parent widget
        """
        super().__init__(parent)

        self._target = target
        self._target_number = target_number

        # Initialize UI
        self._init_ui()

        # Populate if editing
        if self._target:
            self._populate_fields()

    def _init_ui(self):
        """Initialize user interface."""
        title = f"Edit Target" if self._target else f"Add Target"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        # Main layout
        layout = QVBoxLayout()

        # Form sections
        layout.addWidget(self._create_identification_group())
        layout.addWidget(self._create_positioning_group())
        layout.addWidget(self._create_kinematics_group())
        layout.addWidget(self._create_vessel_group())
        layout.addWidget(self._create_ais_group())

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

        # Target ID
        self._id_edit = QLineEdit()
        default_id = f"T{self._target_number}" if not self._target else self._target.target_id
        self._id_edit.setText(default_id)
        self._id_edit.setMaxLength(64)
        form.addRow("Target ID:", self._id_edit)

        # Target Name
        self._name_edit = QLineEdit()
        default_name = f"Target {self._target_number}" if not self._target else self._target.name
        self._name_edit.setText(default_name)
        self._name_edit.setMaxLength(128)
        form.addRow("Name:", self._name_edit)

        group.setLayout(form)
        return group

    def _create_positioning_group(self) -> QGroupBox:
        """Create positioning input group."""
        group = QGroupBox("Relative Positioning (from Own Ship)")
        form = QFormLayout()

        # Range
        self._range_spin = QDoubleSpinBox()
        self._range_spin.setRange(40.0, 20000.0)
        self._range_spin.setDecimals(1)
        self._range_spin.setSuffix(" m")
        self._range_spin.setValue(1000.0)
        form.addRow("Range:", self._range_spin)

        # Bearing
        self._bearing_spin = QDoubleSpinBox()
        self._bearing_spin.setRange(0.0, 359.9)
        self._bearing_spin.setDecimals(1)
        self._bearing_spin.setSuffix(" °")
        self._bearing_spin.setValue(0.0)
        self._bearing_spin.setWrapping(True)
        form.addRow("Bearing:", self._bearing_spin)

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
        form.addRow("Speed:", self._speed_spin)

        # Course
        self._course_spin = QDoubleSpinBox()
        self._course_spin.setRange(0.0, 359.9)
        self._course_spin.setDecimals(1)
        self._course_spin.setSuffix(" °")
        self._course_spin.setValue(0.0)
        self._course_spin.setWrapping(True)
        form.addRow("Course:", self._course_spin)

        group.setLayout(form)
        return group

    def _create_vessel_group(self) -> QGroupBox:
        """Create vessel type group."""
        group = QGroupBox("Vessel Information")
        form = QFormLayout()

        # Vessel Type
        self._vessel_type_combo = QComboBox()
        for vtype in VesselType:
            self._vessel_type_combo.addItem(vtype.value, vtype)
        form.addRow("Vessel Type:", self._vessel_type_combo)

        group.setLayout(form)
        return group

    def _create_ais_group(self) -> QGroupBox:
        """Create AIS configuration group."""
        group = QGroupBox("AIS Configuration")
        form = QFormLayout()

        # MMSI
        self._mmsi_spin = QSpinBox()
        self._mmsi_spin.setRange(100000000, 999999999)
        self._mmsi_spin.setValue(970000000 + self._target_number)
        form.addRow("MMSI:", self._mmsi_spin)

        # AIS Class
        self._ais_class_combo = QComboBox()
        for ais_class in AISClass:
            self._ais_class_combo.addItem(ais_class.value, ais_class)
        form.addRow("AIS Class:", self._ais_class_combo)

        # Navigation Status
        self._nav_status_combo = QComboBox()
        for nav_status in NavigationStatus:
            self._nav_status_combo.addItem(nav_status.value, nav_status)
        self._nav_status_combo.setCurrentIndex(2)  # Default: Under way using engine
        form.addRow("Nav Status:", self._nav_status_combo)

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
        if self._target:
            apply_button = QPushButton("Apply")
            apply_button.clicked.connect(self._on_apply)
            layout.addWidget(apply_button)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _populate_fields(self):
        """Populate fields from existing target."""
        if not self._target:
            return

        self._id_edit.setText(self._target.target_id)
        self._name_edit.setText(self._target.name)
        self._range_spin.setValue(self._target.relative_range_m)
        self._bearing_spin.setValue(self._target.relative_bearing_deg)
        self._speed_spin.setValue(self._target.speed_knots)
        self._course_spin.setValue(self._target.course_deg)

        # Set vessel type
        for i in range(self._vessel_type_combo.count()):
            if self._vessel_type_combo.itemData(i) == self._target.vessel_type:
                self._vessel_type_combo.setCurrentIndex(i)
                break

        self._mmsi_spin.setValue(self._target.mmsi)

        # Set AIS class
        if hasattr(self._target, 'ais_class'):
            for i in range(self._ais_class_combo.count()):
                if self._ais_class_combo.itemData(i) == self._target.ais_class:
                    self._ais_class_combo.setCurrentIndex(i)
                    break

        # Set nav status
        if hasattr(self._target, 'nav_status'):
            for i in range(self._nav_status_combo.count()):
                if self._nav_status_combo.itemData(i) == self._target.nav_status:
                    self._nav_status_combo.setCurrentIndex(i)
                    break

    def _validate_inputs(self) -> bool:
        """Validate input fields."""
        self._validation_label.hide()
        errors = []

        # Validate ID
        if not self._id_edit.text().strip():
            errors.append("Target ID is required")

        # Validate name
        if not self._name_edit.text().strip():
            errors.append("Target name is required")

        # Validate range
        range_val = self._range_spin.value()
        if not 40.0 <= range_val <= 20000.0:
            errors.append(f"Range must be between 40 and 20,000 meters")

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
        if self._validate_inputs() and self._target:
            self._update_target(self._target)

    def _update_target(self, target: Target):
        """Update target from form fields."""
        target.target_id = self._id_edit.text().strip()
        target.name = self._name_edit.text().strip()
        target.relative_range_m = self._range_spin.value()
        target.relative_bearing_deg = self._bearing_spin.value()
        target.speed_knots = self._speed_spin.value()
        target.course_deg = self._course_spin.value()
        target.vessel_type = self._vessel_type_combo.currentData()
        target.mmsi = self._mmsi_spin.value()
        target.ais_class = self._ais_class_combo.currentData()
        target.nav_status = self._nav_status_combo.currentData()

    def get_target(self) -> Target:
        """Get target from dialog inputs."""
        target = Target(
            target_id=self._id_edit.text().strip(),
            name=self._name_edit.text().strip(),
            relative_range_m=self._range_spin.value(),
            relative_bearing_deg=self._bearing_spin.value(),
            speed_knots=self._speed_spin.value(),
            course_deg=self._course_spin.value(),
            vessel_type=self._vessel_type_combo.currentData(),
            mmsi=self._mmsi_spin.value()
        )

        target.ais_class = self._ais_class_combo.currentData()
        target.nav_status = self._nav_status_combo.currentData()

        return target

    @staticmethod
    def create_target(target_number: int = 1, parent=None) -> Optional[Target]:
        """
        Show dialog to create a new target.

        Args:
            target_number: Target number for defaults
            parent: Parent widget

        Returns:
            New Target object or None if cancelled
        """
        dialog = TargetPropertiesDialog(None, target_number, parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_target()

        return None

    @staticmethod
    def edit_target(target: Target, parent=None) -> bool:
        """
        Show dialog to edit an existing target.

        Args:
            target: Target to edit
            parent: Parent widget

        Returns:
            True if changes accepted, False if cancelled
        """
        dialog = TargetPropertiesDialog(target, parent=parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog._update_target(target)
            return True

        return False
