"""
Range rings layer for visualizing distance circles around Own Ship.

Requirements:
- TSE-FUNC-063: Concentric range rings display
- TSE-UI-033: Toggleable layer visibility
"""

import folium
from typing import List, Optional

from tse.models.own_ship import OwnShip


class RangeRingsLayer:
    """
    Renders concentric range rings around Own Ship.

    Features:
    - Multiple range rings at configurable distances
    - Distance labels in nautical miles
    - Semi-transparent circles
    - Centered on Own Ship position

    Requirements: TSE-FUNC-063
    """

    # Default range rings in nautical miles
    DEFAULT_RANGES_NM = [1, 2, 5, 10, 20]

    # Nautical mile to meters conversion
    NM_TO_METERS = 1852.0

    def __init__(self, ranges_nm: Optional[List[float]] = None):
        """
        Initialize Range Rings layer.

        Args:
            ranges_nm: List of ranges in nautical miles (default: [1, 2, 5, 10, 20])
        """
        self._ranges_nm = ranges_nm if ranges_nm else self.DEFAULT_RANGES_NM
        self._own_ship: Optional[OwnShip] = None
        self._circles = []

    def set_own_ship(self, own_ship: OwnShip):
        """
        Set Own Ship position for range rings center.

        Args:
            own_ship: Own Ship object
        """
        self._own_ship = own_ship

    def set_ranges(self, ranges_nm: List[float]):
        """
        Set custom range ring distances.

        Args:
            ranges_nm: List of ranges in nautical miles
        """
        self._ranges_nm = sorted(ranges_nm)  # Sort for consistent display

    def render(self, folium_map: folium.Map):
        """
        Render range rings on the map.

        Args:
            folium_map: Folium map object to render on
        """
        if not self._own_ship or not self._own_ship.position:
            return

        lat = self._own_ship.position.latitude
        lon = self._own_ship.position.longitude

        # Clear previous circles
        self._circles.clear()

        # Create range rings
        for range_nm in self._ranges_nm:
            self._add_range_ring(folium_map, lat, lon, range_nm)

    def _add_range_ring(self, folium_map: folium.Map, lat: float, lon: float, range_nm: float):
        """
        Add a single range ring circle.

        Args:
            folium_map: Map to add circle to
            lat: Center latitude
            lon: Center longitude
            range_nm: Range in nautical miles
        """
        # Convert NM to meters
        range_m = range_nm * self.NM_TO_METERS

        # Create circle
        circle = folium.Circle(
            location=[lat, lon],
            radius=range_m,
            color='blue',
            fill=False,
            weight=1,
            opacity=0.4,
            popup=f"<b>Range Ring</b><br>{range_nm} NM ({range_m:.0f} m)",
            tooltip=f"{range_nm} NM"
        )
        circle.add_to(folium_map)
        self._circles.append(circle)

        # Add label at the top of the circle (North position)
        # Calculate label position (slightly above the circle)
        from tse.utils.geo_calc import destination_point
        label_lat, label_lon = destination_point(lat, lon, range_m, 0)  # 0° = North

        # Create label marker
        folium.Marker(
            location=[label_lat, label_lon],
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    font-size: 11px;
                    font-weight: bold;
                    color: blue;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 2px 5px;
                    border-radius: 3px;
                    border: 1px solid blue;
                    white-space: nowrap;
                    text-align: center;
                ">
                    {range_nm} NM
                </div>
                '''
            )
        ).add_to(folium_map)

    def clear(self):
        """Clear all range rings."""
        self._circles.clear()

    def add_custom_ring(self, folium_map: folium.Map, range_nm: float):
        """
        Add a custom range ring at specified distance.

        Args:
            folium_map: Map to add ring to
            range_nm: Range in nautical miles
        """
        if not self._own_ship or not self._own_ship.position:
            return

        if range_nm not in self._ranges_nm:
            self._ranges_nm.append(range_nm)
            self._ranges_nm.sort()

        self._add_range_ring(
            folium_map,
            self._own_ship.position.latitude,
            self._own_ship.position.longitude,
            range_nm
        )

    def remove_ring(self, range_nm: float):
        """
        Remove a range ring at specified distance.

        Args:
            range_nm: Range in nautical miles to remove
        """
        if range_nm in self._ranges_nm:
            self._ranges_nm.remove(range_nm)
