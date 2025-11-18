"""
Unit tests for sensor configuration models.

Tests for:
- SensorType (enumeration)
- SensorConfiguration (enable/disable flags)
- SensorDropout (temporal dropout periods)

Requirements:
- TSE-FUNC-050 to TSE-FUNC-055
- TSE-FUNC-106 (overlap validation)
"""

import pytest
from tse.models.sensor import SensorType, SensorConfiguration, SensorDropout


class TestSensorType:
    """Test SensorType enumeration."""

    def test_sensor_types_exist(self):
        """Test all sensor types are defined."""
        assert SensorType.AIS_A
        assert SensorType.AIS_B
        assert SensorType.RADAR_A
        assert SensorType.RADAR_B
        assert SensorType.EO

    def test_sensor_type_values(self):
        """Test sensor type string values."""
        assert SensorType.AIS_A.value == "AIS_A"
        assert SensorType.AIS_B.value == "AIS_B"
        assert SensorType.RADAR_A.value == "RADAR_A"
        assert SensorType.RADAR_B.value == "RADAR_B"
        assert SensorType.EO.value == "EO"


class TestSensorConfiguration:
    """Test SensorConfiguration class."""

    def test_default_all_enabled(self):
        """Test default configuration has all sensors enabled."""
        config = SensorConfiguration()
        assert config.ais_enabled is True
        assert config.radar_a_enabled is True
        assert config.radar_b_enabled is True
        assert config.eo_enabled is True

    def test_disable_ais(self):
        """Test disabling AIS sensor."""
        config = SensorConfiguration(ais_enabled=False)
        assert config.ais_enabled is False
        assert config.radar_a_enabled is True
        assert config.radar_b_enabled is True
        assert config.eo_enabled is True

    def test_disable_radar_a(self):
        """Test disabling RADAR A sensor."""
        config = SensorConfiguration(radar_a_enabled=False)
        assert config.ais_enabled is True
        assert config.radar_a_enabled is False
        assert config.radar_b_enabled is True
        assert config.eo_enabled is True

    def test_disable_radar_b(self):
        """Test disabling RADAR B sensor."""
        config = SensorConfiguration(radar_b_enabled=False)
        assert config.ais_enabled is True
        assert config.radar_a_enabled is True
        assert config.radar_b_enabled is False
        assert config.eo_enabled is True

    def test_disable_eo(self):
        """Test disabling EO sensor."""
        config = SensorConfiguration(eo_enabled=False)
        assert config.ais_enabled is True
        assert config.radar_a_enabled is True
        assert config.radar_b_enabled is True
        assert config.eo_enabled is False

    def test_all_disabled(self):
        """Test configuration with all sensors disabled."""
        config = SensorConfiguration(
            ais_enabled=False,
            radar_a_enabled=False,
            radar_b_enabled=False,
            eo_enabled=False
        )
        assert config.ais_enabled is False
        assert config.radar_a_enabled is False
        assert config.radar_b_enabled is False
        assert config.eo_enabled is False

    def test_mixed_configuration(self):
        """Test mixed enabled/disabled configuration."""
        config = SensorConfiguration(
            ais_enabled=True,
            radar_a_enabled=False,
            radar_b_enabled=True,
            eo_enabled=False
        )
        assert config.ais_enabled is True
        assert config.radar_a_enabled is False
        assert config.radar_b_enabled is True
        assert config.eo_enabled is False

    def test_equality(self):
        """Test sensor configuration equality."""
        config1 = SensorConfiguration(ais_enabled=True, radar_a_enabled=False)
        config2 = SensorConfiguration(ais_enabled=True, radar_a_enabled=False)
        config3 = SensorConfiguration(ais_enabled=False, radar_a_enabled=False)

        assert config1 == config2
        assert config1 != config3


