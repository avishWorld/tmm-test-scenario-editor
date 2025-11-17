"""
Interactive map visualization using Folium and Leaflet.js.

Requirements:
- TSE-FUNC-060: Interactive OpenStreetMap visualization
- TSE-FUNC-061: Own Ship marker display
- TSE-FUNC-062: Target markers display
- TSE-FUNC-065: Route visualization
- TSE-INTF-001: OpenStreetMap tile provider
- TSE-PERF-003: Map rendering < 200ms
"""

import os
import tempfile
from typing import Optional, List, Tuple
from PyQt6.QtCore import QUrl, pyqtSignal, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import folium
from folium import plugins

from tse.models.geo import GeoPosition
from tse.models.scenario import Scenario


class MapBridge(QObject):
    """
    Bridge for JavaScript-Python communication.

    Requirements: TSE-FUNC-066, TSE-FUNC-067
    """
    map_clicked = pyqtSignal(float, float)  # lat, lon
    target_clicked = pyqtSignal(str)  # target_id
    marker_dragged = pyqtSignal(str, float, float)  # marker_id, lat, lon


class MapView(QWebEngineView):
    """
    Interactive map visualization widget using Folium/Leaflet.js.

    Features:
    - OpenStreetMap base layer
    - Zoom/pan controls
    - Own Ship marker
    - Target markers
    - Route visualization
    - Range rings
    - Interactive tools

    Requirements: TSE-FUNC-060 to TSE-FUNC-070
    """

    # Signals
    map_clicked = pyqtSignal(float, float)
    target_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the map view."""
        super().__init__(parent)

        # Map state
        self._center: Tuple[float, float] = (32.08, 34.78)  # Default: Haifa area
        self._zoom: int = 12
        self._temp_file: Optional[str] = None

        # Data
        self._scenario: Optional[Scenario] = None
        self._own_ship_marker = None
        self._target_markers = {}
        self._route_lines = {}
        self._range_rings = []

        # Layers visibility
        self._show_own_ship = True
        self._show_targets = True
        self._show_routes = True
        self._show_range_rings = True
        self._show_sensor_coverage = False

        # Communication bridge
        self._bridge = MapBridge()

        # Initialize map
        self._init_map()

    def _init_map(self):
        """
        Initialize the Folium map with OpenStreetMap tiles.

        Requirements:
        - TSE-FUNC-060: OpenStreetMap integration
        - TSE-INTF-001: OpenStreetMap tile provider
        - TSE-UI-030: Zoom/pan controls
        """
        # Create Folium map
        self._map = folium.Map(
            location=self._center,
            zoom_start=self._zoom,
            tiles='OpenStreetMap',
            control_scale=True,  # TSE-UI-031: Scale bar
        )

        # Add fullscreen button
        plugins.Fullscreen().add_to(self._map)

        # Add mouse position plugin (TSE-UI-031: Cursor coordinates)
        plugins.MousePosition(
            position='bottomleft',
            separator=' | ',
            prefix='Position:',
            lat_formatter="function(num) {return L.Util.formatNum(num, 5) + ' °N';}",
            lng_formatter="function(num) {return L.Util.formatNum(num, 5) + ' °E';}"
        ).add_to(self._map)

        # Add measure control
        plugins.MeasureControl(
            position='topleft',
            primary_length_unit='meters',
            secondary_length_unit='kilometers',
            primary_area_unit='sqmeters'
        ).add_to(self._map)

        # Render initial map
        self._render_map()

    def _render_map(self):
        """
        Render the Folium map to HTML and display in QWebEngineView.

        Requirements: TSE-PERF-003 (< 200ms rendering)
        """
        # Save map to temporary HTML file
        if self._temp_file and os.path.exists(self._temp_file):
            os.remove(self._temp_file)

        fd, self._temp_file = tempfile.mkstemp(suffix='.html')
        os.close(fd)

        self._map.save(self._temp_file)

        # Load in QWebEngineView
        self.setUrl(QUrl.fromLocalFile(self._temp_file))

    def set_scenario(self, scenario: Scenario):
        """
        Set the current scenario and update map display.

        Args:
            scenario: Scenario to display
        """
        self._scenario = scenario
        self.refresh()

    def refresh(self):
        """
        Refresh the map with current scenario data.

        Redraws all markers, routes, and overlays.
        """
        if not self._scenario:
            return

        # Clear existing markers
        self._clear_markers()

        # Recreate map (Folium doesn't support dynamic updates well)
        self._init_map()

        # Add Own Ship
        if self._show_own_ship and hasattr(self._scenario, 'own_ship') and self._scenario.own_ship:
            self._add_own_ship_marker()

        # Add Targets
        if self._show_targets and hasattr(self._scenario, 'targets'):
            for target in self._scenario.targets:
                self._add_target_marker(target)

        # Add Routes
        if self._show_routes and hasattr(self._scenario, 'targets'):
            for target in self._scenario.targets:
                if hasattr(target, 'route') and target.route:
                    self._add_route_line(target)

        # Add Range Rings
        if self._show_range_rings and hasattr(self._scenario, 'own_ship') and self._scenario.own_ship:
            self._add_range_rings()

        # Render updated map
        self._render_map()

    def _clear_markers(self):
        """Clear all markers from the map."""
        self._own_ship_marker = None
        self._target_markers.clear()
        self._route_lines.clear()
        self._range_rings.clear()

    def _add_own_ship_marker(self):
        """
        Add Own Ship marker to the map.

        Requirements: TSE-FUNC-061
        """
        if not self._scenario or not hasattr(self._scenario, 'own_ship'):
            return

        own_ship = self._scenario.own_ship
        if not own_ship or not own_ship.position:
            return

        # Create Own Ship marker (blue triangle icon)
        folium.Marker(
            location=[own_ship.position.latitude, own_ship.position.longitude],
            popup=f"<b>Own Ship</b><br>Speed: {own_ship.speed_knots} kts<br>Course: {own_ship.course_deg}°",
            tooltip="Own Ship",
            icon=folium.Icon(color='blue', icon='ship', prefix='fa')
        ).add_to(self._map)

        # Add heading line
        self._add_heading_line(
            own_ship.position.latitude,
            own_ship.position.longitude,
            own_ship.course_deg,
            color='blue'
        )

    def _add_target_marker(self, target):
        """
        Add target marker to the map.

        Args:
            target: Target object to display

        Requirements: TSE-FUNC-062
        """
        if not target.position:
            return

        # Determine marker color based on vessel type
        color_map = {
            'Small_Boat': 'green',
            'Medium_Cargo': 'orange',
            'Large_Cargo': 'red',
            'Tanker': 'darkred',
            'Navigation_Buoy': 'gray',
            'Custom': 'purple'
        }

        vessel_type_str = target.vessel_type.value if hasattr(target.vessel_type, 'value') else str(target.vessel_type)
        color = color_map.get(vessel_type_str, 'gray')

        # Create popup with target info
        popup_html = f"""
        <b>{target.name}</b><br>
        ID: {target.target_id}<br>
        Type: {vessel_type_str}<br>
        Speed: {target.speed_knots} kts<br>
        Course: {target.course_deg}°<br>
        Range: {target.relative_range_m:.0f} m<br>
        Bearing: {target.relative_bearing_deg:.1f}°
        """

        # Create marker
        folium.Marker(
            location=[target.position.latitude, target.position.longitude],
            popup=popup_html,
            tooltip=f"{target.name} ({target.target_id})",
            icon=folium.Icon(color=color, icon='ship', prefix='fa')
        ).add_to(self._map)

        # Add heading line if moving
        if target.speed_knots > 0:
            self._add_heading_line(
                target.position.latitude,
                target.position.longitude,
                target.course_deg,
                color=color
            )

    def _add_route_line(self, target):
        """
        Add route line for target waypoints.

        Args:
            target: Target with route waypoints

        Requirements: TSE-FUNC-065
        """
        if not hasattr(target, 'route') or not target.route or len(target.route) < 2:
            return

        # Extract waypoint coordinates
        waypoints = []
        for wp in target.route:
            if wp.position:
                waypoints.append([wp.position.latitude, wp.position.longitude])

        if len(waypoints) < 2:
            return

        # Create polyline
        folium.PolyLine(
            locations=waypoints,
            color='darkblue',
            weight=2,
            opacity=0.7,
            popup=f"Route: {target.name}"
        ).add_to(self._map)

        # Add waypoint markers
        for i, wp in enumerate(target.route):
            if wp.position:
                folium.CircleMarker(
                    location=[wp.position.latitude, wp.position.longitude],
                    radius=5,
                    popup=f"WP{i+1}: {wp.time_sec}s",
                    color='navy',
                    fill=True,
                    fillColor='lightblue'
                ).add_to(self._map)

    def _add_heading_line(self, lat: float, lon: float, course_deg: float,
                          color: str = 'blue', length_m: float = 500):
        """
        Add a heading line showing vessel direction.

        Args:
            lat: Vessel latitude
            lon: Vessel longitude
            course_deg: Vessel course in degrees
            color: Line color
            length_m: Line length in meters
        """
        from tse.utils.geo_calc import destination_point

        # Calculate endpoint
        end_lat, end_lon = destination_point(lat, lon, length_m, course_deg)

        # Draw line
        folium.PolyLine(
            locations=[[lat, lon], [end_lat, end_lon]],
            color=color,
            weight=3,
            opacity=0.8
        ).add_to(self._map)

        # Add arrowhead
        folium.RegularPolygonMarker(
            location=[end_lat, end_lon],
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            color=color,
            number_of_sides=3,
            radius=8,
            rotation=course_deg
        ).add_to(self._map)

    def _add_range_rings(self, ranges_nm: List[float] = [2, 5, 10]):
        """
        Add range rings around Own Ship.

        Args:
            ranges_nm: List of ranges in nautical miles

        Requirements: TSE-FUNC-063
        """
        if not self._scenario or not hasattr(self._scenario, 'own_ship'):
            return

        own_ship = self._scenario.own_ship
        if not own_ship or not own_ship.position:
            return

        # Convert NM to meters (1 NM = 1852 m)
        for range_nm in ranges_nm:
            range_m = range_nm * 1852

            folium.Circle(
                location=[own_ship.position.latitude, own_ship.position.longitude],
                radius=range_m,
                color='blue',
                fill=False,
                weight=1,
                opacity=0.3,
                popup=f"{range_nm} NM"
            ).add_to(self._map)

    def set_center(self, lat: float, lon: float):
        """Set map center position."""
        self._center = (lat, lon)
        self._map.location = self._center
        self._render_map()

    def set_zoom(self, zoom: int):
        """Set map zoom level."""
        self._zoom = zoom
        self._map.zoom_start = self._zoom
        self._render_map()

    def toggle_layer(self, layer_name: str, visible: bool):
        """
        Toggle visibility of map layers.

        Args:
            layer_name: Layer name ('own_ship', 'targets', 'routes', 'range_rings')
            visible: Show or hide

        Requirements: TSE-FUNC-069, TSE-UI-033
        """
        if layer_name == 'own_ship':
            self._show_own_ship = visible
        elif layer_name == 'targets':
            self._show_targets = visible
        elif layer_name == 'routes':
            self._show_routes = visible
        elif layer_name == 'range_rings':
            self._show_range_rings = visible
        elif layer_name == 'sensor_coverage':
            self._show_sensor_coverage = visible

        self.refresh()

    def fit_bounds_to_scenario(self):
        """
        Adjust map zoom to fit all scenario elements.

        Requirements: TSE-UI-030
        """
        if not self._scenario:
            return

        # Collect all positions
        positions = []

        if hasattr(self._scenario, 'own_ship') and self._scenario.own_ship and self._scenario.own_ship.position:
            positions.append([
                self._scenario.own_ship.position.latitude,
                self._scenario.own_ship.position.longitude
            ])

        if hasattr(self._scenario, 'targets'):
            for target in self._scenario.targets:
                if target.position:
                    positions.append([target.position.latitude, target.position.longitude])

        if len(positions) > 0:
            # Fit bounds
            self._map.fit_bounds(positions)
            self._render_map()

    def cleanup(self):
        """Clean up temporary files."""
        if self._temp_file and os.path.exists(self._temp_file):
            os.remove(self._temp_file)
