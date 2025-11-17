"""
Target layer for map visualization.

Requirements:
- TSE-FUNC-062: Display targets on map
- TSE-UI-032: Hover tooltips for targets
- TSE-FUNC-026: Visual distinction by vessel type
"""

import folium
from typing import List, Dict

from tse.models.target import Target, VesselType
from tse.utils.geo_calc import destination_point


class TargetLayer:
    """
    Renders target markers and associated elements on the map.

    Features:
    - Color-coded markers by vessel type
    - Heading indicator for moving targets
    - Hover tooltips
    - Detailed popups with target information

    Requirements: TSE-FUNC-062, TSE-UI-032
    """

    # Color mapping for vessel types
    VESSEL_COLORS = {
        VesselType.SMALL_BOAT: 'green',
        VesselType.MEDIUM_CARGO: 'orange',
        VesselType.LARGE_CARGO: 'red',
        VesselType.TANKER: 'darkred',
        VesselType.NAVIGATION_BUOY: 'gray',
        VesselType.CUSTOM: 'purple'
    }

    def __init__(self):
        """Initialize Target layer."""
        self._targets: List[Target] = []
        self._markers: Dict[str, folium.Marker] = {}

    def set_targets(self, targets: List[Target]):
        """
        Set the targets to display.

        Args:
            targets: List of Target objects
        """
        self._targets = targets
        self._markers.clear()

    def render(self, folium_map: folium.Map):
        """
        Render all targets on the map.

        Args:
            folium_map: Folium map object to render on
        """
        for target in self._targets:
            if target.position:
                self._render_target(folium_map, target)

    def _render_target(self, folium_map: folium.Map, target: Target):
        """
        Render a single target on the map.

        Args:
            folium_map: Map to render on
            target: Target to render
        """
        lat = target.position.latitude
        lon = target.position.longitude

        # Get marker color based on vessel type
        color = self.VESSEL_COLORS.get(target.vessel_type, 'gray')

        # Create detailed popup
        popup_html = self._create_popup_html(target)

        # Create tooltip (hover text)
        tooltip_text = f"<b>{target.name}</b><br>ID: {target.target_id}<br>Type: {target.vessel_type.value}"

        # Create target marker
        marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=tooltip_text,
            icon=folium.Icon(
                color=color,
                icon='ship',
                prefix='fa'
            )
        )
        marker.add_to(folium_map)
        self._markers[target.target_id] = marker

        # Add heading line if target is moving
        if target.speed_knots > 0:
            self._add_heading_line(
                folium_map,
                lat, lon,
                target.course_deg,
                color=color,
                length_m=500
            )

        # Add circle showing detection range
        folium.Circle(
            location=[lat, lon],
            radius=50,  # 50m detection radius
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.1,
            weight=1,
            opacity=0.3
        ).add_to(folium_map)

    def _create_popup_html(self, target: Target) -> str:
        """
        Create HTML content for target popup.

        Args:
            target: Target object

        Returns:
            HTML string for popup
        """
        # Get vessel type string
        vessel_type_str = target.vessel_type.value if hasattr(target.vessel_type, 'value') else str(target.vessel_type)

        # Get AIS class string
        ais_class_str = target.ais_class.value if hasattr(target.ais_class, 'value') else str(target.ais_class)

        popup_html = f"""
        <div style="font-family: Arial; min-width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #cc6600;">{target.name}</h4>
            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td><b>Target ID:</b></td>
                    <td>{target.target_id}</td>
                </tr>
                <tr>
                    <td><b>Vessel Type:</b></td>
                    <td>{vessel_type_str}</td>
                </tr>
                <tr>
                    <td><b>Position:</b></td>
                    <td>{target.position.latitude:.5f}°N<br>{target.position.longitude:.5f}°E</td>
                </tr>
                <tr>
                    <td><b>Speed:</b></td>
                    <td>{target.speed_knots:.1f} knots</td>
                </tr>
                <tr>
                    <td><b>Course:</b></td>
                    <td>{target.course_deg:.1f}°</td>
                </tr>
                <tr>
                    <td><b>Range from Own Ship:</b></td>
                    <td>{target.relative_range_m:.0f} m ({target.relative_range_m/1852:.2f} NM)</td>
                </tr>
                <tr>
                    <td><b>Bearing:</b></td>
                    <td>{target.relative_bearing_deg:.1f}°</td>
                </tr>
                <tr>
                    <td><b>MMSI:</b></td>
                    <td>{target.mmsi}</td>
                </tr>
                <tr>
                    <td><b>AIS Class:</b></td>
                    <td>{ais_class_str}</td>
                </tr>
            </table>
        </div>
        """
        return popup_html

    def _add_heading_line(self, folium_map: folium.Map, lat: float, lon: float,
                          course_deg: float, color: str, length_m: float = 500):
        """
        Add a heading line showing target direction.

        Args:
            folium_map: Map to add line to
            lat: Target latitude
            lon: Target longitude
            course_deg: Target course in degrees
            color: Line color
            length_m: Line length in meters
        """
        # Calculate endpoint
        end_lat, end_lon = destination_point(lat, lon, length_m, course_deg)

        # Draw heading line
        folium.PolyLine(
            locations=[[lat, lon], [end_lat, end_lon]],
            color=color,
            weight=2,
            opacity=0.7,
            dash_array='5, 5',
            tooltip=f"Course: {course_deg:.1f}°"
        ).add_to(folium_map)

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
        ).add_to(folium_map)

    def clear(self):
        """Clear all target markers."""
        self._targets.clear()
        self._markers.clear()

    def get_marker(self, target_id: str) -> folium.Marker:
        """
        Get marker for specific target.

        Args:
            target_id: Target ID

        Returns:
            Folium marker or None
        """
        return self._markers.get(target_id)
