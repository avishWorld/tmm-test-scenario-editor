"""
Vessel Type Selector Widget.

Allows users to select vessel type with automatic dimension defaults.

Requirements:
- TSE-FUNC-026: Predefined vessel types
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QGroupBox,
)
from PyQt6.QtCore import pyqtSignal

from ...models import VesselType, VesselDimensions


class VesselTypeSelector(QWidget):
    """
    Widget for selecting vessel type.

    Displays vessel type combo box and shows default dimensions.

    Requirements: TSE-FUNC-026
    """

    # Signal emitted when vessel type changes
    vessel_type_changed = pyqtSignal(VesselType, VesselDimensions)

    def __init__(self, parent=None):
        """Initialize the vessel type selector."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Vessel type combo box
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Vessel Type:"))

        self.type_combo = QComboBox()
        self.type_combo.addItem("Small Boat (10-30m)", VesselType.SMALL_BOAT)
        self.type_combo.addItem("Medium Cargo (50-100m)", VesselType.MEDIUM_CARGO)
        self.type_combo.addItem("Large Cargo (150-250m)", VesselType.LARGE_CARGO)
        self.type_combo.addItem("Tanker (200-350m)", VesselType.TANKER)
        self.type_combo.addItem("Navigation Buoy (5m)", VesselType.NAVIGATION_BUOY)
        self.type_combo.addItem("Custom", VesselType.CUSTOM)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()

        layout.addLayout(type_layout)

        # Default dimensions label
        self.dimensions_label = QLabel()
        self.dimensions_label.setStyleSheet("QLabel { color: gray; font-style: italic; }")
        layout.addWidget(self.dimensions_label)

        # Update initial display
        self._update_dimensions_label()

    def _on_type_changed(self):
        """Handle vessel type change."""
        vessel_type = self.get_vessel_type()
        dimensions = self._get_default_dimensions(vessel_type)
        self._update_dimensions_label()
        self.vessel_type_changed.emit(vessel_type, dimensions)

    def _update_dimensions_label(self):
        """Update the dimensions label."""
        vessel_type = self.get_vessel_type()
        dimensions = self._get_default_dimensions(vessel_type)

        self.dimensions_label.setText(
            f"Default dimensions: {dimensions.length_m}m × {dimensions.width_m}m × {dimensions.height_m}m"
        )

    def _get_default_dimensions(self, vessel_type: VesselType) -> VesselDimensions:
        """Get default dimensions for vessel type."""
        defaults = {
            VesselType.SMALL_BOAT: (20.0, 5.0, 3.0),
            VesselType.MEDIUM_CARGO: (75.0, 12.0, 8.0),
            VesselType.LARGE_CARGO: (200.0, 30.0, 15.0),
            VesselType.TANKER: (275.0, 45.0, 20.0),
            VesselType.NAVIGATION_BUOY: (5.0, 5.0, 2.0),
            VesselType.CUSTOM: (50.0, 10.0, 5.0),
        }

        length, width, height = defaults.get(vessel_type, (50.0, 10.0, 5.0))
        return VesselDimensions(length, width, height)

    def get_vessel_type(self) -> VesselType:
        """Get the currently selected vessel type."""
        return self.type_combo.currentData()

    def set_vessel_type(self, vessel_type: VesselType):
        """Set the vessel type."""
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == vessel_type:
                self.type_combo.setCurrentIndex(i)
                break

    def get_default_dimensions(self) -> VesselDimensions:
        """Get default dimensions for current vessel type."""
        return self._get_default_dimensions(self.get_vessel_type())
