"""
Map View component for displaying scenarios on an interactive map.

This module provides the MapView widget which integrates Folium/Leaflet.js
within a QWebEngineView to display an interactive OpenStreetMap-based map
with scenario elements (Own Ship, Targets, Routes).

Requirements:
- PHASE 3: Map Visualization
- Task 3.1.1: MapView widget creation
- Task 3.1.2: Folium/Leaflet.js integration
- Task 3.1.3: OpenStreetMap tile provider
"""

import os
import tempfile
from typing import Optional
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import folium
from folium import Icon, Marker, Circle

from ..models.scenario import Scenario
from ..models.own_ship import OwnShip
from ..models.target import Target
from ..models.geo import GeoPosition


class MapView(QWidget):
    """
    Interactive map view widget for displaying maritime scenarios.

    This widget uses Folium to generate an interactive Leaflet.js map
    and embeds it in a QWebEngineView. It displays:
    - Own Ship position and heading
    - Target vessels with their positions
    - Routes and waypoints
    - Range rings and sensor coverage (future)

    Signals:
        map_clicked: Emitted when user clicks on the map (lat, lon)
    """

    map_clicked = pyqtSignal(float, float)  # latitude, longitude

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the MapView widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view for displaying the map
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Map parameters
        self.default_center = (32.0, 34.8)  # Mediterranean (Israel coast)
        self.default_zoom = 10

        # Temporary file for map HTML
        self.temp_map_file = None

        # Current scenario reference
        self.scenario: Optional[Scenario] = None

        # Initialize with empty map
        self.create_empty_map()

    def create_empty_map(self):
        """Create and display an empty map centered at default location."""
        # Create Folium map
        m = folium.Map(
            location=self.default_center,
            zoom_start=self.default_zoom,
            tiles="OpenStreetMap",
            control_scale=True
        )

        # Add attribution
        folium.map.LayerControl().add_to(m)

        # Render to HTML and display
        self._render_map(m)

    def update_from_scenario(self, scenario: Optional[Scenario]):
        """
        Update the map to display the given scenario.

        Args:
            scenario: Scenario object to display, or None for empty map
        """
        self.scenario = scenario

        if scenario is None:
            self.create_empty_map()
            return

        # Determine map center
        center = self._calculate_map_center(scenario)

        # Create Folium map
        m = folium.Map(
            location=center,
            zoom_start=self.default_zoom,
            tiles="OpenStreetMap",
            control_scale=True
        )

        # Add Own Ship if present
        if scenario.own_ship and scenario.own_ship.position:
            self._add_own_ship_marker(m, scenario.own_ship)

        # Add all targets
        for target in scenario.targets:
            if target.position:
                self._add_target_marker(m, target)

        # Add layer control
        folium.map.LayerControl().add_to(m)

        # Render to HTML and display
        self._render_map(m)

    def _calculate_map_center(self, scenario: Scenario) -> tuple[float, float]:
        """
        Calculate the center point for the map based on scenario elements.

        Args:
            scenario: Scenario to analyze

        Returns:
            Tuple of (latitude, longitude) for map center
        """
        # If Own Ship exists, center on it
        if scenario.own_ship and scenario.own_ship.position:
            return (
                scenario.own_ship.position.latitude_deg,
                scenario.own_ship.position.longitude_deg
            )

        # If targets exist, center on first target
        if scenario.targets and scenario.targets[0].position:
            return (
                scenario.targets[0].position.latitude_deg,
                scenario.targets[0].position.longitude_deg
            )

        # Otherwise use default center
        return self.default_center

    def _add_own_ship_marker(self, map_obj: folium.Map, own_ship: OwnShip):
        """
        Add Own Ship marker to the map.

        Args:
            map_obj: Folium map object
            own_ship: Own Ship to display
        """
        if not own_ship.position:
            return

        lat = own_ship.position.latitude_deg
        lon = own_ship.position.longitude_deg

        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">🚢 Own Ship</h4>
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>Position:</b></td><td>{lat:.6f}, {lon:.6f}</td></tr>
                <tr><td><b>Speed:</b></td><td>{own_ship.speed_knots:.1f} knots</td></tr>
                <tr><td><b>Course:</b></td><td>{own_ship.course_deg:.1f}°</td></tr>
            </table>
        </div>
        """

        # Add marker with blue color (Own Ship)
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="Own Ship",
            icon=folium.Icon(color='blue', icon='ship', prefix='fa')
        ).add_to(map_obj)

        # Add heading indicator (small line showing course)
        if own_ship.speed_knots > 0:
            # TODO: Add course line using folium.PolyLine
            pass

    def _add_target_marker(self, map_obj: folium.Map, target: Target):
        """
        Add Target marker to the map.

        Args:
            map_obj: Folium map object
            target: Target to display
        """
        if not target.position:
            return

        lat = target.position.latitude_deg
        lon = target.position.longitude_deg

        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #c0392b;">🎯 {target.name or target.target_id}</h4>
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>ID:</b></td><td>{target.target_id}</td></tr>
                <tr><td><b>Position:</b></td><td>{lat:.6f}, {lon:.6f}</td></tr>
                <tr><td><b>Speed:</b></td><td>{target.speed_knots:.1f} knots</td></tr>
                <tr><td><b>Course:</b></td><td>{target.course_deg:.1f}°</td></tr>
                <tr><td><b>Type:</b></td><td>{target.vessel_type.value}</td></tr>
                <tr><td><b>MMSI:</b></td><td>{target.mmsi}</td></tr>
            </table>
        </div>
        """

        # Add marker with red color (Target)
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{target.name or target.target_id}",
            icon=folium.Icon(color='red', icon='bullseye', prefix='fa')
        ).add_to(map_obj)

        # Add heading indicator (small line showing course)
        if target.speed_knots > 0:
            # TODO: Add course line using folium.PolyLine
            pass

    def _render_map(self, map_obj: folium.Map):
        """
        Render Folium map to HTML and display in web view.

        Args:
            map_obj: Folium map object to render
        """
        # Clean up old temporary file
        if self.temp_map_file and os.path.exists(self.temp_map_file):
            try:
                os.remove(self.temp_map_file)
            except:
                pass

        # Create new temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            encoding='utf-8'
        ) as f:
            # Save map to HTML
            map_obj.save(f.name)
            self.temp_map_file = f.name

        # Load HTML in web view
        self.web_view.setUrl(QUrl.fromLocalFile(self.temp_map_file))

    def set_center(self, lat: float, lon: float, zoom: Optional[int] = None):
        """
        Set the map center and zoom level.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level (optional, uses default if not provided)
        """
        self.default_center = (lat, lon)
        if zoom is not None:
            self.default_zoom = zoom

        # Refresh the map
        self.update_from_scenario(self.scenario)

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_map_file and os.path.exists(self.temp_map_file):
            try:
                os.remove(self.temp_map_file)
            except:
                pass
