"""
Unit tests for geographic calculations.

Tests for:
- haversine_distance()
- forward_azimuth()
- destination_point()
- meters_per_degree_longitude()
- meters_per_degree_latitude()

Requirements:
- TSE-FUNC-150 to TSE-FUNC-154
- TSE-DATA-024, TSE-DATA-025
"""

import pytest
import math
from tse.utils.geo_calc import (
    haversine_distance,
    forward_azimuth,
    destination_point,
    meters_per_degree_longitude,
    meters_per_degree_latitude
)


class TestHaversineDistance:
    """Test haversine_distance() function."""

    def test_same_point_zero_distance(self):
        """Test distance from point to itself is zero."""
        distance = haversine_distance(32.82, 34.98, 32.82, 34.98)
        assert distance < 0.001  # Within 1mm

    def test_short_distance_haifa_tel_aviv(self):
        """Test realistic short distance (Haifa to Tel Aviv)."""
        # Haifa: 32.82°N, 34.98°E
        # Tel Aviv: 32.08°N, 34.78°E
        distance = haversine_distance(32.82, 34.98, 32.08, 34.78)

        # Expected: ~84.5 km
        assert 83000 < distance < 86000

    def test_very_short_distance_1nm(self):
        """Test very short distance (~1 NM)."""
        # Start at Haifa
        # Move 0.0167° north ≈ 1 NM (~1.852 km)
        distance = haversine_distance(32.82, 34.98, 32.8367, 34.98)

        # Expected: ~1852 meters (1 nautical mile)
        assert 1800 < distance < 1900

    def test_medium_distance_10nm(self):
        """Test medium distance (~10 NM)."""
        # 0.1667° apart ≈ 10 NM
        distance = haversine_distance(32.0, 35.0, 32.1667, 35.0)

        # Expected: ~18,520 meters (10 nautical miles)
        assert 18000 < distance < 19000

    def test_distance_symmetry(self):
        """Test distance(A,B) == distance(B,A)."""
        dist_ab = haversine_distance(32.82, 34.98, 32.08, 34.78)
        dist_ba = haversine_distance(32.08, 34.78, 32.82, 34.98)

        assert abs(dist_ab - dist_ba) < 1.0  # Within 1 meter

    def test_distance_accuracy_tolerance(self):
        """Test ±0.5% accuracy requirement up to 20 NM."""
        # Test at different distances
        # 5 NM apart (vertically)
        dist = haversine_distance(32.0, 35.0, 32.0833, 35.0)
        expected_5nm = 5 * 1852  # 9260 meters
        error_percent = abs(dist - expected_5nm) / expected_5nm * 100
        assert error_percent < 0.5

        # 10 NM apart
        dist = haversine_distance(32.0, 35.0, 32.1667, 35.0)
        expected_10nm = 10 * 1852  # 18520 meters
        error_percent = abs(dist - expected_10nm) / expected_10nm * 100
        assert error_percent < 0.5

    def test_distance_across_equator(self):
        """Test distance calculation across equator."""
        distance = haversine_distance(-1.0, 0.0, 1.0, 0.0)

        # Expected: ~222 km (2 degrees latitude)
        assert 220000 < distance < 224000

    def test_distance_across_date_line(self):
        """Test distance calculation across international date line."""
        # Just west of date line to just east
        distance = haversine_distance(0.0, 179.0, 0.0, -179.0)

        # Expected: ~222 km (2 degrees longitude at equator)
        assert 220000 < distance < 224000

    def test_north_south_distance(self):
        """Test pure north-south distance."""
        # 1 degree latitude difference
        distance = haversine_distance(32.0, 35.0, 33.0, 35.0)

        # Expected: ~111 km (1 degree latitude)
        assert 110000 < distance < 112000

    def test_east_west_distance_equator(self):
        """Test pure east-west distance at equator."""
        # 1 degree longitude difference at equator
        distance = haversine_distance(0.0, 0.0, 0.0, 1.0)

        # Expected: ~111.32 km (1 degree longitude at equator)
        assert 110000 < distance < 112000

    def test_east_west_distance_at_latitude(self):
        """Test east-west distance at non-zero latitude."""
        # 1 degree longitude at ~60° latitude
        distance = haversine_distance(60.0, 0.0, 60.0, 1.0)

        # Expected: ~55-56 km (1 degree longitude at 60°)
        assert 55000 < distance < 57000


