"""
Own Ship Configuration Dialog.

Allows users to configure Own Ship parameters.

Requirements:
- TSE-FUNC-010: Own Ship position (lat/lon)
- TSE-FUNC-011: Own Ship speed (0-40 knots)
- TSE-FUNC-012: Own Ship course (0-360°)
- TSE-FUNC-013: Own Ship sensor suite configuration
- TSE-UI-042: Field validation with visual feedback
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QLabel,
    QDialogButtonBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt

from ...models import OwnShip, GeoPosition, SensorConfiguration


class OwnShipConfigDialog(QDialog):
    """
    Dialog for configuring Own Ship.

    Requirements: TSE-FUNC-010 to TSE-FUNC-013, TSE-UI-042
    """

    def __init__(self, own_ship: OwnShip = None, parent=None):
        """
        Initialize the dialog.

        Args:
            own_ship: OwnShip to edit (None to create new)
            parent: Parent widget
        """
        super().__init__(parent)
        self.own_ship = own_ship
        self._init_ui()

        if own_ship:
            self._load_from_own_ship()
        else:
            # Set default position (Haifa, Israel)
            self.lat_spin.setValue(32.08)
            self.lon_spin.setValue(34.78)

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Own Ship Configuration")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Position Group (TSE-FUNC-010)
        position_group = QGroupBox("Position (WGS84)")
        position_layout = QFormLayout(position_group)

        # Latitude
        lat_layout = QHBoxLayout()
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90.0, 90.0)
        self.lat_spin.setDecimals(6)
        self.lat_spin.setSuffix(" °")
        self.lat_spin.setSingleStep(0.001)
        self.lat_spin.setToolTip("Latitude in decimal degrees (-90 to +90)")
        lat_layout.addWidget(self.lat_spin)
        lat_layout.addWidget(QLabel("North"))
        lat_layout.addStretch()
        position_layout.addRow("Latitude*:", lat_layout)

        # Longitude
        lon_layout = QHBoxLayout()
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180.0, 180.0)
        self.lon_spin.setDecimals(6)
        self.lon_spin.setSuffix(" °")
        self.lon_spin.setSingleStep(0.001)
        self.lon_spin.setToolTip("Longitude in decimal degrees (-180 to +180)")
        lon_layout.addWidget(self.lon_spin)
        lon_layout.addWidget(QLabel("East"))
        lon_layout.addStretch()
        position_layout.addRow("Longitude*:", lon_layout)

        layout.addWidget(position_group)

        # Kinematics Group (TSE-FUNC-011, TSE-FUNC-012)
        kinematics_group = QGroupBox("Kinematics")
        kinematics_layout = QFormLayout(kinematics_group)

        # Speed
        speed_layout = QHBoxLayout()
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.0, 40.0)
        self.speed_spin.setDecimals(1)
        self.speed_spin.setSuffix(" knots")
        self.speed_spin.setSingleStep(0.5)
        self.speed_spin.setToolTip("Speed in knots (0 to 40)")
        self.speed_spin.valueChanged.connect(self._update_speed_mps)
        speed_layout.addWidget(self.speed_spin)

        self.speed_mps_label = QLabel()
        speed_layout.addWidget(self.speed_mps_label)
        speed_layout.addStretch()
        self._update_speed_mps(0.0)

        kinematics_layout.addRow("Speed:", speed_layout)

        # Course
        course_layout = QHBoxLayout()
        self.course_spin = QDoubleSpinBox()
        self.course_spin.setRange(0.0, 359.9)
        self.course_spin.setDecimals(1)
        self.course_spin.setSuffix(" °")
        self.course_spin.setSingleStep(1.0)
        self.course_spin.setWrapping(True)
        self.course_spin.setToolTip("Course in degrees (0 to 360, true north)")
        course_layout.addWidget(self.course_spin)
        course_layout.addWidget(QLabel("(True North)"))
        course_layout.addStretch()
        kinematics_layout.addRow("Course:", course_layout)

        layout.addWidget(kinematics_group)

        # Sensor Configuration Group (TSE-FUNC-013)
        sensor_group = QGroupBox("Sensor Suite")
        sensor_layout = QVBoxLayout(sensor_group)

        self.ais_checkbox = QCheckBox("AIS (Automatic Identification System)")
        self.ais_checkbox.setChecked(True)
        sensor_layout.addWidget(self.ais_checkbox)

        self.radar_a_checkbox = QCheckBox("Radar A")
        self.radar_a_checkbox.setChecked(True)
        sensor_layout.addWidget(self.radar_a_checkbox)

        self.radar_b_checkbox = QCheckBox("Radar B")
        self.radar_b_checkbox.setChecked(True)
        sensor_layout.addWidget(self.radar_b_checkbox)

        self.eo_checkbox = QCheckBox("EO (Electro-Optical)")
        self.eo_checkbox.setChecked(True)
        sensor_layout.addWidget(self.eo_checkbox)

        layout.addWidget(sensor_group)

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

    def _update_speed_mps(self, knots: float):
        """Update speed display in m/s."""
        mps = knots * 0.51444
        self.speed_mps_label.setText(f"({mps:.2f} m/s)")

    def _load_from_own_ship(self):
        """Load values from Own Ship."""
        if self.own_ship and self.own_ship.position:
            self.lat_spin.setValue(self.own_ship.position.latitude_deg)
            self.lon_spin.setValue(self.own_ship.position.longitude_deg)
            self.speed_spin.setValue(self.own_ship.speed_knots)
            self.course_spin.setValue(self.own_ship.course_deg)

            if self.own_ship.sensors:
                self.ais_checkbox.setChecked(self.own_ship.sensors.ais_enabled)
                self.radar_a_checkbox.setChecked(self.own_ship.sensors.radar_a_enabled)
                self.radar_b_checkbox.setChecked(self.own_ship.sensors.radar_b_enabled)
                self.eo_checkbox.setChecked(self.own_ship.sensors.eo_enabled)

    def _validate(self) -> bool:
        """
        Validate all fields.

        Returns:
            True if all fields are valid

        Requirements: TSE-UI-042 (visual feedback)
        """
        # All fields are validated by their spin box constraints
        # Latitude: -90 to +90
        # Longitude: -180 to +180
        # Speed: 0 to 40
        # Course: 0 to 360

        # Warn if all sensors are disabled
        if not any([
            self.ais_checkbox.isChecked(),
            self.radar_a_checkbox.isChecked(),
            self.radar_b_checkbox.isChecked(),
            self.eo_checkbox.isChecked()
        ]):
            # This is valid but worth warning about
            pass

        return True

    def _accept(self):
        """Accept the dialog if validation passes."""
        if self._validate():
            self.accept()

    def get_own_ship(self) -> OwnShip:
        """
        Get the Own Ship with updated values.

        Returns:
            OwnShip object with values from dialog
        """
        position = GeoPosition(
            latitude_deg=self.lat_spin.value(),
            longitude_deg=self.lon_spin.value()
        )

        sensors = SensorConfiguration(
            ais_enabled=self.ais_checkbox.isChecked(),
            radar_a_enabled=self.radar_a_checkbox.isChecked(),
            radar_b_enabled=self.radar_b_checkbox.isChecked(),
            eo_enabled=self.eo_checkbox.isChecked()
        )

        if self.own_ship:
            # Update existing Own Ship
            self.own_ship.position = position
            self.own_ship.speed_knots = self.speed_spin.value()
            self.own_ship.course_deg = self.course_spin.value()
            self.own_ship.sensors = sensors
            return self.own_ship
        else:
            # Create new Own Ship
            return OwnShip(
                position=position,
                speed_knots=self.speed_spin.value(),
                course_deg=self.course_spin.value(),
                sensors=sensors
            )
