"""
Sensor configuration panel for enabling/disabling sensors and managing dropouts.

Requirements:
- TSE-FUNC-050: Sensor enable/disable configuration
- TSE-FUNC-140: Sensor dropout configuration
- TSE-FUNC-141: Dropout schedule table
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional

from tse.models.sensor import SensorConfiguration, SensorDropout, SensorType


class SensorConfigPanel(QWidget):
    """
    Panel for configuring sensors and their dropout schedules.

    Features:
    - Enable/disable individual sensors (AIS, RADAR_A, RADAR_B, EO)
    - Dropout schedule table
    - Add/Edit/Delete dropout buttons
    - Visual feedback for active dropouts

    Requirements: TSE-FUNC-050, TSE-FUNC-140, TSE-FUNC-141
    """

    # Signals
    config_changed = pyqtSignal()  # Emitted when configuration changes
    dropout_selected = pyqtSignal(int)  # dropout_index

    def __init__(self, parent=None):
        """Initialize sensor configuration panel."""
        super().__init__(parent)

        self._sensor_config: Optional[SensorConfiguration] = None
        self._dropouts: List[SensorDropout] = []

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()

        # Sensor enable/disable
        layout.addWidget(self._create_sensor_group())

        # Dropout schedule
        layout.addWidget(self._create_dropout_group())

        self.setLayout(layout)

    def _create_sensor_group(self) -> QGroupBox:
        """
        Create sensor enable/disable group.

        Requirements: TSE-FUNC-050
        """
        group = QGroupBox("Available Sensors")
        layout = QVBoxLayout()

        # AIS checkbox
        self._ais_checkbox = QCheckBox("AIS (Automatic Identification System)")
        self._ais_checkbox.setChecked(True)
        self._ais_checkbox.stateChanged.connect(self._on_sensor_changed)
        layout.addWidget(self._ais_checkbox)

        # RADAR A checkbox
        self._radar_a_checkbox = QCheckBox("RADAR A (Primary)")
        self._radar_a_checkbox.setChecked(True)
        self._radar_a_checkbox.stateChanged.connect(self._on_sensor_changed)
        layout.addWidget(self._radar_a_checkbox)

        # RADAR B checkbox
        self._radar_b_checkbox = QCheckBox("RADAR B (Secondary)")
        self._radar_b_checkbox.setChecked(True)
        self._radar_b_checkbox.stateChanged.connect(self._on_sensor_changed)
        layout.addWidget(self._radar_b_checkbox)

        # EO checkbox
        self._eo_checkbox = QCheckBox("EO (Electro-Optical)")
        self._eo_checkbox.setChecked(True)
        self._eo_checkbox.stateChanged.connect(self._on_sensor_changed)
        layout.addWidget(self._eo_checkbox)

        group.setLayout(layout)
        return group

    def _create_dropout_group(self) -> QGroupBox:
        """
        Create dropout schedule group.

        Requirements: TSE-FUNC-141
        """
        group = QGroupBox("Sensor Dropout Schedule")
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Configure temporary sensor failures during scenario:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Dropout table
        self._dropout_table = QTableWidget()
        self._setup_dropout_table()
        layout.addWidget(self._dropout_table)

        # Buttons
        layout.addWidget(self._create_dropout_buttons())

        group.setLayout(layout)
        return group

    def _setup_dropout_table(self):
        """Setup dropout schedule table."""
        # Columns
        self._dropout_table.setColumnCount(4)
        self._dropout_table.setHorizontalHeaderLabels([
            "Sensor",
            "Start Time (s)",
            "End Time (s)",
            "Duration (s)"
        ])

        # Table settings
        self._dropout_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._dropout_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._dropout_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._dropout_table.setAlternatingRowColors(True)

        # Resize columns
        header = self._dropout_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Connect signals
        self._dropout_table.itemSelectionChanged.connect(self._on_dropout_selected)
        self._dropout_table.itemDoubleClicked.connect(self._on_edit_dropout)

    def _create_dropout_buttons(self) -> QWidget:
        """Create dropout action buttons."""
        widget = QWidget()
        layout = QHBoxLayout()

        # Add dropout button
        self._add_dropout_btn = QPushButton("Add Dropout")
        self._add_dropout_btn.clicked.connect(self._on_add_dropout)
        layout.addWidget(self._add_dropout_btn)

        # Edit dropout button
        self._edit_dropout_btn = QPushButton("Edit Dropout")
        self._edit_dropout_btn.clicked.connect(self._on_edit_dropout)
        self._edit_dropout_btn.setEnabled(False)
        layout.addWidget(self._edit_dropout_btn)

        # Delete dropout button
        self._delete_dropout_btn = QPushButton("Delete Dropout")
        self._delete_dropout_btn.clicked.connect(self._on_delete_dropout)
        self._delete_dropout_btn.setEnabled(False)
        layout.addWidget(self._delete_dropout_btn)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def set_sensor_config(self, config: SensorConfiguration):
        """
        Set sensor configuration.

        Args:
            config: SensorConfiguration object
        """
        self._sensor_config = config
        self._update_sensor_checkboxes()

    def set_dropouts(self, dropouts: List[SensorDropout]):
        """
        Set dropout schedule.

        Args:
            dropouts: List of SensorDropout objects
        """
        self._dropouts = dropouts
        self._update_dropout_table()

    def get_sensor_config(self) -> SensorConfiguration:
        """Get current sensor configuration."""
        if not self._sensor_config:
            self._sensor_config = SensorConfiguration()

        self._sensor_config.ais_enabled = self._ais_checkbox.isChecked()
        self._sensor_config.radar_a_enabled = self._radar_a_checkbox.isChecked()
        self._sensor_config.radar_b_enabled = self._radar_b_checkbox.isChecked()
        self._sensor_config.eo_enabled = self._eo_checkbox.isChecked()

        return self._sensor_config

    def get_dropouts(self) -> List[SensorDropout]:
        """Get current dropout schedule."""
        return self._dropouts

    def _update_sensor_checkboxes(self):
        """Update checkbox states from configuration."""
        if not self._sensor_config:
            return

        self._ais_checkbox.setChecked(self._sensor_config.ais_enabled)
        self._radar_a_checkbox.setChecked(self._sensor_config.radar_a_enabled)
        self._radar_b_checkbox.setChecked(self._sensor_config.radar_b_enabled)
        self._eo_checkbox.setChecked(self._sensor_config.eo_enabled)

    def _update_dropout_table(self):
        """Update dropout table with current dropouts."""
        self._dropout_table.setRowCount(len(self._dropouts))

        for i, dropout in enumerate(self._dropouts):
            # Sensor type
            sensor_name = dropout.sensor_type.value if hasattr(dropout.sensor_type, 'value') else str(dropout.sensor_type)
            self._dropout_table.setItem(i, 0, self._create_centered_item(sensor_name))

            # Start time
            self._dropout_table.setItem(i, 1, self._create_centered_item(f"{dropout.start_time_sec:.1f}"))

            # End time
            self._dropout_table.setItem(i, 2, self._create_centered_item(f"{dropout.end_time_sec:.1f}"))

            # Duration
            duration = dropout.end_time_sec - dropout.start_time_sec
            self._dropout_table.setItem(i, 3, self._create_centered_item(f"{duration:.1f}"))

    def _create_centered_item(self, text: str) -> QTableWidgetItem:
        """Create table item with centered text."""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _on_sensor_changed(self):
        """Handle sensor checkbox change."""
        self.config_changed.emit()

    def _on_dropout_selected(self):
        """Handle dropout selection."""
        selected = len(self._dropout_table.selectedItems()) > 0
        self._edit_dropout_btn.setEnabled(selected)
        self._delete_dropout_btn.setEnabled(selected)

        if selected:
            row = self._dropout_table.currentRow()
            self.dropout_selected.emit(row)

    def _on_add_dropout(self):
        """Handle Add Dropout button."""
        from tse.ui.dialogs.dropout_dialog import DropoutDialog

        dropout = DropoutDialog.create_dropout(parent=self)
        if dropout:
            self._dropouts.append(dropout)
            self._update_dropout_table()
            self.config_changed.emit()

    def _on_edit_dropout(self):
        """Handle Edit Dropout button."""
        row = self._dropout_table.currentRow()
        if row < 0 or row >= len(self._dropouts):
            return

        from tse.ui.dialogs.dropout_dialog import DropoutDialog

        dropout = self._dropouts[row]
        if DropoutDialog.edit_dropout(dropout, parent=self):
            self._update_dropout_table()
            self.config_changed.emit()

    def _on_delete_dropout(self):
        """Handle Delete Dropout button."""
        row = self._dropout_table.currentRow()
        if row < 0 or row >= len(self._dropouts):
            return

        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Delete Dropout",
            f"Delete dropout starting at {self._dropouts[row].start_time_sec}s?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self._dropouts[row]
            self._update_dropout_table()
            self.config_changed.emit()

    def refresh(self):
        """Refresh display."""
        self._update_sensor_checkboxes()
        self._update_dropout_table()
