"""
Target Properties Dialog.

Allows users to create and edit maritime targets.

Requirements:
- TSE-FUNC-020: Target management
- TSE-FUNC-021: Relative positioning (range, bearing)
- TSE-FUNC-023: Unique Target ID auto-assignment
- TSE-FUNC-024: Target speed (0-40 knots)
- TSE-FUNC-025: Target course (0-360°)
- TSE-FUNC-026: Predefined vessel types
- TSE-FUNC-028: MMSI auto-generation
- TSE-FUNC-029: AIS class (A, B, or None)
- TSE-FUNC-030: Navigation status
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    QLabel,
    QDialogButtonBox,
    QGroupBox,
    QComboBox,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import Qt

from ...models import Target, GeoPosition, VesselType, AISClass, NavigationStatus
from ...utils import generate_mmsi, generate_target_id
from ..widgets import VesselTypeSelector, SensorConfigPanel


class TargetPropertiesDialog(QDialog):
    """
    Dialog for creating and editing targets.

    Requirements: TSE-FUNC-020 to TSE-FUNC-030
    """

    def __init__(self, target: Target = None, own_ship_pos: GeoPosition = None, parent=None):
        """
        Initialize the dialog.

        Args:
            target: Target to edit (None to create new)
            own_ship_pos: Own Ship position for relative calculations
            parent: Parent widget
        """
        super().__init__(parent)
        self.target = target
        self.own_ship_pos = own_ship_pos
        self._init_ui()

        if target:
            self._load_from_target()
        else:
            # Auto-generate ID and MMSI for new targets
            self.id_edit.setText(generate_target_id())
            self._generate_mmsi()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Target Properties")
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # Create tab widget for organized layout
        tabs = QTabWidget()

        # Tab 1: Basic Properties
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        self._create_basic_properties(basic_layout)
        tabs.addTab(basic_tab, "Basic")

        # Tab 2: Position & Kinematics
        position_tab = QWidget()
        position_layout = QVBoxLayout(position_tab)
        self._create_position_kinematics(position_layout)
        tabs.addTab(position_tab, "Position && Kinematics")

        # Tab 3: Sensors
        sensor_tab = QWidget()
        sensor_layout = QVBoxLayout(sensor_tab)
        self._create_sensor_config(sensor_layout)
        tabs.addTab(sensor_tab, "Sensors")

        layout.addWidget(tabs)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_basic_properties(self, layout):
        """Create basic properties group."""
        # Identification Group
        id_group = QGroupBox("Identification")
        id_layout = QFormLayout(id_group)

        # Target ID (TSE-FUNC-023)
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("e.g., T1, T2, ...")
        self.id_edit.setMaxLength(64)
        id_layout.addRow("Target ID*:", self.id_edit)

        # Target Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Cargo Ship Alpha")
        self.name_edit.setMaxLength(128)
        id_layout.addRow("Name:", self.name_edit)

        # MMSI (TSE-FUNC-028)
        mmsi_layout = QHBoxLayout()
        self.mmsi_spin = QSpinBox()
        self.mmsi_spin.setRange(100000000, 999999999)
        self.mmsi_spin.setValue(111000001)
        self.mmsi_spin.setToolTip("9-digit Maritime Mobile Service Identity")
        mmsi_layout.addWidget(self.mmsi_spin)

        mmsi_btn = QPushButton("Auto-Generate")
        mmsi_btn.setToolTip("Generate a unique MMSI number")
        mmsi_btn.clicked.connect(self._generate_mmsi)
        mmsi_layout.addWidget(mmsi_btn)
        mmsi_layout.addStretch()

        id_layout.addRow("MMSI:", mmsi_layout)

        layout.addWidget(id_group)

        # Vessel Type Group (TSE-FUNC-026)
        vessel_group = QGroupBox("Vessel Classification")
        vessel_layout = QFormLayout(vessel_group)

        self.vessel_type_selector = VesselTypeSelector()
        vessel_layout.addRow(self.vessel_type_selector)

        # AIS Class (TSE-FUNC-029)
        self.ais_class_combo = QComboBox()
        self.ais_class_combo.addItem("Class A", AISClass.CLASS_A)
        self.ais_class_combo.addItem("Class B", AISClass.CLASS_B)
        self.ais_class_combo.addItem("None (No AIS)", AISClass.NONE)
        vessel_layout.addRow("AIS Class:", self.ais_class_combo)

        # Navigation Status (TSE-FUNC-030)
        self.nav_status_combo = QComboBox()
        self.nav_status_combo.addItem("Under way using engine", NavigationStatus.UNDER_WAY_USING_ENGINE)
        self.nav_status_combo.addItem("At anchor", NavigationStatus.AT_ANCHOR)
        self.nav_status_combo.addItem("Moored", NavigationStatus.MOORED)
        self.nav_status_combo.addItem("Not under command", NavigationStatus.NOT_UNDER_COMMAND)
        vessel_layout.addRow("Navigation Status:", self.nav_status_combo)

        layout.addWidget(vessel_group)
        layout.addStretch()

    def _create_position_kinematics(self, layout):
        """Create position and kinematics group."""
        # Relative Position Group (TSE-FUNC-021)
        pos_group = QGroupBox("Relative Position (from Own Ship)")
        pos_layout = QFormLayout(pos_group)

        # Range
        range_layout = QHBoxLayout()
        self.range_spin = QDoubleSpinBox()
        self.range_spin.setRange(40.0, 20000.0)
        self.range_spin.setValue(1000.0)
        self.range_spin.setDecimals(1)
        self.range_spin.setSuffix(" m")
        self.range_spin.setSingleStep(10.0)
        self.range_spin.setToolTip("Range from Own Ship (40m to 20km)")
        range_layout.addWidget(self.range_spin)

        self.range_nm_label = QLabel()
        self.range_spin.valueChanged.connect(self._update_range_nm)
        self._update_range_nm(1000.0)
        range_layout.addWidget(self.range_nm_label)
        range_layout.addStretch()

        pos_layout.addRow("Range*:", range_layout)

        # Bearing
        bearing_layout = QHBoxLayout()
        self.bearing_spin = QDoubleSpinBox()
        self.bearing_spin.setRange(0.0, 359.9)
        self.bearing_spin.setValue(0.0)
        self.bearing_spin.setDecimals(1)
        self.bearing_spin.setSuffix(" °")
        self.bearing_spin.setSingleStep(1.0)
        self.bearing_spin.setWrapping(True)
        self.bearing_spin.setToolTip("Bearing from Own Ship (0-360°, true north)")
        bearing_layout.addWidget(self.bearing_spin)
        bearing_layout.addWidget(QLabel("(True North)"))
        bearing_layout.addStretch()

        pos_layout.addRow("Bearing*:", bearing_layout)

        layout.addWidget(pos_group)

        # Kinematics Group
        kin_group = QGroupBox("Kinematics")
        kin_layout = QFormLayout(kin_group)

        # Speed (TSE-FUNC-024)
        speed_layout = QHBoxLayout()
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.0, 40.0)
        self.speed_spin.setValue(0.0)
        self.speed_spin.setDecimals(1)
        self.speed_spin.setSuffix(" knots")
        self.speed_spin.setSingleStep(0.5)
        self.speed_spin.setToolTip("Speed (0 to 40 knots)")
        self.speed_spin.valueChanged.connect(self._update_speed_mps)
        speed_layout.addWidget(self.speed_spin)

        self.speed_mps_label = QLabel()
        speed_layout.addWidget(self.speed_mps_label)
        speed_layout.addStretch()
        self._update_speed_mps(0.0)

        kin_layout.addRow("Speed:", speed_layout)

        # Course (TSE-FUNC-025)
        course_layout = QHBoxLayout()
        self.course_spin = QDoubleSpinBox()
        self.course_spin.setRange(0.0, 359.9)
        self.course_spin.setValue(0.0)
        self.course_spin.setDecimals(1)
        self.course_spin.setSuffix(" °")
        self.course_spin.setSingleStep(1.0)
        self.course_spin.setWrapping(True)
        self.course_spin.setToolTip("Course (0 to 360°, true north)")
        course_layout.addWidget(self.course_spin)
        course_layout.addWidget(QLabel("(True North)"))
        course_layout.addStretch()

        kin_layout.addRow("Course:", course_layout)

        layout.addWidget(kin_group)
        layout.addStretch()

    def _create_sensor_config(self, layout):
        """Create sensor configuration group."""
        self.sensor_panel = SensorConfigPanel("Target Sensor Configuration")
        layout.addWidget(self.sensor_panel)
        layout.addStretch()

    def _generate_mmsi(self):
        """Generate a new MMSI number (TSE-FUNC-028)."""
        mmsi = generate_mmsi()
        self.mmsi_spin.setValue(mmsi)

    def _update_range_nm(self, meters: float):
        """Update range display in nautical miles."""
        nm = meters / 1852.0
        self.range_nm_label.setText(f"({nm:.2f} NM)")

    def _update_speed_mps(self, knots: float):
        """Update speed display in m/s."""
        mps = knots * 0.51444
        self.speed_mps_label.setText(f"({mps:.2f} m/s)")

    def _load_from_target(self):
        """Load values from target."""
        if not self.target:
            return

        self.id_edit.setText(self.target.target_id)
        self.name_edit.setText(self.target.name)
        self.mmsi_spin.setValue(self.target.mmsi if self.target.mmsi > 0 else 111000001)

        self.range_spin.setValue(self.target.relative_range_m)
        self.bearing_spin.setValue(self.target.relative_bearing_deg)
        self.speed_spin.setValue(self.target.speed_knots)
        self.course_spin.setValue(self.target.course_deg)

        self.vessel_type_selector.set_vessel_type(self.target.vessel_type)

        # Set AIS class
        for i in range(self.ais_class_combo.count()):
            if self.ais_class_combo.itemData(i) == self.target.ais_class:
                self.ais_class_combo.setCurrentIndex(i)
                break

        # Set navigation status
        for i in range(self.nav_status_combo.count()):
            if self.nav_status_combo.itemData(i) == self.target.nav_status:
                self.nav_status_combo.setCurrentIndex(i)
                break

        # Set sensors
        if self.target.sensors:
            self.sensor_panel.set_sensor_config(self.target.sensors)

    def _validate(self) -> bool:
        """Validate all fields."""
        # Target ID is required
        if not self.id_edit.text().strip():
            return False

        # All other fields are validated by their widgets
        return True

    def _accept(self):
        """Accept the dialog if validation passes."""
        if self._validate():
            self.accept()

    def get_target(self) -> Target:
        """
        Get the target with updated values.

        Returns:
            Target object with values from dialog
        """
        # Use vessel type selector's default dimensions
        dimensions = self.vessel_type_selector.get_default_dimensions()

        if self.target:
            # Update existing target
            self.target.target_id = self.id_edit.text().strip()
            self.target.name = self.name_edit.text().strip()
            self.target.relative_range_m = self.range_spin.value()
            self.target.relative_bearing_deg = self.bearing_spin.value()
            self.target.speed_knots = self.speed_spin.value()
            self.target.course_deg = self.course_spin.value()
            self.target.vessel_type = self.vessel_type_selector.get_vessel_type()
            self.target.dimensions = dimensions
            self.target.mmsi = self.mmsi_spin.value()
            self.target.ais_class = self.ais_class_combo.currentData()
            self.target.nav_status = self.nav_status_combo.currentData()
            self.target.sensors = self.sensor_panel.get_sensor_config()
            return self.target
        else:
            # Create new target
            return Target(
                target_id=self.id_edit.text().strip(),
                name=self.name_edit.text().strip(),
                relative_range_m=self.range_spin.value(),
                relative_bearing_deg=self.bearing_spin.value(),
                speed_knots=self.speed_spin.value(),
                course_deg=self.course_spin.value(),
                vessel_type=self.vessel_type_selector.get_vessel_type(),
                dimensions=dimensions,
                mmsi=self.mmsi_spin.value(),
                ais_class=self.ais_class_combo.currentData(),
                nav_status=self.nav_status_combo.currentData(),
                sensors=self.sensor_panel.get_sensor_config(),
            )
