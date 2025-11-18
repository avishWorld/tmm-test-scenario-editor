"""
Export dialog for JSON export with preview and validation.

Requirements:
- TSE-FUNC-089: Export dialog with preview
- TSE-FUNC-088: Schema validation feedback
- TSE-FUNC-087: Pretty-printed JSON
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QMessageBox,
    QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from tse.models.scenario import Scenario
from tse.io.json_exporter import JSONExporter
from tse.io.json_schema_validator import JSONSchemaValidator


class ExportDialog(QDialog):
    """
    Dialog for exporting scenario to JSON with preview.

    Features:
    - JSON preview with syntax highlighting
    - Schema validation feedback
    - File path selection
    - Export button

    Requirements: TSE-FUNC-089, TSE-FUNC-088, TSE-FUNC-087
    """

    def __init__(self, scenario: Scenario, parent=None):
        """
        Initialize export dialog.

        Args:
            scenario: Scenario to export
            parent: Parent widget
        """
        super().__init__(parent)

        self._scenario = scenario
        self._exporter = JSONExporter()
        self._validator = JSONSchemaValidator()
        self._json_data = None
        self._json_string = None

        # Initialize UI
        self._init_ui()

        # Generate initial JSON
        self._generate_json()

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Export Scenario to JSON")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel(f"Exporting scenario: {self._scenario.title if hasattr(self._scenario, 'title') else 'Untitled'}")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(info_label)

        # Preview group
        layout.addWidget(self._create_preview_group())

        # Validation status
        self._validation_label = QLabel()
        self._validation_label.setWordWrap(True)
        layout.addWidget(self._validation_label)

        # Buttons
        layout.addWidget(self._create_buttons())

        self.setLayout(layout)

    def _create_preview_group(self) -> QGroupBox:
        """Create JSON preview group."""
        group = QGroupBox("JSON Preview")
        layout = QVBoxLayout()

        # Preview text edit
        self._preview_text = QTextEdit()
        self._preview_text.setReadOnly(True)
        self._preview_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Use monospace font
        font = QFont("Courier New", 10)
        self._preview_text.setFont(font)

        layout.addWidget(self._preview_text)

        # Options
        options_layout = QHBoxLayout()

        self._pretty_print_checkbox = QCheckBox("Pretty Print")
        self._pretty_print_checkbox.setChecked(True)
        self._pretty_print_checkbox.stateChanged.connect(self._on_format_changed)
        options_layout.addWidget(self._pretty_print_checkbox)

        options_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.clicked.connect(self._generate_json)
        options_layout.addWidget(refresh_btn)

        layout.addLayout(options_layout)

        group.setLayout(layout)
        return group

    def _create_buttons(self) -> QWidget:
        """Create dialog buttons."""
        widget = QWidget()
        layout = QHBoxLayout()

        # Export button
        export_btn = QPushButton("Export to File...")
        export_btn.clicked.connect(self._on_export)
        export_btn.setDefault(True)
        layout.addWidget(export_btn)

        # Copy to clipboard button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self._on_copy_to_clipboard)
        layout.addWidget(copy_btn)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        widget.setLayout(layout)
        return widget

    def _generate_json(self):
        """Generate JSON and update preview."""
        try:
            # Generate JSON data
            self._json_data = self._exporter.generate_json(self._scenario)

            # Generate JSON string
            pretty = self._pretty_print_checkbox.isChecked()
            self._json_string = self._exporter.export_to_string(self._scenario, pretty=pretty)

            # Update preview
            self._preview_text.setPlainText(self._json_string)

            # Validate
            self._validate_json()

        except Exception as e:
            self._preview_text.setPlainText(f"Error generating JSON:\n{str(e)}")
            self._validation_label.setText(f"❌ Generation Error: {str(e)}")
            self._validation_label.setStyleSheet("color: red; font-weight: bold;")

    def _validate_json(self):
        """Validate JSON against schema."""
        if not self._json_data:
            return

        # Validate
        is_valid, error_msg = self._validator.validate_json_data(self._json_data)

        if is_valid:
            self._validation_label.setText("✓ JSON is valid according to simulator schema")
            self._validation_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self._validation_label.setText(f"❌ Validation Error:\n{error_msg}")
            self._validation_label.setStyleSheet("color: red; font-weight: bold;")

    def _on_format_changed(self):
        """Handle format change (pretty print toggle)."""
        self._generate_json()

    def _on_export(self):
        """Handle Export to File button."""
        # Get filename
        default_filename = f"{self._scenario.scenario_id if hasattr(self._scenario, 'scenario_id') else 'scenario'}.json"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            default_filename,
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                # Export
                success = self._exporter.export_scenario(self._scenario, filename)

                if success:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Scenario exported to:\n{filename}"
                    )
                    self.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export scenario. Check file permissions."
                    )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Error during export:\n{str(e)}"
                )

    def _on_copy_to_clipboard(self):
        """Handle Copy to Clipboard button."""
        from PyQt6.QtWidgets import QApplication

        if self._json_string:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._json_string)

            QMessageBox.information(
                self,
                "Copied",
                "JSON copied to clipboard"
            )

    @staticmethod
    def export_scenario(scenario: Scenario, parent=None) -> bool:
        """
        Show export dialog for scenario.

        Args:
            scenario: Scenario to export
            parent: Parent widget

        Returns:
            True if exported successfully, False otherwise
        """
        dialog = ExportDialog(scenario, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted
