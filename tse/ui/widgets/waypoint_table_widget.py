"""
Waypoint table widget for displaying and editing route waypoints.

Requirements:
- TSE-FUNC-132: Waypoint table view
- TSE-FUNC-133: Drag-and-drop waypoint reordering
- TSE-FUNC-136: Route metrics display
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
from typing import List, Optional

from tse.models.waypoint import Waypoint
from tse.logic.route_calculator import RouteCalculator


class WaypointTableWidget(QTableWidget):
    """
    Table widget for displaying and managing route waypoints.

    Features:
    - Display waypoint properties in columns
    - Select and highlight waypoints
    - Drag-and-drop reordering
    - Context menu for waypoint operations
    - Color coding for validation issues

    Requirements: TSE-FUNC-132, TSE-FUNC-133
    """

    # Signals
    waypoint_selected = pyqtSignal(int)  # waypoint_index
    waypoint_double_clicked = pyqtSignal(int)  # waypoint_index
    waypoint_deleted = pyqtSignal(int)  # waypoint_index
    waypoints_reordered = pyqtSignal()  # emitted after drag-drop

    # Column indices
    COL_NUMBER = 0
    COL_TIME = 1
    COL_LATITUDE = 2
    COL_LONGITUDE = 3
    COL_SPEED = 4
    COL_COURSE = 5
    COL_DISTANCE = 6
    COL_REQUIRED_SPEED = 7

    def __init__(self, parent=None):
        """Initialize waypoint table widget."""
        super().__init__(parent)

        self._waypoints: List[Waypoint] = []

        # Configure table
        self._setup_table()

    def _setup_table(self):
        """Setup table structure and behavior."""
        # Set columns
        column_headers = [
            "WP#",
            "Time (s)",
            "Latitude (°)",
            "Longitude (°)",
            "Speed (kts)",
            "Course (°)",
            "Distance (NM)",
            "Req. Speed (kts)"
        ]
        self.setColumnCount(len(column_headers))
        self.setHorizontalHeaderLabels(column_headers)

        # Configure table behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Read-only
        self.setAlternatingRowColors(True)

        # Enable drag-and-drop for reordering (TSE-FUNC-133)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDropIndicatorShown(True)

        # Resize columns
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)

        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def set_waypoints(self, waypoints: List[Waypoint]):
        """
        Set waypoints to display in table.

        Args:
            waypoints: List of Waypoint objects
        """
        self._waypoints = waypoints
        self._populate_table()

    def get_waypoints(self) -> List[Waypoint]:
        """Get current waypoints."""
        return self._waypoints

    def _populate_table(self):
        """Populate table with waypoint data."""
        self.setRowCount(len(self._waypoints))

        for i, wp in enumerate(self._waypoints):
            # WP Number
            self.setItem(i, self.COL_NUMBER, self._create_item(f"WP{i+1}"))

            # Time
            self.setItem(i, self.COL_TIME, self._create_item(f"{wp.time_sec:.1f}"))

            # Position
            if wp.position:
                self.setItem(i, self.COL_LATITUDE, self._create_item(f"{wp.position.latitude:.5f}"))
                self.setItem(i, self.COL_LONGITUDE, self._create_item(f"{wp.position.longitude:.5f}"))
            else:
                self.setItem(i, self.COL_LATITUDE, self._create_item("N/A"))
                self.setItem(i, self.COL_LONGITUDE, self._create_item("N/A"))

            # Speed and Course
            self.setItem(i, self.COL_SPEED, self._create_item(f"{wp.speed_knots:.1f}"))
            self.setItem(i, self.COL_COURSE, self._create_item(f"{wp.course_deg:.1f}"))

            # Distance and Required Speed (calculated from previous waypoint)
            if i > 0:
                prev_wp = self._waypoints[i - 1]
                distance_m = RouteCalculator.calculate_leg_distance(prev_wp, wp)
                distance_nm = distance_m / 1852.0
                req_speed = RouteCalculator.calculate_required_speed(prev_wp, wp)

                self.setItem(i, self.COL_DISTANCE, self._create_item(f"{distance_nm:.2f}"))
                self.setItem(i, self.COL_REQUIRED_SPEED, self._create_item(f"{req_speed:.1f}"))

                # Highlight if required speed exceeds max
                if req_speed > 40.0:
                    self._highlight_row(i, QColor(255, 200, 200))  # Light red
            else:
                # WP1 has no previous waypoint
                self.setItem(i, self.COL_DISTANCE, self._create_item("-"))
                self.setItem(i, self.COL_REQUIRED_SPEED, self._create_item("-"))

                # Highlight WP1 in light blue
                self._highlight_row(i, QColor(200, 220, 255))

    def _create_item(self, text: str) -> QTableWidgetItem:
        """Create a table item with centered text."""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _highlight_row(self, row: int, color: QColor):
        """Highlight entire row with a background color."""
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    def _on_selection_changed(self):
        """Handle selection change."""
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.waypoint_selected.emit(row)

    def _on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on item."""
        row = item.row()
        self.waypoint_double_clicked.emit(row)

    def _show_context_menu(self, position):
        """Show context menu for waypoint operations."""
        menu = QMenu(self)

        # Get selected waypoint
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        # Actions
        edit_action = menu.addAction("Edit Waypoint...")
        edit_action.triggered.connect(lambda: self.waypoint_double_clicked.emit(row))

        menu.addSeparator()

        delete_action = menu.addAction("Delete Waypoint")
        delete_action.triggered.connect(lambda: self.waypoint_deleted.emit(row))

        # Don't allow deleting WP1 if it's the only waypoint
        if row == 0 and len(self._waypoints) == 1:
            delete_action.setEnabled(False)

        menu.addSeparator()

        insert_before_action = menu.addAction("Insert Waypoint Before...")
        insert_after_action = menu.addAction("Insert Waypoint After...")

        # Show menu
        menu.exec(self.viewport().mapToGlobal(position))

    def select_waypoint(self, index: int):
        """
        Select a specific waypoint by index.

        Args:
            index: Waypoint index (0-based)
        """
        if 0 <= index < len(self._waypoints):
            self.selectRow(index)

    def get_selected_waypoint_index(self) -> Optional[int]:
        """
        Get index of currently selected waypoint.

        Returns:
            Waypoint index or None if no selection
        """
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            return selected_rows[0].row()
        return None

    def refresh(self):
        """Refresh table display with current waypoints."""
        self._populate_table()

    def dropEvent(self, event):
        """
        Handle drop event for waypoint reordering.

        Requirements: TSE-FUNC-133
        """
        # Get source and destination rows
        source_row = self.currentRow()

        # Let Qt handle the visual move
        super().dropEvent(event)

        # Get new position after drop
        dest_row = self.currentRow()

        # Reorder waypoints list
        if source_row != dest_row and 0 <= source_row < len(self._waypoints):
            waypoint = self._waypoints.pop(source_row)
            insert_pos = dest_row if dest_row < source_row else dest_row
            self._waypoints.insert(insert_pos, waypoint)

            # Refresh table
            self._populate_table()

            # Emit signal
            self.waypoints_reordered.emit()
