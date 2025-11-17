"""
Route editor panel for managing target routes and waypoints.

Requirements:
- TSE-FUNC-130: Route editor panel
- TSE-FUNC-131: Add/edit/delete waypoints
- TSE-FUNC-132: Waypoint table view
- TSE-FUNC-136: Route metrics display
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QLabel, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, List

from tse.models.target import Target
from tse.models.waypoint import Waypoint
from tse.ui.widgets.waypoint_table_widget import WaypointTableWidget
from tse.ui.dialogs.waypoint_properties_dialog import WaypointPropertiesDialog
from tse.logic.route_calculator import RouteCalculator, RouteMetrics
from tse.validation.route_validator import RouteValidator


class RouteEditorPanel(QWidget):
    """
    Panel for editing target routes with waypoints.

    Features:
    - Waypoint table view
    - Add/Edit/Delete waypoint buttons
    - Route metrics display
    - Route validation feedback
    - Drag-and-drop waypoint reordering

    Requirements: TSE-FUNC-130 to TSE-FUNC-136
    """

    # Signals
    route_modified = pyqtSignal()  # Emitted when route is changed
    waypoint_selected = pyqtSignal(int)  # waypoint_index

    def __init__(self, parent=None):
        """Initialize route editor panel."""
        super().__init__(parent)

        self._target: Optional[Target] = None
        self._waypoints: List[Waypoint] = []

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout()

        # Target info
        self._target_label = QLabel("No target selected")
        self._target_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self._target_label)

        # Splitter for table and metrics
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Waypoint table
        self._waypoint_table = WaypointTableWidget()
        self._waypoint_table.waypoint_selected.connect(self._on_waypoint_selected)
        self._waypoint_table.waypoint_double_clicked.connect(self._on_edit_waypoint)
        self._waypoint_table.waypoint_deleted.connect(self._on_delete_waypoint)
        self._waypoint_table.waypoints_reordered.connect(self._on_waypoints_reordered)
        splitter.addWidget(self._waypoint_table)

        # Metrics panel
        metrics_widget = self._create_metrics_panel()
        splitter.addWidget(metrics_widget)

        # Set initial splitter sizes
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        # Buttons
        layout.addWidget(self._create_buttons())

        self.setLayout(layout)

    def _create_buttons(self) -> QWidget:
        """Create action buttons."""
        widget = QWidget()
        layout = QHBoxLayout()

        # Add Waypoint button
        self._add_btn = QPushButton("Add Waypoint")
        self._add_btn.clicked.connect(self._on_add_waypoint)
        layout.addWidget(self._add_btn)

        # Edit Waypoint button
        self._edit_btn = QPushButton("Edit Waypoint")
        self._edit_btn.clicked.connect(self._on_edit_waypoint)
        self._edit_btn.setEnabled(False)
        layout.addWidget(self._edit_btn)

        # Delete Waypoint button
        self._delete_btn = QPushButton("Delete Waypoint")
        self._delete_btn.clicked.connect(self._on_delete_waypoint_btn)
        self._delete_btn.setEnabled(False)
        layout.addWidget(self._delete_btn)

        layout.addStretch()

        # Validate button
        self._validate_btn = QPushButton("Validate Route")
        self._validate_btn.clicked.connect(self._on_validate_route)
        layout.addWidget(self._validate_btn)

        # Clear Route button
        self._clear_btn = QPushButton("Clear Route")
        self._clear_btn.clicked.connect(self._on_clear_route)
        layout.addWidget(self._clear_btn)

        widget.setLayout(layout)
        return widget

    def _create_metrics_panel(self) -> QGroupBox:
        """
        Create route metrics display panel.

        Requirements: TSE-FUNC-136
        """
        group = QGroupBox("Route Metrics")
        layout = QVBoxLayout()

        # Metrics labels
        self._metrics_label = QLabel("No route data")
        self._metrics_label.setWordWrap(True)
        layout.addWidget(self._metrics_label)

        # Validation status
        self._validation_label = QLabel()
        self._validation_label.setWordWrap(True)
        self._validation_label.setStyleSheet("font-family: monospace;")
        layout.addWidget(self._validation_label)

        group.setLayout(layout)
        return group

    def set_target(self, target: Target):
        """
        Set target for route editing.

        Args:
            target: Target object
        """
        self._target = target

        # Get waypoints from target
        if hasattr(target, 'route') and target.route:
            self._waypoints = target.route
        else:
            self._waypoints = []
            target.route = self._waypoints

        # Update display
        self._update_display()

    def _update_display(self):
        """Update all display elements."""
        # Update target label
        if self._target:
            self._target_label.setText(f"Route Editor: {self._target.name} ({self._target.target_id})")
        else:
            self._target_label.setText("No target selected")

        # Update waypoint table
        self._waypoint_table.set_waypoints(self._waypoints)

        # Update metrics
        self._update_metrics()

        # Update validation
        self._update_validation()

    def _update_metrics(self):
        """Update route metrics display."""
        if len(self._waypoints) < 2:
            self._metrics_label.setText("Add at least 2 waypoints to see route metrics")
            return

        # Calculate metrics
        metrics = RouteCalculator.calculate_route_metrics(self._waypoints)

        if not metrics:
            self._metrics_label.setText("Unable to calculate metrics")
            return

        # Format metrics display
        metrics_text = f"""
