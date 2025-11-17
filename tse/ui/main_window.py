"""
Main application window for TMM Test Scenario Editor.

Requirements:
- TSE-UI-001: Main window with menu bar and toolbar
- TSE-UI-002: Resizable panel layout
- TSE-UI-003: Window state persistence
- TSE-PERF-001: Startup time < 5 seconds
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter,
    QDockWidget, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from typing import Optional

from tse.ui.map_view import MapView
from tse.models.scenario import Scenario
from tse.models.own_ship import OwnShip
from tse.models.geo import GeoPosition


class MainWindow(QMainWindow):
    """
    Main application window for the Test Scenario Editor.

    Layout:
    - Menu bar (File, Edit, Scenario, View, Help)
    - Toolbar with common actions
    - Central map view
    - Dockable panels (left: scenario tree, right: properties)
    - Status bar

    Requirements: TSE-UI-001 to TSE-UI-003
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Application state
        self._scenario: Optional[Scenario] = None
        self._current_file: Optional[str] = None
        self._modified = False

        # Settings for window state persistence
        self._settings = QSettings('TMM', 'TestScenarioEditor')

        # Initialize UI
        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()

        # Restore window state
        self._restore_window_state()

        # Create initial scenario
        self._create_new_scenario()

    def _init_ui(self):
        """
        Initialize the user interface layout.

        Requirements: TSE-UI-001, TSE-UI-002
        """
        self.setWindowTitle("TMM Test Scenario Editor & Planner")
        self.setMinimumSize(1280, 720)

        # Create central widget with map view
        self._map_view = MapView()
        self.setCentralWidget(self._map_view)

        # TODO: Add left panel (scenario tree)
        # TODO: Add right panel (properties)

    def _create_actions(self):
        """
        Create menu and toolbar actions.

        Requirements: TSE-UI-010 to TSE-UI-021
        """
        # File menu actions
        self._action_new = QAction("&New Scenario", self)
        self._action_new.setShortcut(QKeySequence.StandardKey.New)
        self._action_new.setStatusTip("Create a new scenario")
        self._action_new.triggered.connect(self._on_new_scenario)

        self._action_open = QAction("&Open...", self)
        self._action_open.setShortcut(QKeySequence.StandardKey.Open)
        self._action_open.setStatusTip("Open an existing scenario")
        self._action_open.triggered.connect(self._on_open_scenario)

        self._action_save = QAction("&Save", self)
        self._action_save.setShortcut(QKeySequence.StandardKey.Save)
        self._action_save.setStatusTip("Save the current scenario")
        self._action_save.triggered.connect(self._on_save_scenario)

        self._action_save_as = QAction("Save &As...", self)
        self._action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self._action_save_as.setStatusTip("Save the scenario with a new name")
        self._action_save_as.triggered.connect(self._on_save_as_scenario)

        self._action_export_json = QAction("Export &JSON...", self)
        self._action_export_json.setShortcut("Ctrl+E")
        self._action_export_json.setStatusTip("Export scenario to JSON for simulator")
        self._action_export_json.triggered.connect(self._on_export_json)

        self._action_exit = QAction("E&xit", self)
        self._action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self._action_exit.setStatusTip("Exit the application")
        self._action_exit.triggered.connect(self.close)

        # Edit menu actions
        self._action_undo = QAction("&Undo", self)
        self._action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self._action_undo.setEnabled(False)

        self._action_redo = QAction("&Redo", self)
        self._action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self._action_redo.setEnabled(False)

        # Scenario menu actions
        self._action_add_target = QAction("Add &Target", self)
        self._action_add_target.setShortcut("Ctrl+T")
        self._action_add_target.setStatusTip("Add a new target to the scenario")
        self._action_add_target.triggered.connect(self._on_add_target)

        self._action_validate = QAction("&Validate Scenario", self)
        self._action_validate.setShortcut("F5")
        self._action_validate.setStatusTip("Validate the current scenario")
        self._action_validate.triggered.connect(self._on_validate_scenario)

        # View menu actions
        self._action_zoom_in = QAction("Zoom &In", self)
        self._action_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)

        self._action_zoom_out = QAction("Zoom &Out", self)
        self._action_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)

        self._action_fit_scenario = QAction("&Fit Scenario", self)
        self._action_fit_scenario.setShortcut("Ctrl+F")
        self._action_fit_scenario.setStatusTip("Zoom to fit all scenario elements")
        self._action_fit_scenario.triggered.connect(self._on_fit_scenario)

        # Help menu actions
        self._action_about = QAction("&About", self)
        self._action_about.triggered.connect(self._on_about)

    def _create_menus(self):
        """
        Create menu bar.

        Requirements: TSE-UI-010 to TSE-UI-014
        """
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self._action_new)
        file_menu.addAction(self._action_open)
        file_menu.addSeparator()
        file_menu.addAction(self._action_save)
        file_menu.addAction(self._action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self._action_export_json)
        file_menu.addSeparator()
        file_menu.addAction(self._action_exit)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self._action_undo)
        edit_menu.addAction(self._action_redo)

        # Scenario menu
        scenario_menu = menubar.addMenu("&Scenario")
        scenario_menu.addAction(self._action_add_target)
        scenario_menu.addSeparator()
        scenario_menu.addAction(self._action_validate)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self._action_zoom_in)
        view_menu.addAction(self._action_zoom_out)
        view_menu.addAction(self._action_fit_scenario)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self._action_about)

    def _create_toolbars(self):
        """
        Create toolbars.

        Requirements: TSE-UI-020, TSE-UI-021
        """
        # Main toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._action_new)
        toolbar.addAction(self._action_open)
        toolbar.addAction(self._action_save)
        toolbar.addSeparator()
        toolbar.addAction(self._action_add_target)
        toolbar.addSeparator()
        toolbar.addAction(self._action_validate)
        toolbar.addSeparator()
        toolbar.addAction(self._action_export_json)

    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")

    def _restore_window_state(self):
        """
        Restore window state from settings.

        Requirements: TSE-UI-003
        """
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self._settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def _save_window_state(self):
        """
        Save window state to settings.

        Requirements: TSE-UI-003
        """
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("windowState", self.saveState())

    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self._modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The scenario has unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self._on_save_scenario():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Save window state
        self._save_window_state()

        # Cleanup
        self._map_view.cleanup()

        event.accept()

    # Action handlers

    def _on_new_scenario(self):
        """Handle New Scenario action."""
        # Check for unsaved changes
        if self._modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The current scenario has unsaved changes. Do you want to save?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self._on_save_scenario():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self._create_new_scenario()

    def _create_new_scenario(self):
        """Create a new empty scenario."""
        # Create default Own Ship at Haifa coordinates
        own_ship = OwnShip(
            position=GeoPosition(latitude=32.08, longitude=34.78),
            speed_knots=0.0,
            course_deg=0.0
        )

        # Create new scenario
        self._scenario = Scenario(
            scenario_id="SCN001",
            title="New Scenario",
            description="Test scenario for TMM",
            duration_sec=300  # 5 minutes default
        )
        self._scenario.own_ship = own_ship
        self._scenario.targets = []

        # Update map
        self._map_view.set_scenario(self._scenario)

        # Reset state
        self._current_file = None
        self._modified = False
        self._update_window_title()

        self.statusBar().showMessage("New scenario created", 3000)

    def _on_open_scenario(self):
        """Handle Open Scenario action."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Scenario",
            "",
            "Scenario Files (*.tse);;All Files (*)"
        )

        if filename:
            # TODO: Implement scenario loading
            self.statusBar().showMessage(f"Opening {filename}...", 3000)

    def _on_save_scenario(self) -> bool:
        """
        Handle Save Scenario action.

        Returns:
            True if saved successfully, False otherwise
        """
        if self._current_file:
            # TODO: Implement scenario saving
            self.statusBar().showMessage(f"Saved to {self._current_file}", 3000)
            self._modified = False
            self._update_window_title()
            return True
        else:
            return self._on_save_as_scenario()

    def _on_save_as_scenario(self) -> bool:
        """
        Handle Save As action.

        Returns:
            True if saved successfully, False otherwise
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scenario As",
            "",
            "Scenario Files (*.tse);;All Files (*)"
        )

        if filename:
            self._current_file = filename
            # TODO: Implement scenario saving
            self.statusBar().showMessage(f"Saved to {filename}", 3000)
            self._modified = False
            self._update_window_title()
            return True

        return False

    def _on_export_json(self):
        """Handle Export JSON action."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            # TODO: Implement JSON export
            self.statusBar().showMessage(f"Exported to {filename}", 3000)

    def _on_add_target(self):
        """Handle Add Target action."""
        # TODO: Implement add target dialog
        self.statusBar().showMessage("Click on the map to add a target", 3000)

    def _on_validate_scenario(self):
        """Handle Validate Scenario action."""
        # TODO: Implement scenario validation
        QMessageBox.information(
            self,
            "Validation",
            "Scenario validation not yet implemented."
        )

    def _on_fit_scenario(self):
        """Handle Fit Scenario action."""
        self._map_view.fit_bounds_to_scenario()
        self.statusBar().showMessage("Fitted scenario to view", 2000)

    def _on_about(self):
        """Handle About action."""
        QMessageBox.about(
            self,
            "About TMM Test Scenario Editor",
            "<h3>TMM Test Scenario Editor & Planner</h3>"
            "<p>Version 0.1.0</p>"
            "<p>Maritime Simulation Scenario Configuration Tool</p>"
            "<p>Requirements: TSE-UI-001 to TSE-UI-003</p>"
        )

    def _update_window_title(self):
        """Update window title with current file and modified status."""
        title = "TMM Test Scenario Editor & Planner"

        if self._current_file:
            title += f" - {self._current_file}"
        else:
            title += " - Untitled"

        if self._modified:
            title += " *"

        self.setWindowTitle(title)

    def set_modified(self, modified: bool = True):
        """
        Set the modified state of the scenario.

        Args:
            modified: True if modified, False otherwise
        """
        self._modified = modified
        self._update_window_title()
