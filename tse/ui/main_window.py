"""
Main application window for TSE.

Requirements:
- TSE-UI-001: Main window with menu bar, toolbar, and panels
- TSE-UI-002: Resizable layout panels
- TSE-UI-003: Window state persistence (size, position, layout)
- TSE-UI-010 to TSE-UI-014: Menu system
- TSE-UI-020 to TSE-UI-021: Toolbar
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QMenuBar,
    QToolBar,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QDialog,
)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from pathlib import Path
from typing import Optional

from ..models import Scenario, GeoPosition, OwnShip
from ..io import save_project, load_project, export_to_json, get_project_metadata
from ..validation import validate_scenario
from .dialogs import ScenarioPropertiesDialog, OwnShipConfigDialog


class MainWindow(QMainWindow):
    """
    Main application window for TSE.

    Provides the main UI framework with menu bar, toolbar, status bar,
    and resizable panel layout.

    Requirements: TSE-UI-001, TSE-UI-002, TSE-UI-003
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Current scenario
        self.current_scenario: Optional[Scenario] = None
        self.current_file_path: Optional[str] = None
        self.is_modified = False

        # Settings for persistence
        self.settings = QSettings("TMM", "TSE")

        # Setup UI
        self._init_ui()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._restore_window_state()

        # Create a new scenario by default
        self._new_scenario()

    def _init_ui(self):
        """Initialize the user interface layout."""
        self.setWindowTitle("TMM Test Scenario Editor & Planner")
        self.setMinimumSize(1024, 768)

        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels (TSE-UI-002)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Scenario tree/list
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.addWidget(QLabel("Scenario Explorer"))
        self.scenario_info = QTextEdit()
        self.scenario_info.setReadOnly(True)
        left_layout.addWidget(self.scenario_info)

        # Center panel - Map view (placeholder for Phase 3)
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)
        center_label = QLabel("Map View\n(Phase 3 - Map Visualization)")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 20px; }")
        center_layout.addWidget(center_label)

        # Right panel - Properties/Details
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.addWidget(QLabel("Properties"))
        self.properties_info = QTextEdit()
        self.properties_info.setReadOnly(True)
        right_layout.addWidget(self.properties_info)

        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)

        # Set initial splitter sizes (20% - 60% - 20%)
        self.main_splitter.setSizes([200, 600, 200])

        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)

    def _create_menus(self):
        """Create menu bar with all menus."""
        menubar = self.menuBar()

        # File Menu (TSE-UI-010)
        file_menu = menubar.addMenu("&File")

        self.action_new = QAction("&New Scenario", self)
        self.action_new.setShortcut(QKeySequence.StandardKey.New)
        self.action_new.setStatusTip("Create a new scenario")
        self.action_new.triggered.connect(self._new_scenario)
        file_menu.addAction(self.action_new)

        self.action_open = QAction("&Open...", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.setStatusTip("Open an existing scenario")
        self.action_open.triggered.connect(self._open_scenario)
        file_menu.addAction(self.action_open)

        self.action_save = QAction("&Save", self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.setStatusTip("Save the current scenario")
        self.action_save.triggered.connect(self._save_scenario)
        file_menu.addAction(self.action_save)

        self.action_save_as = QAction("Save &As...", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.setStatusTip("Save the scenario to a new file")
        self.action_save_as.triggered.connect(self._save_scenario_as)
        file_menu.addAction(self.action_save_as)

        file_menu.addSeparator()

        self.action_export_json = QAction("&Export to JSON...", self)
        self.action_export_json.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export_json.setStatusTip("Export scenario to simulator JSON format")
        self.action_export_json.triggered.connect(self._export_json)
        file_menu.addAction(self.action_export_json)

        file_menu.addSeparator()

        self.action_exit = QAction("E&xit", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.setStatusTip("Exit the application")
        self.action_exit.triggered.connect(self.close)
        file_menu.addAction(self.action_exit)

        # Edit Menu (TSE-UI-011)
        edit_menu = menubar.addMenu("&Edit")

        self.action_undo = QAction("&Undo", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.setEnabled(False)  # TODO: Implement undo/redo in Phase 7
        edit_menu.addAction(self.action_undo)

        self.action_redo = QAction("&Redo", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.setEnabled(False)  # TODO: Implement undo/redo in Phase 7
        edit_menu.addAction(self.action_redo)

        # Scenario Menu (TSE-UI-012)
        scenario_menu = menubar.addMenu("&Scenario")

        self.action_scenario_properties = QAction("&Properties...", self)
        self.action_scenario_properties.setShortcut(QKeySequence("Ctrl+P"))
        self.action_scenario_properties.setStatusTip("Edit scenario properties")
        self.action_scenario_properties.triggered.connect(self._edit_scenario_properties)
        scenario_menu.addAction(self.action_scenario_properties)

        self.action_own_ship = QAction("&Own Ship...", self)
        self.action_own_ship.setStatusTip("Configure Own Ship")
        self.action_own_ship.triggered.connect(self._edit_own_ship)
        scenario_menu.addAction(self.action_own_ship)

        scenario_menu.addSeparator()

        self.action_add_target = QAction("Add &Target...", self)
        self.action_add_target.setShortcut(QKeySequence("Ctrl+T"))
        self.action_add_target.setStatusTip("Add a new target")
        self.action_add_target.triggered.connect(self._add_target)
        scenario_menu.addAction(self.action_add_target)

        scenario_menu.addSeparator()

        self.action_validate = QAction("&Validate Scenario", self)
        self.action_validate.setShortcut(QKeySequence("F5"))
        self.action_validate.setStatusTip("Validate the current scenario")
        self.action_validate.triggered.connect(self._validate_scenario)
        scenario_menu.addAction(self.action_validate)

        # View Menu (TSE-UI-013)
        view_menu = menubar.addMenu("&View")

        self.action_show_left_panel = QAction("Scenario &Explorer", self)
        self.action_show_left_panel.setCheckable(True)
        self.action_show_left_panel.setChecked(True)
        self.action_show_left_panel.triggered.connect(self._toggle_left_panel)
        view_menu.addAction(self.action_show_left_panel)

        self.action_show_right_panel = QAction("&Properties Panel", self)
        self.action_show_right_panel.setCheckable(True)
        self.action_show_right_panel.setChecked(True)
        self.action_show_right_panel.triggered.connect(self._toggle_right_panel)
        view_menu.addAction(self.action_show_right_panel)

        view_menu.addSeparator()

        self.action_reset_layout = QAction("&Reset Layout", self)
        self.action_reset_layout.setStatusTip("Reset panel layout to default")
        self.action_reset_layout.triggered.connect(self._reset_layout)
        view_menu.addAction(self.action_reset_layout)

        # Help Menu (TSE-UI-014)
        help_menu = menubar.addMenu("&Help")

        self.action_about = QAction("&About...", self)
        self.action_about.setStatusTip("About TSE")
        self.action_about.triggered.connect(self._show_about)
        help_menu.addAction(self.action_about)

    def _create_toolbar(self):
        """Create toolbar with common actions (TSE-UI-020, TSE-UI-021)."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)

        # Add common actions to toolbar
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        toolbar.addAction(self.action_add_target)
        toolbar.addSeparator()
        toolbar.addAction(self.action_validate)
        toolbar.addAction(self.action_export_json)

    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")

    def _restore_window_state(self):
        """Restore window state from settings (TSE-UI-003)."""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Restore window state (toolbars, docks, etc.)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

        # Restore splitter sizes
        splitter_sizes = self.settings.value("splitterSizes")
        if splitter_sizes:
            self.main_splitter.restoreSizes(splitter_sizes)

    def _save_window_state(self):
        """Save window state to settings (TSE-UI-003)."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("splitterSizes", self.main_splitter.saveState())

    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "The scenario has unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self._save_scenario()
                if self.is_modified:  # Save was cancelled
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Save window state before closing
        self._save_window_state()
        event.accept()

    def _new_scenario(self):
        """Create a new scenario."""
        # Check for unsaved changes
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save the current scenario?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self._save_scenario()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        # Create default scenario
        self.current_scenario = Scenario(
            scenario_id="NEW001",
            title="New Scenario",
            description="",
            duration_sec=300
        )
        self.current_file_path = None
        self.is_modified = False
        self._update_ui()
        self.statusBar().showMessage("New scenario created")

    def _open_scenario(self):
        """Open an existing scenario."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Scenario",
            "",
            "TSE Project Files (*.tse);;All Files (*)"
        )

        if file_path:
            try:
                self.current_scenario = load_project(file_path)
                self.current_file_path = file_path
                self.is_modified = False
                self._update_ui()
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def _save_scenario(self):
        """Save the current scenario."""
        if self.current_file_path:
            try:
                save_project(self.current_scenario, self.current_file_path)
                self.is_modified = False
                self.statusBar().showMessage(f"Saved: {self.current_file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
        else:
            self._save_scenario_as()

    def _save_scenario_as(self):
        """Save the scenario to a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scenario As",
            "",
            "TSE Project Files (*.tse);;All Files (*)"
        )

        if file_path:
            try:
                save_project(self.current_scenario, file_path)
                self.current_file_path = file_path
                self.is_modified = False
                self.statusBar().showMessage(f"Saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def _export_json(self):
        """Export scenario to JSON."""
        if not self.current_scenario:
            QMessageBox.warning(self, "Warning", "No scenario to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                export_to_json(self.current_scenario, file_path)
                self.statusBar().showMessage(f"Exported: {file_path}")
                QMessageBox.information(self, "Success", "Scenario exported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    def _edit_scenario_properties(self):
        """Edit scenario properties."""
        if not self.current_scenario:
            QMessageBox.warning(self, "Warning", "No scenario to edit")
            return

        dialog = ScenarioPropertiesDialog(self.current_scenario, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update scenario with dialog values
            self.current_scenario = dialog.get_scenario()
            self.is_modified = True
            self._update_ui()
            self.statusBar().showMessage("Scenario properties updated")

    def _edit_own_ship(self):
        """Edit Own Ship configuration."""
        if not self.current_scenario:
            QMessageBox.warning(self, "Warning", "No scenario to configure")
            return

        dialog = OwnShipConfigDialog(self.current_scenario.own_ship, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update Own Ship with dialog values
            self.current_scenario.own_ship = dialog.get_own_ship()
            self.is_modified = True
            self._update_ui()
            self.statusBar().showMessage("Own Ship configuration updated")

    def _add_target(self):
        """Add a new target."""
        QMessageBox.information(self, "TODO", "Add Target dialog - Phase 2.3")

    def _validate_scenario(self):
        """Validate the current scenario."""
        if not self.current_scenario:
            QMessageBox.warning(self, "Warning", "No scenario to validate")
            return

        report = validate_scenario(self.current_scenario)

        if report.has_errors:
            msg = f"Validation FAILED\n\nErrors: {report.error_count}\nWarnings: {report.warning_count}\n\n"
            for message in report.messages[:10]:  # Show first 10
                msg += f"[{message.severity.value}] {message.location}: {message.message}\n"
            QMessageBox.critical(self, "Validation Failed", msg)
        else:
            msg = f"Validation PASSED\n\nWarnings: {report.warning_count}\n"
            if report.warning_count > 0:
                for message in report.messages[:10]:
                    msg += f"[{message.severity.value}] {message.location}: {message.message}\n"
            QMessageBox.information(self, "Validation Passed", msg)

    def _toggle_left_panel(self):
        """Toggle left panel visibility."""
        self.left_panel.setVisible(self.action_show_left_panel.isChecked())

    def _toggle_right_panel(self):
        """Toggle right panel visibility."""
        self.right_panel.setVisible(self.action_show_right_panel.isChecked())

    def _reset_layout(self):
        """Reset panel layout to default."""
        self.main_splitter.setSizes([200, 600, 200])
        self.left_panel.setVisible(True)
        self.right_panel.setVisible(True)
        self.action_show_left_panel.setChecked(True)
        self.action_show_right_panel.setChecked(True)

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About TSE",
            "<h2>TMM Test Scenario Editor & Planner</h2>"
            "<p>Version 0.1.0 (Pre-Alpha)</p>"
            "<p>A desktop application for creating, visualizing, and exporting "
            "maritime test scenarios for the Track Management Module (TMM) of a "
            "Collision Detection & Avoidance (CDA) Naval System.</p>"
            "<p>Phase 1 (Foundation & Infrastructure) complete.</p>"
            "<p>© 2025 TMM Project</p>"
        )

    def _update_ui(self):
        """Update UI to reflect current scenario state."""
        if self.current_scenario:
            # Update window title
            title = f"TSE - {self.current_scenario.title}"
            if self.is_modified:
                title += " *"
            if self.current_file_path:
                title += f" [{Path(self.current_file_path).name}]"
            self.setWindowTitle(title)

            # Update scenario info panel
            info = f"<h3>{self.current_scenario.title}</h3>"
            info += f"<p><b>ID:</b> {self.current_scenario.scenario_id}</p>"
            info += f"<p><b>Duration:</b> {self.current_scenario.duration_sec}s</p>"
            info += f"<p><b>Description:</b><br/>{self.current_scenario.description or 'None'}</p>"
            if self.current_scenario.own_ship:
                info += f"<p><b>Own Ship:</b> Configured</p>"
            else:
                info += f"<p><b>Own Ship:</b> Not configured</p>"
            info += f"<p><b>Targets:</b> {len(self.current_scenario.targets)}</p>"
            self.scenario_info.setHtml(info)

            # Update properties panel
            props = "<h4>Quick Stats</h4>"
            if self.current_scenario.own_ship:
                props += f"<p><b>Own Ship Position:</b><br/>"
                props += f"Lat: {self.current_scenario.own_ship.position.latitude_deg:.4f}°<br/>"
                props += f"Lon: {self.current_scenario.own_ship.position.longitude_deg:.4f}°</p>"
            props += f"<p><b>Target Count:</b> {len(self.current_scenario.targets)}</p>"

            # Count waypoints and dropouts
            total_waypoints = sum(len(t.route) for t in self.current_scenario.targets)
            total_dropouts = sum(len(t.dropouts) for t in self.current_scenario.targets)
            props += f"<p><b>Total Waypoints:</b> {total_waypoints}</p>"
            props += f"<p><b>Total Dropouts:</b> {total_dropouts}</p>"

            self.properties_info.setHtml(props)