<b>Route Statistics:</b><br>
• Waypoints: {metrics.num_waypoints}<br>
• Total Distance: {RouteCalculator.format_distance(metrics.total_distance_m)}<br>
• Total Time: {RouteCalculator.format_time(metrics.total_time_sec)}<br>
• Average Speed: {RouteCalculator.format_speed(metrics.average_speed_knots)}<br>
• Speed Range: {metrics.min_speed_knots:.1f} - {metrics.max_speed_knots:.1f} kts
        """.strip()

        self._metrics_label.setText(metrics_text)

    def _update_validation(self):
        """Update route validation display."""
        if not self._waypoints:
            self._validation_label.setText("")
            return

        # Validate route
        issues = RouteValidator.validate_route(self._waypoints, self._target)

        # Format validation results
        validation_text = RouteValidator.format_issues(issues)

        # Set color based on validation status
        if RouteValidator.has_errors(issues):
            self._validation_label.setStyleSheet("color: red; font-family: monospace;")
        elif RouteValidator.has_warnings(issues):
            self._validation_label.setStyleSheet("color: orange; font-family: monospace;")
        else:
            self._validation_label.setStyleSheet("color: green; font-family: monospace;")

        self._validation_label.setText(validation_text)

    def _on_waypoint_selected(self, index: int):
        """Handle waypoint selection."""
        has_selection = index >= 0
        self._edit_btn.setEnabled(has_selection)
        self._delete_btn.setEnabled(has_selection)

        # Emit signal
        if has_selection:
            self.waypoint_selected.emit(index)

    def _on_add_waypoint(self):
        """
        Handle Add Waypoint button.

        Requirements: TSE-FUNC-131
        """
        # Determine waypoint number and time
        waypoint_num = len(self._waypoints) + 1
        is_wp1 = (waypoint_num == 1)

        # Default time (after last waypoint)
        if self._waypoints:
            default_time = self._waypoints[-1].time_sec + 60.0  # +1 minute
        else:
            default_time = 0.0

        # Show dialog
        new_waypoint = WaypointPropertiesDialog.create_waypoint(
            waypoint_number=waypoint_num,
            is_wp1=is_wp1,
            parent=self
        )

        if new_waypoint:
            # Override time if not WP1
            if not is_wp1:
                new_waypoint.time_sec = default_time

            # Add to route
            self._waypoints.append(new_waypoint)

            # Update display
            self._update_display()

            # Emit signal
            self.route_modified.emit()

    def _on_edit_waypoint(self, index: Optional[int] = None):
        """
        Handle Edit Waypoint.

        Args:
            index: Waypoint index (None = use selected)

        Requirements: TSE-FUNC-131
        """
        if index is None:
            index = self._waypoint_table.get_selected_waypoint_index()

        if index is None or not 0 <= index < len(self._waypoints):
            return

        waypoint = self._waypoints[index]
        is_wp1 = (index == 0)

        # Show dialog
        if WaypointPropertiesDialog.edit_waypoint(
            waypoint=waypoint,
            waypoint_number=index + 1,
            is_wp1=is_wp1,
            parent=self
        ):
            # Update display
            self._update_display()

            # Emit signal
            self.route_modified.emit()

    def _on_delete_waypoint(self, index: int):
        """Handle waypoint deletion from table context menu."""
        self._delete_waypoint(index)

    def _on_delete_waypoint_btn(self):
        """Handle Delete Waypoint button."""
        index = self._waypoint_table.get_selected_waypoint_index()
        if index is not None:
            self._delete_waypoint(index)

    def _delete_waypoint(self, index: int):
        """
        Delete a waypoint.

        Args:
            index: Waypoint index to delete

        Requirements: TSE-FUNC-131
        """
        if not 0 <= index < len(self._waypoints):
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Waypoint",
            f"Delete WP{index+1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete waypoint
            del self._waypoints[index]

            # Update display
            self._update_display()

            # Emit signal
            self.route_modified.emit()

    def _on_waypoints_reordered(self):
        """Handle waypoint reordering via drag-and-drop."""
        # Get reordered waypoints from table
        self._waypoints = self._waypoint_table.get_waypoints()

        # Update display
        self._update_display()

        # Emit signal
        self.route_modified.emit()

    def _on_validate_route(self):
        """Handle Validate Route button."""
        if not self._waypoints:
            QMessageBox.information(
                self,
                "Route Validation",
                "Route is empty. Add waypoints first."
            )
            return

        # Validate
        issues = RouteValidator.validate_route(self._waypoints, self._target)

        # Show results
        validation_text = RouteValidator.format_issues(issues)

        if RouteValidator.has_errors(issues):
            QMessageBox.critical(self, "Route Validation Failed", validation_text)
        elif RouteValidator.has_warnings(issues):
            QMessageBox.warning(self, "Route Validation Warnings", validation_text)
        else:
            QMessageBox.information(self, "Route Validation Passed", validation_text)

    def _on_clear_route(self):
        """Handle Clear Route button."""
        if not self._waypoints:
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Clear Route",
            "Delete all waypoints from this route?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._waypoints.clear()

            # Update display
            self._update_display()

            # Emit signal
            self.route_modified.emit()

    def get_waypoints(self) -> List[Waypoint]:
        """Get current waypoints."""
        return self._waypoints
