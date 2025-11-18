"""
Unit tests for Waypoint model.

Tests for:
- Waypoint creation and validation
- WP1 constraints (time=0)
- Time ordering
- Speed/course validation

Requirements:
- TSE-FUNC-040 to TSE-FUNC-046
"""

import pytest
from tse.models.waypoint import Waypoint
from tse.models.geo import GeoPosition


class TestWaypoint:
    """Test Waypoint class."""

    def test_valid_waypoint(self):
        """Test creation of valid waypoint."""
        wp = Waypoint(
            index=0,
            time_sec=0.0,
            position=GeoPosition(32.82, 34.98),
            relative_range_m=1000.0,
            relative_bearing_deg=45.0,
            speed_knots=10.0,
            course_deg=90.0
        )
        assert wp.index == 0
        assert wp.time_sec == 0.0
        assert wp.relative_range_m == 1000.0
        assert wp.relative_bearing_deg == 45.0
        assert wp.speed_knots == 10.0
        assert wp.course_deg == 90.0

    def test_wp1_time_zero(self):
        """Test WP1 constraint: time must be 0."""
        wp1 = Waypoint(
            index=0,
            time_sec=0.0,
            position=GeoPosition(32.82, 34.98),
            speed_knots=15.0,
            course_deg=180.0
        )
        assert wp1.time_sec == 0.0

    def test_subsequent_waypoint(self):
        """Test creation of subsequent waypoints (not WP1)."""
        wp2 = Waypoint(
            index=1,
            time_sec=60.0,
            position=GeoPosition(32.83, 34.99),
            speed_knots=12.0,
            course_deg=270.0
        )
        assert wp2.index == 1
        assert wp2.time_sec == 60.0

    def test_invalid_negative_time(self):
        """Test rejection of negative time."""
        with pytest.raises(ValueError, match="time .* must be >= 0"):
            Waypoint(
                index=0,
                time_sec=-1.0,
                position=GeoPosition(32.82, 34.98)
            )

    def test_valid_bearing_boundaries(self):
        """Test valid bearing at boundaries."""
        # 0 degrees (North)
        wp_n = Waypoint(index=0, time_sec=0.0, relative_bearing_deg=0.0)
        assert wp_n.relative_bearing_deg == 0.0

        # 359.9 degrees
        wp_max = Waypoint(index=1, time_sec=10.0, relative_bearing_deg=359.9)
        assert wp_max.relative_bearing_deg == 359.9

    def test_invalid_bearing_negative(self):
        """Test rejection of negative bearing."""
        with pytest.raises(ValueError, match="Bearing .* out of range"):
            Waypoint(index=0, time_sec=0.0, relative_bearing_deg=-1.0)

    def test_invalid_bearing_too_high(self):
        """Test rejection of bearing >= 360°."""
        with pytest.raises(ValueError, match="Bearing .* out of range"):
            Waypoint(index=0, time_sec=0.0, relative_bearing_deg=360.0)

    def test_valid_speed_zero(self):
        """Test waypoint with zero speed (stationary)."""
        wp = Waypoint(index=0, time_sec=0.0, speed_knots=0.0)
        assert wp.speed_knots == 0.0

    def test_valid_speed_maximum(self):
        """Test waypoint with maximum speed (40 kts)."""
        wp = Waypoint(index=0, time_sec=0.0, speed_knots=40.0)
        assert wp.speed_knots == 40.0

    def test_invalid_speed_negative(self):
        """Test rejection of negative speed."""
        with pytest.raises(ValueError, match="Speed .* out of range"):
            Waypoint(index=0, time_sec=0.0, speed_knots=-1.0)

    def test_invalid_speed_too_high(self):
        """Test rejection of speed > 40 kts."""
        with pytest.raises(ValueError, match="Speed .* out of range"):
            Waypoint(index=0, time_sec=0.0, speed_knots=41.0)

    def test_valid_course_boundaries(self):
        """Test valid course at boundaries."""
        # 0 degrees (North)
        wp_n = Waypoint(index=0, time_sec=0.0, course_deg=0.0)
        assert wp_n.course_deg == 0.0

        # 359.9 degrees
        wp_max = Waypoint(index=1, time_sec=10.0, course_deg=359.9)
        assert wp_max.course_deg == 359.9

    def test_invalid_course_negative(self):
        """Test rejection of negative course."""
        with pytest.raises(ValueError, match="Course .* out of range"):
            Waypoint(index=0, time_sec=0.0, course_deg=-1.0)

    def test_invalid_course_too_high(self):
        """Test rejection of course >= 360°."""
        with pytest.raises(ValueError, match="Course .* out of range"):
            Waypoint(index=0, time_sec=0.0, course_deg=360.0)

    def test_waypoint_with_position(self):
        """Test waypoint with explicit position."""
        pos = GeoPosition(32.82, 34.98)
        wp = Waypoint(index=0, time_sec=0.0, position=pos)
        assert wp.position == pos
        assert wp.position.latitude_deg == 32.82
        assert wp.position.longitude_deg == 34.98

    def test_waypoint_without_position(self):
        """Test waypoint without position (to be calculated)."""
        wp = Waypoint(
            index=0,
            time_sec=0.0,
            relative_range_m=1000.0,
            relative_bearing_deg=90.0
        )
        assert wp.position is None
        assert wp.relative_range_m == 1000.0
        assert wp.relative_bearing_deg == 90.0

    def test_multiple_waypoints_sequence(self):
        """Test sequence of waypoints with increasing time."""
        waypoints = [
            Waypoint(index=0, time_sec=0.0, speed_knots=10.0, course_deg=0.0),
            Waypoint(index=1, time_sec=60.0, speed_knots=12.0, course_deg=45.0),
            Waypoint(index=2, time_sec=120.0, speed_knots=15.0, course_deg=90.0),
            Waypoint(index=3, time_sec=180.0, speed_knots=10.0, course_deg=180.0)
        ]

        for i, wp in enumerate(waypoints):
            assert wp.index == i
            assert wp.time_sec == i * 60.0

    def test_typical_route_waypoints(self):
        """Test realistic route with multiple waypoints."""
        # Waypoint 1: Start at Haifa
        wp1 = Waypoint(
            index=0,
            time_sec=0.0,
            position=GeoPosition(32.82, 34.98),
            speed_knots=15.0,
            course_deg=180.0
        )

        # Waypoint 2: 5 minutes later, heading south
        wp2 = Waypoint(
            index=1,
            time_sec=300.0,
            position=GeoPosition(32.78, 34.98),
            speed_knots=15.0,
            course_deg=180.0
        )

        # Waypoint 3: 10 minutes later, turning east
        wp3 = Waypoint(
            index=2,
            time_sec=600.0,
            position=GeoPosition(32.74, 35.02),
            speed_knots=15.0,
            course_deg=90.0
        )

        assert wp1.index == 0
        assert wp2.index == 1
        assert wp3.index == 2
        assert wp1.time_sec < wp2.time_sec < wp3.time_sec

    def test_stationary_waypoint(self):
        """Test waypoint representing stationary position."""
        wp = Waypoint(
            index=1,
            time_sec=120.0,
            position=GeoPosition(32.82, 34.98),
            speed_knots=0.0,  # Stationary
            course_deg=0.0
        )
        assert wp.speed_knots == 0.0

    def test_fast_moving_waypoint(self):
        """Test waypoint at high speed."""
        wp = Waypoint(
            index=2,
            time_sec=240.0,
            speed_knots=35.0,  # Fast patrol boat
            course_deg=270.0
        )
        assert wp.speed_knots == 35.0

    def test_cardinal_directions(self):
        """Test waypoints at cardinal directions."""
        wp_n = Waypoint(index=0, time_sec=0.0, course_deg=0.0)    # North
        wp_e = Waypoint(index=1, time_sec=10.0, course_deg=90.0)  # East
        wp_s = Waypoint(index=2, time_sec=20.0, course_deg=180.0) # South
        wp_w = Waypoint(index=3, time_sec=30.0, course_deg=270.0) # West

        assert wp_n.course_deg == 0.0
        assert wp_e.course_deg == 90.0
        assert wp_s.course_deg == 180.0
        assert wp_w.course_deg == 270.0

    def test_waypoint_equality(self):
        """Test waypoint equality comparison."""
        wp1 = Waypoint(
            index=0,
            time_sec=0.0,
            speed_knots=10.0,
            course_deg=90.0
        )
        wp2 = Waypoint(
            index=0,
            time_sec=0.0,
            speed_knots=10.0,
            course_deg=90.0
        )
        wp3 = Waypoint(
            index=1,
            time_sec=0.0,
            speed_knots=10.0,
            course_deg=90.0
        )

        assert wp1 == wp2
        assert wp1 != wp3

    def test_long_duration_waypoint(self):
        """Test waypoint at very long time (end of long scenario)."""
        wp = Waypoint(
            index=10,
            time_sec=3600.0,  # 1 hour
            speed_knots=20.0,
            course_deg=45.0
        )
        assert wp.time_sec == 3600.0

    def test_relative_positioning_fields(self):
        """Test relative positioning fields."""
        wp = Waypoint(
            index=0,
            time_sec=0.0,
            relative_range_m=5000.0,
            relative_bearing_deg=135.0
        )
        assert wp.relative_range_m == 5000.0
        assert wp.relative_bearing_deg == 135.0
