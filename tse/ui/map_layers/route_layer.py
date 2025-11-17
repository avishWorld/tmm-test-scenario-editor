"""
Route layer for visualizing target routes and waypoints.

Requirements:
- TSE-FUNC-065: Route visualization with waypoint markers
- TSE-FUNC-042: Waypoint display on map
"""

import folium
from typing import List, Dict

from tse.models.target import Target


class RouteLayer:
    """
    Renders target routes and waypoints on the map.

    Features:
    - Route polylines connecting waypoints
    - Waypoint markers with time labels
    - Distance/time information
    - Visual distinction between targets

    Requirements: TSE-FUNC-065
    """

    # Colors for different target routes
    ROUTE_COLORS = [
        'darkblue', 'darkgreen', 'darkred', 'purple',
        'darkorange', 'brown', 'pink', 'gray'
    ]

    def __init__(self):
        """Initialize Route layer."""
        self._targets: List[Target] = []
        self._route_lines: Dict[str, folium.PolyLine] = {}
        self._color_index = 0

    def set_targets(self, targets: List[Target]):
        """
        Set the targets whose routes to display.

        Args:
            targets: List of Target objects with routes
        """
        self._targets = targets
        self._route_lines.clear()
        self._color_index = 0

    def render(self, folium_map: folium.Map):
        """
        Render all target routes on the map.

        Args:
            folium_map: Folium map object to render on
        """
        for target in self._targets:
            if hasattr(target, 'route') and target.route and len(target.route) > 0:
                self._render_route(folium_map, target)

    def _render_route(self, folium_map: folium.Map, target: Target):
        """
        Render a single target's route.

        Args:
            folium_map: Map to render on
            target: Target with route to render
        """
        if not hasattr(target, 'route') or not target.route:
            return

        # Get color for this route
        color = self._get_next_color()

        # Collect waypoint positions
        waypoints = []
        for wp in target.route:
            if wp.position:
                waypoints.append([wp.position.latitude, wp.position.longitude])

        if len(waypoints) < 2:
            return

        # Create route polyline
        route_line = folium.PolyLine(
            locations=waypoints,
            color=color,
            weight=3,
            opacity=0.7,
            popup=f"<b>Route: {target.name}</b><br>Waypoints: {len(waypoints)}"
        )
        route_line.add_to(folium_map)
        self._route_lines[target.target_id] = route_line

        # Add waypoint markers
        for i, wp in enumerate(target.route):
            if wp.position:
                self._add_waypoint_marker(
                    folium_map,
                    wp,
                    i + 1,
                    target.name,
                    color
                )

    def _add_waypoint_marker(self, folium_map: folium.Map, waypoint,
                             wp_number: int, target_name: str, color: str):
        """
        Add a waypoint marker to the map.

        Args:
            folium_map: Map to add marker to
            waypoint: Waypoint object
            wp_number: Waypoint sequence number
            target_name: Name of parent target
            color: Marker color
        """
        lat = waypoint.position.latitude
        lon = waypoint.position.longitude

        # Create popup with waypoint details
        popup_html = f"""
        <div style="font-family: Arial;">
            <h4 style="margin: 0 0 10px 0;">Waypoint {wp_number}</h4>
            <table>
                <tr>
                    <td><b>Target:</b></td>
                    <td>{target_name}</td>
                </tr>
                <tr>
                    <td><b>Time:</b></td>
                    <td>{waypoint.time_sec} seconds</td>
                </tr>
                <tr>
                    <td><b>Position:</b></td>
                    <td>{lat:.5f}°N, {lon:.5f}°E</td>
                </tr>
                <tr>
                    <td><b>Speed:</b></td>
                    <td>{waypoint.speed_knots:.1f} knots</td>
                </tr>
                <tr>
                    <td><b>Course:</b></td>
                    <td>{waypoint.course_deg:.1f}°</td>
                </tr>
            </table>
        </div>
        """

        # Create waypoint marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"<b>WP{wp_number}</b><br>{waypoint.time_sec}s",
            color=color,
            fill=True,
            fillColor='white',
            fillOpacity=0.9,
            weight=3
        ).add_to(folium_map)

        # Add label with waypoint number
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 10px; font-weight: bold; color: {color};">WP{wp_number}</div>'
            )
        ).add_to(folium_map)

    def _get_next_color(self) -> str:
        """
        Get next color for route visualization.

        Returns:
            Color string
        """
        color = self.ROUTE_COLORS[self._color_index % len(self.ROUTE_COLORS)]
        self._color_index += 1
        return color

    def clear(self):
        """Clear all route lines."""
        self._targets.clear()
        self._route_lines.clear()
        self._color_index = 0
