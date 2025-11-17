"""
Own Ship layer for map visualization.

Requirements:
- TSE-FUNC-061: Display Own Ship on map
- TSE-DATA-023: Own Ship icon/symbol
"""

import folium
from typing import Optional

from tse.models.own_ship import OwnShip
from tse.utils.geo_calc import destination_point


class OwnShipLayer:
    """
    Renders Own Ship marker and associated elements on the map.

    Features:
    - Blue ship icon at Own Ship position
    - Heading indicator line
    - Speed and course display
    - Popup with vessel details

    Requirements: TSE-FUNC-061
    """

    def __init__(self):
        """Initialize Own Ship layer."""
        self._own_ship: Optional[OwnShip] = None
        self._marker = None
        self._heading_line = None

    def set_own_ship(self, own_ship: OwnShip):
        """
        Set the Own Ship to display.

        Args:
            own_ship: Own Ship object
        """
        self._own_ship = own_ship

    def render(self, folium_map: folium.Map):
        """
        Render Own Ship on the map.

        Args:
            folium_map: Folium map object to render on
        """
        if not self._own_ship or not self._own_ship.position:
            return

        lat = self._own_ship.position.latitude
        lon = self._own_ship.position.longitude

        # Create popup with Own Ship info
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #0066cc;">Own Ship</h4>
            <table style="width: 100%;">
                <tr>
                    <td><b>Position:</b></td>
                    <td>{lat:.5f}°N, {lon:.5f}°E</td>
                </tr>
                <tr>
                    <td><b>Speed:</b></td>
                    <td>{self._own_ship.speed_knots:.1f} knots</td>
                </tr>
                <tr>
                    <td><b>Course:</b></td>
                    <td>{self._own_ship.course_deg:.1f}°</td>
                </tr>
            </table>
        </div>
        """

        # Create Own Ship marker (blue ship icon)
        self._marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="<b>Own Ship</b>",
            icon=folium.Icon(
                color='blue',
                icon='ship',
                prefix='fa'
            )
        )
        self._marker.add_to(folium_map)

        # Add heading line if moving
        if self._own_ship.speed_knots > 0:
            self._add_heading_line(folium_map, lat, lon, self._own_ship.course_deg)

    def _add_heading_line(self, folium_map: folium.Map, lat: float, lon: float,
                          course_deg: float, length_m: float = 1000):
        """
        Add a heading line showing Own Ship direction.

        Args:
            folium_map: Map to add line to
            lat: Own Ship latitude
            lon: Own Ship longitude
            course_deg: Own Ship course in degrees
            length_m: Line length in meters (default 1000m)
        """
        # Calculate endpoint using geo calculations
        end_lat, end_lon = destination_point(lat, lon, length_m, course_deg)

        # Draw heading line
        self._heading_line = folium.PolyLine(
            locations=[[lat, lon], [end_lat, end_lon]],
            color='blue',
            weight=3,
            opacity=0.8,
            tooltip=f"Course: {course_deg:.1f}°"
        )
        self._heading_line.add_to(folium_map)

        # Add arrowhead at the end
        folium.RegularPolygonMarker(
            location=[end_lat, end_lon],
            fill=True,
            fillColor='blue',
            fillOpacity=0.9,
            color='darkblue',
            number_of_sides=3,
            radius=10,
            rotation=course_deg
        ).add_to(folium_map)

    def clear(self):
        """Clear Own Ship layer."""
        self._marker = None
        self._heading_line = None