class TestForwardAzimuth:
    """Test forward_azimuth() function."""

    def test_due_north(self):
        """Test bearing due north."""
        bearing = forward_azimuth(32.0, 35.0, 33.0, 35.0)
        assert abs(bearing - 0.0) < 0.1

    def test_due_east(self):
        """Test bearing due east."""
        bearing = forward_azimuth(32.0, 35.0, 32.0, 36.0)
        assert abs(bearing - 90.0) < 1.0

    def test_due_south(self):
        """Test bearing due south."""
        bearing = forward_azimuth(32.0, 35.0, 31.0, 35.0)
        assert abs(bearing - 180.0) < 0.1

    def test_due_west(self):
        """Test bearing due west."""
        bearing = forward_azimuth(32.0, 35.0, 32.0, 34.0)
        assert abs(bearing - 270.0) < 1.0

    def test_northeast_45deg(self):
        """Test bearing northeast (approximately 45°)."""
        # Move equal amounts north and east
        bearing = forward_azimuth(32.0, 35.0, 32.1, 35.1)
        # At latitude 32°, east movement is scaled, so not exactly 45°
        assert 40.0 < bearing < 55.0

    def test_southwest_225deg(self):
        """Test bearing southwest (approximately 225°)."""
        bearing = forward_azimuth(32.0, 35.0, 31.9, 34.9)
        assert 215.0 < bearing < 235.0

    def test_bearing_range_0_to_360(self):
        """Test bearing is always in range [0, 360)."""
        # Test multiple directions
        bearings = [
            forward_azimuth(32.0, 35.0, 33.0, 35.0),  # North
            forward_azimuth(32.0, 35.0, 32.0, 36.0),  # East
            forward_azimuth(32.0, 35.0, 31.0, 35.0),  # South
            forward_azimuth(32.0, 35.0, 32.0, 34.0),  # West
        ]

        for bearing in bearings:
            assert 0.0 <= bearing < 360.0

    def test_same_point_undefined_bearing(self):
        """Test bearing from point to itself."""
        # Bearing is undefined, but function should return something in range
        bearing = forward_azimuth(32.0, 35.0, 32.0, 35.0)
        assert 0.0 <= bearing < 360.0

    def test_haifa_to_tel_aviv_bearing(self):
        """Test realistic bearing (Haifa to Tel Aviv)."""
        # Haifa: 32.82°N, 34.98°E
        # Tel Aviv: 32.08°N, 34.78°E
        # Expected: roughly southwest (~190-200°)
        bearing = forward_azimuth(32.82, 34.98, 32.08, 34.78)
        assert 180.0 < bearing < 210.0


