"""
Unit tests for geographic data models.

Tests for:
- GeoPosition (WGS84 coordinates validation)
- VesselDimensions (physical dimensions validation)

Requirements:
- TSE-DATA-020 to TSE-DATA-025
- TSE-FUNC-027, TSE-FUNC-084
"""

import pytest
from tse.models.geo import GeoPosition, VesselDimensions


class TestGeoPosition:
    """Test GeoPosition class."""

    def test_valid_position(self):
        """Test creation of valid geographic position."""
        pos = GeoPosition(latitude_deg=32.82, longitude_deg=34.98)
        assert pos.latitude_deg == 32.82
        assert pos.longitude_deg == 34.98

    def test_valid_position_boundaries(self):
        """Test valid positions at coordinate boundaries."""
        # North pole
        pos_north = GeoPosition(latitude_deg=90.0, longitude_deg=0.0)
        assert pos_north.latitude_deg == 90.0

        # South pole
        pos_south = GeoPosition(latitude_deg=-90.0, longitude_deg=0.0)
        assert pos_south.latitude_deg == -90.0

        # Date line east
        pos_east = GeoPosition(latitude_deg=0.0, longitude_deg=180.0)
        assert pos_east.longitude_deg == 180.0

        # Date line west
        pos_west = GeoPosition(latitude_deg=0.0, longitude_deg=-180.0)
        assert pos_west.longitude_deg == -180.0

    def test_invalid_latitude_too_high(self):
        """Test rejection of latitude > 90°."""
        with pytest.raises(ValueError, match="Latitude .* out of range"):
            GeoPosition(latitude_deg=90.1, longitude_deg=0.0)

    def test_invalid_latitude_too_low(self):
        """Test rejection of latitude < -90°."""
        with pytest.raises(ValueError, match="Latitude .* out of range"):
            GeoPosition(latitude_deg=-90.1, longitude_deg=0.0)

    def test_invalid_longitude_too_high(self):
        """Test rejection of longitude > 180°."""
        with pytest.raises(ValueError, match="Longitude .* out of range"):
            GeoPosition(latitude_deg=0.0, longitude_deg=180.1)

    def test_invalid_longitude_too_low(self):
        """Test rejection of longitude < -180°."""
        with pytest.raises(ValueError, match="Longitude .* out of range"):
            GeoPosition(latitude_deg=0.0, longitude_deg=-180.1)

    def test_equality(self):
        """Test position equality comparison."""
        pos1 = GeoPosition(latitude_deg=32.82, longitude_deg=34.98)
        pos2 = GeoPosition(latitude_deg=32.82, longitude_deg=34.98)
        pos3 = GeoPosition(latitude_deg=32.83, longitude_deg=34.98)

        assert pos1 == pos2
        assert pos1 != pos3

    def test_string_representation(self):
        """Test string representation with 6 decimal places."""
        pos = GeoPosition(latitude_deg=32.82, longitude_deg=34.98)
        s = str(pos)

        # Check format
        assert s.startswith("(")
        assert s.endswith(")")
        assert "32.820000" in s
        assert "34.980000" in s

    def test_precision_6_decimal_places(self):
        """Test precision of 6+ decimal places (TSE-DATA-023)."""
        pos = GeoPosition(latitude_deg=32.123456, longitude_deg=34.987654)
        assert pos.latitude_deg == 32.123456
        assert pos.longitude_deg == 34.987654

    def test_sample_coordinates_haifa(self):
        """Test with real-world coordinates (Haifa Port)."""
        haifa = GeoPosition(latitude_deg=32.82, longitude_deg=34.98)
        assert haifa.latitude_deg == 32.82
        assert haifa.longitude_deg == 34.98

    def test_sample_coordinates_tel_aviv(self):
        """Test with real-world coordinates (Tel Aviv)."""
        tel_aviv = GeoPosition(latitude_deg=32.08, longitude_deg=34.78)
        assert tel_aviv.latitude_deg == 32.08
        assert tel_aviv.longitude_deg == 34.78

    def test_sample_coordinates_eilat(self):
        """Test with real-world coordinates (Eilat)."""
        eilat = GeoPosition(latitude_deg=29.55, longitude_deg=34.95)
        assert eilat.latitude_deg == 29.55
        assert eilat.longitude_deg == 34.95


