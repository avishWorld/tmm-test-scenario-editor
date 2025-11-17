"""
Sensor Configuration Panel Widget.

Reusable widget for configuring sensor suite.

Requirements:
- TSE-FUNC-050: Sensor configuration
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QGroupBox,
)

from ...models import SensorConfiguration


class SensorConfigPanel(QWidget):
    """
    Widget for configuring sensor suite.

    Provides checkboxes for each sensor type (AIS, Radar A, Radar B, EO).

    Requirements: TSE-FUNC-050
    """

    def __init__(self, title: str = "Sensor Configuration", parent=None):
        """
        Initialize the sensor configuration panel.

        Args:
            title: Title for the group box
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box
        group = QGroupBox(self.title)
        group_layout = QVBoxLayout(group)

        # AIS checkbox
        self.ais_checkbox = QCheckBox("AIS (Automatic Identification System)")
        self.ais_checkbox.setChecked(True)
        self.ais_checkbox.setToolTip("Enable AIS sensor for this target")
        group_layout.addWidget(self.ais_checkbox)

        # Radar A checkbox
        self.radar_a_checkbox = QCheckBox("Radar A")
        self.radar_a_checkbox.setChecked(True)
        self.radar_a_checkbox.setToolTip("Enable Radar A sensor for this target")
        group_layout.addWidget(self.radar_a_checkbox)

        # Radar B checkbox
        self.radar_b_checkbox = QCheckBox("Radar B")
        self.radar_b_checkbox.setChecked(True)
        self.radar_b_checkbox.setToolTip("Enable Radar B sensor for this target")
        group_layout.addWidget(self.radar_b_checkbox)

        # EO checkbox
        self.eo_checkbox = QCheckBox("EO (Electro-Optical)")
        self.eo_checkbox.setChecked(True)
        self.eo_checkbox.setToolTip("Enable Electro-Optical sensor for this target")
        group_layout.addWidget(self.eo_checkbox)

        layout.addWidget(group)

    def get_sensor_config(self) -> SensorConfiguration:
        """
        Get the sensor configuration from checkboxes.

        Returns:
            SensorConfiguration object
        """
        return SensorConfiguration(
            ais_enabled=self.ais_checkbox.isChecked(),
            radar_a_enabled=self.radar_a_checkbox.isChecked(),
            radar_b_enabled=self.radar_b_checkbox.isChecked(),
            eo_enabled=self.eo_checkbox.isChecked()
        )

    def set_sensor_config(self, config: SensorConfiguration):
        """
        Set the sensor configuration.

        Args:
            config: SensorConfiguration to apply
        """
        if config:
            self.ais_checkbox.setChecked(config.ais_enabled)
            self.radar_a_checkbox.setChecked(config.radar_a_enabled)
            self.radar_b_checkbox.setChecked(config.radar_b_enabled)
            self.eo_checkbox.setChecked(config.eo_enabled)

    def set_all_enabled(self, enabled: bool):
        """
        Enable or disable all sensors.

        Args:
            enabled: True to enable all, False to disable all
        """
        self.ais_checkbox.setChecked(enabled)
        self.radar_a_checkbox.setChecked(enabled)
        self.radar_b_checkbox.setChecked(enabled)
        self.eo_checkbox.setChecked(enabled)
