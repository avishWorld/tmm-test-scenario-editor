"""
Main entry point for the TMM Test Scenario Editor & Planner application.

Requirements:
- TSE-PERF-001: Startup time < 5 seconds
"""

import sys
from PyQt6.QtWidgets import QApplication


def main():
    """
    Application entry point.

    Initializes the Qt application and displays the main window.

    Performance Target: Startup time < 5 seconds (TSE-PERF-001)
    """
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TMM Test Scenario Editor & Planner")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("TMM")
    app.setOrganizationDomain("tse.example.com")

    # Create and show main window
    from tse.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