class TestVesselDimensions:
    """Test VesselDimensions class."""

    def test_valid_dimensions(self):
        """Test creation of valid vessel dimensions."""
        dims = VesselDimensions(length_m=100.0, width_m=20.0, height_m=10.0)
        assert dims.length_m == 100.0
        assert dims.width_m == 20.0
        assert dims.height_m == 10.0

    def test_derived_dimensions_auto_calculation(self):
        """Test automatic calculation of a, b, c, d dimensions."""
        dims = VesselDimensions(length_m=100.0, width_m=20.0, height_m=10.0)

        # a and b = length / 2
        assert dims.a_m == 50.0
        assert dims.b_m == 50.0

        # c and d = width / 2
        assert dims.c_m == 10.0
        assert dims.d_m == 10.0

    def test_derived_dimensions_explicit(self):
        """Test explicit setting of derived dimensions."""
        dims = VesselDimensions(
            length_m=100.0, width_m=20.0, height_m=10.0,
            a_m=60.0, b_m=40.0, c_m=12.0, d_m=8.0
        )

        # Use explicit values
        assert dims.a_m == 60.0
        assert dims.b_m == 40.0
        assert dims.c_m == 12.0
        assert dims.d_m == 8.0

    def test_length_too_small(self):
        """Test rejection of length < 1m."""
        with pytest.raises(ValueError, match="Length .* out of range"):
            VesselDimensions(length_m=0.5, width_m=10.0, height_m=5.0)

    def test_length_too_large(self):
        """Test rejection of length > 500m."""
        with pytest.raises(ValueError, match="Length .* out of range"):
            VesselDimensions(length_m=501.0, width_m=10.0, height_m=5.0)

    def test_width_too_small(self):
        """Test rejection of width < 1m."""
        with pytest.raises(ValueError, match="Width .* out of range"):
            VesselDimensions(length_m=50.0, width_m=0.5, height_m=5.0)

    def test_width_too_large(self):
        """Test rejection of width > 100m."""
        with pytest.raises(ValueError, match="Width .* out of range"):
            VesselDimensions(length_m=200.0, width_m=101.0, height_m=10.0)

    def test_height_too_small(self):
        """Test rejection of height < 1m."""
        with pytest.raises(ValueError, match="Height .* out of range"):
            VesselDimensions(length_m=50.0, width_m=10.0, height_m=0.5)

    def test_height_too_large(self):
        """Test rejection of height > 50m."""
        with pytest.raises(ValueError, match="Height .* out of range"):
            VesselDimensions(length_m=200.0, width_m=30.0, height_m=51.0)

    def test_typical_cargo_ship(self):
        """Test dimensions for typical cargo ship."""
        cargo = VesselDimensions(length_m=200.0, width_m=30.0, height_m=15.0)
        assert cargo.length_m == 200.0
        assert cargo.width_m == 30.0
        assert cargo.height_m == 15.0
        assert cargo.a_m == 100.0
        assert cargo.c_m == 15.0

    def test_typical_patrol_boat(self):
        """Test dimensions for typical patrol boat."""
        patrol = VesselDimensions(length_m=50.0, width_m=8.0, height_m=5.0)
        assert patrol.length_m == 50.0
        assert patrol.width_m == 8.0
        assert patrol.height_m == 5.0
        assert patrol.a_m == 25.0
        assert patrol.c_m == 4.0

    def test_typical_fishing_vessel(self):
        """Test dimensions for typical fishing vessel."""
        fishing = VesselDimensions(length_m=15.0, width_m=5.0, height_m=3.0)
        assert fishing.length_m == 15.0
        assert fishing.width_m == 5.0
        assert fishing.height_m == 3.0
        assert fishing.a_m == 7.5
        assert fishing.c_m == 2.5

    def test_small_boat_minimum(self):
        """Test minimum valid dimensions (small boat)."""
        small = VesselDimensions(length_m=1.0, width_m=1.0, height_m=1.0)
        assert small.length_m == 1.0
        assert small.width_m == 1.0
        assert small.height_m == 1.0
        assert small.a_m == 0.5
        assert small.c_m == 0.5

    def test_large_ship_maximum(self):
        """Test maximum valid dimensions (large ship)."""
        large = VesselDimensions(length_m=500.0, width_m=100.0, height_m=50.0)
        assert large.length_m == 500.0
        assert large.width_m == 100.0
        assert large.height_m == 50.0
        assert large.a_m == 250.0
        assert large.c_m == 50.0

    def test_equality(self):
        """Test dimensions equality comparison."""
        dims1 = VesselDimensions(length_m=100.0, width_m=20.0, height_m=10.0)
        dims2 = VesselDimensions(length_m=100.0, width_m=20.0, height_m=10.0)
        dims3 = VesselDimensions(length_m=101.0, width_m=20.0, height_m=10.0)

        assert dims1 == dims2
        assert dims1 != dims3