class TestDestinationPoint:
    """Test destination_point() function."""

    def test_zero_distance_same_point(self):
        """Test zero distance returns same point."""
        lat2, lon2 = destination_point(32.82, 34.98, 0.0, 0.0)
        assert abs(lat2 - 32.82) < 0.000001
        assert abs(lon2 - 34.98) < 0.000001

    def test_north_1km(self):
        """Test moving 1 km north."""
        lat2, lon2 = destination_point(32.0, 35.0, 1000.0, 0.0)

        # Should move ~0.009° north (1km / 111km per degree)
        assert lat2 > 32.0
        assert abs(lat2 - 32.009) < 0.001
        assert abs(lon2 - 35.0) < 0.0001  # Longitude unchanged

    def test_east_1km_at_equator(self):
        """Test moving 1 km east at equator."""
        lat2, lon2 = destination_point(0.0, 0.0, 1000.0, 90.0)

        # Should move ~0.009° east at equator
        assert abs(lat2 - 0.0) < 0.0001  # Latitude unchanged
        assert lon2 > 0.0
        assert abs(lon2 - 0.009) < 0.001

    def test_south_2km(self):
        """Test moving 2 km south."""
        lat2, lon2 = destination_point(32.0, 35.0, 2000.0, 180.0)

        # Should move ~0.018° south
        assert lat2 < 32.0
        assert abs(lat2 - 31.982) < 0.001
        assert abs(lon2 - 35.0) < 0.0001

    def test_west_1km(self):
        """Test moving 1 km west."""
        lat2, lon2 = destination_point(32.0, 35.0, 1000.0, 270.0)

        # Should move west
        assert abs(lat2 - 32.0) < 0.0001  # Latitude unchanged
        assert lon2 < 35.0

    def test_round_trip_consistency(self):
        """Test destination_point and haversine_distance consistency."""
        # Start point
        lat1, lon1 = 32.82, 34.98
        range_m = 5000.0
        bearing = 45.0

        # Calculate destination
        lat2, lon2 = destination_point(lat1, lon1, range_m, bearing)

        # Calculate distance back
        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # Should match original range (within accuracy)
        error = abs(distance - range_m)
        error_percent = error / range_m * 100
        assert error_percent < 1.0  # Within 1%

    def test_accuracy_10m_requirement(self):
        """Test ±10m accuracy up to 20 NM."""
        lat1, lon1 = 32.0, 35.0

        # Test at different ranges
        for range_nm in [1, 5, 10, 15, 20]:
            range_m = range_nm * 1852  # Convert NM to meters

            # Move north
            lat2, lon2 = destination_point(lat1, lon1, range_m, 0.0)

            # Verify distance
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            error = abs(distance - range_m)
            assert error < 10.0  # Within 10 meters

    def test_1nm_north_from_haifa(self):
        """Test moving 1 NM north from Haifa."""
        lat2, lon2 = destination_point(32.82, 34.98, 1852.0, 0.0)

        # Latitude should increase by ~1/60 degree
        assert lat2 > 32.82
        assert abs(lat2 - (32.82 + 1.0/60.0)) < 0.001

    def test_10nm_east_from_haifa(self):
        """Test moving 10 NM east from Haifa."""
        range_m = 10 * 1852  # 10 nautical miles
        lat2, lon2 = destination_point(32.82, 34.98, range_m, 90.0)

        # Longitude should increase
        assert lon2 > 34.98
        # At 32.82° latitude, 1 degree is ~95 km, so 18.52 km should be ~0.195°
        assert abs(lon2 - (34.98 + 0.195)) < 0.02

    def test_diagonal_movement_northeast(self):
        """Test diagonal movement northeast (45°)."""
        lat2, lon2 = destination_point(32.0, 35.0, 10000.0, 45.0)

        # Both lat and lon should increase
        assert lat2 > 32.0
        assert lon2 > 35.0

    def test_diagonal_movement_southwest(self):
        """Test diagonal movement southwest (225°)."""
        lat2, lon2 = destination_point(32.0, 35.0, 10000.0, 225.0)

        # Both lat and lon should decrease
        assert lat2 < 32.0
        assert lon2 < 35.0

    def test_longitude_normalization(self):
        """Test longitude normalization to [-180, 180]."""
        # Move far east (crossing 180°)
        lat2, lon2 = destination_point(0.0, 179.0, 500000.0, 90.0)

        # Longitude should be normalized
        assert -180.0 <= lon2 <= 180.0


class TestMetersPerDegreeLongitude:
    """Test meters_per_degree_longitude() function."""

    def test_at_equator(self):
        """Test meters per degree longitude at equator."""
        meters = meters_per_degree_longitude(0.0)

        # Expected: ~111,320 meters/degree
        assert 111000 < meters < 112000

    def test_at_60_degrees(self):
        """Test meters per degree longitude at 60° latitude."""
        meters = meters_per_degree_longitude(60.0)

        # Expected: ~55,660 meters/degree (cos(60°) = 0.5)
        assert 55000 < meters < 56500

    def test_at_haifa_latitude(self):
        """Test meters per degree longitude at Haifa latitude (~32.82°)."""
        meters = meters_per_degree_longitude(32.82)

        # Expected: ~94,000 meters/degree (cos(32.82°) ≈ 0.84)
        assert 93000 < meters < 95000

    def test_at_poles(self):
        """Test meters per degree longitude at poles."""
        meters_north = meters_per_degree_longitude(90.0)
        meters_south = meters_per_degree_longitude(-90.0)

        # At poles: ~0 meters/degree (cos(90°) = 0)
        assert meters_north < 100
        assert meters_south < 100

    def test_symmetry_north_south(self):
        """Test symmetry between northern and southern hemispheres."""
        meters_30n = meters_per_degree_longitude(30.0)
        meters_30s = meters_per_degree_longitude(-30.0)

        assert abs(meters_30n - meters_30s) < 1.0


class TestMetersPerDegreeLatitude:
    """Test meters_per_degree_latitude() function."""

    def test_constant_value(self):
        """Test latitude spacing is approximately constant."""
        meters = meters_per_degree_latitude()

        # Expected: ~111,111 meters/degree
        assert 110000 < meters < 112000

    def test_approximation(self):
        """Test approximation is close to actual value."""
        meters = meters_per_degree_latitude()

        # Should be very close to 111,111
        assert abs(meters - 111111.0) < 1.0
