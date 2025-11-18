"""
Dropout dialog for creating and editing sensor dropouts.

Requirements:
- TSE-FUNC-142: Dropout add/edit dialog
- TSE-FUNC-053: Dropout time range specification
- TSE-FUNC-054: Sensor type selection for dropout
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional

from tse.models.sensor import SensorDropout, SensorType


class DropoutDialog(QDialog):
    """
    Dialog for editing sensor dropout properties.

    Features:
    - Sensor type selection (AIS, RADAR_A, RADAR_B, EO)
    - Start/End time input
    - Real-time validation
    - Duration display

    Requirements: TSE-FUNC-142, TSE-FUNC-053, TSE-FUNC-054
    """

    def __init__(self, dropout: Optional[SensorDropout] = None, parent=None):
        """
        Initialize dropout dialog.

        Args:
            dropout: Existing dropout to edit (None for new)
            parent: Parent widget
        """
        super().__init__(parent)

        self._dropout = dropout

        # Initialize UI
        self._init_ui()

        # Populate fields if editing
        if self._dropout:
            self._populate_fields()

    def _init_ui(self):
        """Initialize user interface."""
        title = "Edit Dropout" if self._dropout else "Add Dropout"
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout()

        # Form
        layout.addWidget(self._create_form())

        # Duration display
        self._duration_label = QLabel()
        self._duration_label.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self._duration_label)

        # Validation message
        self._validation_label = QLabel()
        self._validation_label.setWordWrap(True)
        self._validation_label.setStyleSheet("color: red; font-weight: bold;")
        self._validation_label.hide()
        layout.addWidget(self._validation_label)

        # Buttons
        layout.addWidget(self._create_buttons())

        self.setLayout(layout)

        # Initial validation
        self._update_duration()
        self._validate_inputs()

    def _create_form(self) -> QGroupBox:
        """Create input form."""
        group = QGroupBox("Dropout Configuration")
        form = QFormLayout()

        # Sensor type
        self._sensor_combo = QComboBox()
        self._sensor_combo.addItem("AIS", SensorType.AIS)
        self._sensor_combo.addItem("RADAR A", SensorType.RADAR_A)
        self._sensor_combo.addItem("RADAR B", SensorType.RADAR_B)
        self._sensor_combo.addItem("EO (Electro-Optical)", SensorType.EO)
        form.addRow("Sensor:", self._sensor_combo)

        # Start time
        self._start_time_spin = QDoubleSpinBox()
        self._start_time_spin.setRange(0.0, 86400.0)  # 0 to 24 hours
        self._start_time_spin.setDecimals(1)
        self._start_time_spin.setSuffix(" s")
        self._start_time_spin.setValue(0.0)
        self._start_time_spin.valueChanged.connect(self._on_time_changed)
        form.addRow("Start Time:", self._start_time_spin)

        # End time
        self._end_time_spin = QDoubleSpinBox()
        self._end_time_spin.setRange(0.0, 86400.0)
        self._end_time_spin.setDecimals(1)
        self._end_time_spin.setSuffix(" s")
        self._end_time_spin.setValue(60.0)  # Default 60s dropout
        self._end_time_spin.valueChanged.connect(self._on_time_changed)
        form.addRow("End Time:", self._end_time_spin)

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

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _populate_fields(self):
        """Populate fields from existing dropout."""
        if not self._dropout:
            return

        # Find sensor type index
        for i in range(self._sensor_combo.count()):
            if self._sensor_combo.itemData(i) == self._dropout.sensor_type:
                self._sensor_combo.setCurrentIndex(i)
                break

        self._start_time_spin.setValue(self._dropout.start_time_sec)
        self._end_time_spin.setValue(self._dropout.end_time_sec)

    def _on_time_changed(self):
        """Handle time change."""
        self._update_duration()
        self._validate_inputs()

    def _update_duration(self):
        """Update duration display."""
        start = self._start_time_spin.value()
        end = self._end_time_spin.value()
        duration = end - start

        if duration > 0:
            self._duration_label.setText(f"Duration: {duration:.1f} seconds")
            self._duration_label.setStyleSheet("font-weight: bold; color: blue;")
        else:
            self._duration_label.setText(f"Duration: {duration:.1f} seconds (INVALID)")
            self._duration_label.setStyleSheet("font-weight: bold; color: red;")

    def _validate_inputs(self) -> bool:
        """
        Validate input fields.

        Returns:
            True if all inputs are valid

        Requirements: TSE-FUNC-053
        """
        # Clear previous validation
        self._validation_label.hide()

        errors = []

        # Validate time range
        start = self._start_time_spin.value()
        end = self._end_time_spin.value()

        if start < 0:
            errors.append("Start time must be >= 0")

        if end <= start:
            errors.append("End time must be greater than start time")

        if end > 86400:
            errors.append("End time must be <= 86400 (24 hours)")

        # Validate duration
        duration = end - start
        if duration < 1.0:
            errors.append("Dropout duration must be at least 1 second")

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

    def get_dropout(self) -> SensorDropout:
        """
        Get dropout from dialog inputs.

        Returns:
            SensorDropout object
        """
        dropout = SensorDropout(
            sensor_type=self._sensor_combo.currentData(),
            start_time_sec=self._start_time_spin.value(),
            end_time_sec=self._end_time_spin.value()
        )
        return dropout

    def _update_dropout(self, dropout: SensorDropout):
        """Update dropout object from form fields."""
        dropout.sensor_type = self._sensor_combo.currentData()
        dropout.start_time_sec = self._start_time_spin.value()
        dropout.end_time_sec = self._end_time_spin.value()

    @staticmethod
    def create_dropout(parent=None) -> Optional[SensorDropout]:
        """
        Show dialog to create a new dropout.

        Args:
            parent: Parent widget

        Returns:
            New SensorDropout object or None if cancelled
        """
        dialog = DropoutDialog(dropout=None, parent=parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_dropout()

        return None

    @staticmethod
    def edit_dropout(dropout: SensorDropout, parent=None) -> bool:
        """
        Show dialog to edit an existing dropout.

        Args:
            dropout: Dropout to edit
            parent: Parent widget

        Returns:
            True if changes were accepted, False if cancelled
        """
        dialog = DropoutDialog(dropout=dropout, parent=parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog._update_dropout(dropout)
            return True

        return False