class TestSensorDropout:
    """Test SensorDropout class."""

    def test_valid_dropout(self):
        """Test creation of valid sensor dropout."""
        dropout = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=20.0,
            dropout_index=1
        )
        assert dropout.sensor_type == SensorType.AIS_A
        assert dropout.start_time_sec == 10.0
        assert dropout.end_time_sec == 20.0
        assert dropout.dropout_index == 1

    def test_dropout_zero_start(self):
        """Test dropout starting at time 0."""
        dropout = SensorDropout(
            sensor_type=SensorType.RADAR_A,
            start_time_sec=0.0,
            end_time_sec=10.0
        )
        assert dropout.start_time_sec == 0.0

    def test_dropout_until_scenario_end(self):
        """Test dropout with end_time=-1 (until scenario end)."""
        dropout = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=-1
        )
        assert dropout.end_time_sec == -1

    def test_invalid_negative_start_time(self):
        """Test rejection of negative start time."""
        with pytest.raises(ValueError, match="start time must be >= 0"):
            SensorDropout(
                sensor_type=SensorType.AIS_A,
                start_time_sec=-1.0,
                end_time_sec=10.0
            )

    def test_invalid_end_before_start(self):
        """Test rejection of end time before start time."""
        with pytest.raises(ValueError, match="end time must be > start time"):
            SensorDropout(
                sensor_type=SensorType.AIS_A,
                start_time_sec=20.0,
                end_time_sec=10.0
            )

    def test_invalid_zero_duration(self):
        """Test rejection of zero-duration dropout."""
        with pytest.raises(ValueError, match="end time must be > start time"):
            SensorDropout(
                sensor_type=SensorType.AIS_A,
                start_time_sec=10.0,
                end_time_sec=10.0
            )

    def test_duration_calculation(self):
        """Test dropout duration calculation."""
        dropout = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=35.0
        )
        duration = dropout.end_time_sec - dropout.start_time_sec
        assert duration == 25.0

    def test_overlaps_with_same_sensor_overlapping(self):
        """Test overlap detection for same sensor with overlapping periods."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=30.0
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=20.0,
            end_time_sec=40.0
        )
        assert dropout1.overlaps_with(dropout2)
        assert dropout2.overlaps_with(dropout1)

    def test_overlaps_with_same_sensor_contained(self):
        """Test overlap detection for contained dropout."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=40.0
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=20.0,
            end_time_sec=30.0
        )
        assert dropout1.overlaps_with(dropout2)
        assert dropout2.overlaps_with(dropout1)

    def test_overlaps_with_same_sensor_adjacent_no_overlap(self):
        """Test no overlap for adjacent dropouts."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=20.0
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=20.0,
            end_time_sec=30.0
        )
        # Adjacent dropouts don't overlap (end_time = other's start_time)
        assert not dropout1.overlaps_with(dropout2)
        assert not dropout2.overlaps_with(dropout1)

    def test_overlaps_with_same_sensor_separate_no_overlap(self):
        """Test no overlap for separate dropouts."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=20.0
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=30.0,
            end_time_sec=40.0
        )
        assert not dropout1.overlaps_with(dropout2)
        assert not dropout2.overlaps_with(dropout1)

    def test_overlaps_with_different_sensor_no_overlap(self):
        """Test no overlap for different sensors (even if times overlap)."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=30.0
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.RADAR_A,
            start_time_sec=20.0,
            end_time_sec=40.0
        )
        assert not dropout1.overlaps_with(dropout2)
        assert not dropout2.overlaps_with(dropout1)

    def test_overlaps_with_infinite_end(self):
        """Test overlap detection with end_time=-1 (infinite)."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=-1  # Until scenario end
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=50.0,
            end_time_sec=60.0
        )
        # dropout1 extends indefinitely, so it overlaps with dropout2
        assert dropout1.overlaps_with(dropout2)
        assert dropout2.overlaps_with(dropout1)

    def test_overlaps_with_both_infinite(self):
        """Test overlap detection with both having infinite end."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=-1
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=20.0,
            end_time_sec=-1
        )
        assert dropout1.overlaps_with(dropout2)
        assert dropout2.overlaps_with(dropout1)

    def test_multiple_dropout_indices(self):
        """Test dropout index tracking."""
        dropout1 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=10.0,
            end_time_sec=20.0,
            dropout_index=1
        )
        dropout2 = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=30.0,
            end_time_sec=40.0,
            dropout_index=2
        )
        assert dropout1.dropout_index == 1
        assert dropout2.dropout_index == 2

    def test_ais_dropout(self):
        """Test AIS sensor dropout."""
        dropout = SensorDropout(
            sensor_type=SensorType.AIS_A,
            start_time_sec=15.0,
            end_time_sec=45.0
        )
        assert dropout.sensor_type == SensorType.AIS_A

    def test_radar_a_dropout(self):
        """Test RADAR A sensor dropout."""
        dropout = SensorDropout(
            sensor_type=SensorType.RADAR_A,
            start_time_sec=20.0,
            end_time_sec=50.0
        )
        assert dropout.sensor_type == SensorType.RADAR_A

    def test_radar_b_dropout(self):
        """Test RADAR B sensor dropout."""
        dropout = SensorDropout(
            sensor_type=SensorType.RADAR_B,
            start_time_sec=25.0,
            end_time_sec=55.0
        )
        assert dropout.sensor_type == SensorType.RADAR_B

    def test_eo_dropout(self):
        """Test EO sensor dropout."""
        dropout = SensorDropout(
            sensor_type=SensorType.EO,
            start_time_sec=30.0,
            end_time_sec=60.0
        )
        assert dropout.sensor_type == SensorType.EO
