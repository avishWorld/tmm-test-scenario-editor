"""
Unit tests for JSON exporter.

Tests for:
- Scenario export to JSON
- Own Ship export
- Target export
- Sensor configuration export
- Unit conversions

Requirements:
- TSE-FUNC-080 to TSE-FUNC-087
"""

import pytest
import json
import tempfile
from pathlib import Path

from tse.io.json_exporter import JSONExporter
from tse.models.scenario import Scenario
from tse.models.own_ship import OwnShip
from tse.models.target import Target
from tse.models.geo import GeoPosition, VesselDimensions
from tse.models.sensor import SensorConfiguration, SensorDropout, SensorType
from tse.models.waypoint import Waypoint


class TestJSONExporter:
    """Test JSONExporter class."""

    def test_exporter_initialization(self):
        """Test JSON exporter initialization."""
        exporter = JSONExporter()
        assert exporter is not None

    def test_generate_json_minimal_scenario(self):
        """Test JSON generation for minimal scenario."""
        exporter = JSONExporter()

        # Create minimal scenario
        scenario = Scenario(
            scenario_id="TEST001",
            title="Test Scenario",
            description="Minimal test",
            duration_sec=300
        )

        # Add Own Ship
        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        # Generate JSON
        json_data = exporter.generate_json(scenario)

        # Verify structure
        assert "boats" in json_data
        assert len(json_data["boats"]) == 1  # Only Own Ship
        assert json_data["boats"][0]["name"] == "Own Ship"

    def test_export_to_file(self):
        """Test exporting scenario to file."""
        exporter = JSONExporter()

        # Create minimal scenario
        scenario = Scenario(
            scenario_id="TEST002",
            title="Test Scenario",
            description="File export test",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            result = exporter.export_scenario(scenario, filepath)
            assert result is True

            # Verify file exists and is valid JSON
            with open(filepath, 'r') as f:
                data = json.load(f)
                assert "boats" in data

        finally:
            # Cleanup
            Path(filepath).unlink(missing_ok=True)

    def test_own_ship_export(self):
        """Test Own Ship export structure."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST003",
            title="Own Ship Test",
            description="Test Own Ship export",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=15.0,
            course_deg=45.0
        )
        scenario.own_ship = own_ship

        json_data = exporter.generate_json(scenario)
        own_ship_data = json_data["boats"][0]

        # Verify Own Ship fields
        assert own_ship_data["name"] == "Own Ship"
        assert own_ship_data["color"] == JSONExporter.OWN_SHIP_COLOR
        assert "waypoints" in own_ship_data

    def test_unit_conversion_knots_to_ms(self):
        """Test speed conversion from knots to m/s."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST004",
            title="Unit Conversion Test",
            description="Test unit conversions",
            duration_sec=300
        )

        # Speed in knots
        speed_knots = 20.0

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=speed_knots,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        json_data = exporter.generate_json(scenario)

        # Speed should be converted to m/s
        # 20 knots ≈ 10.29 m/s
        waypoint = json_data["boats"][0]["waypoints"][0]
        speed_ms = waypoint["v"]

        assert 10.0 < speed_ms < 10.5

    def test_dimension_calculations(self):
        """Test vessel dimension calculations (a, b, c, d)."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST005",
            title="Dimensions Test",
            description="Test dimension calculations",
            duration_sec=300
        )

        # Own Ship with dimensions
        dimensions = VesselDimensions(length_m=100.0, width_m=20.0, height_m=10.0)
        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0,
            dimensions=dimensions
        )
        scenario.own_ship = own_ship

        json_data = exporter.generate_json(scenario)
        boat_data = json_data["boats"][0]

        # Check dimension fields
        assert "a" in boat_data
        assert "b" in boat_data
        assert "c" in boat_data
        assert "d" in boat_data

        # a, b should be length/2 = 50.0
        assert boat_data["a"] == 50.0
        assert boat_data["b"] == 50.0

        # c, d should be width/2 = 10.0
        assert boat_data["c"] == 10.0
        assert boat_data["d"] == 10.0

    def test_target_export(self):
        """Test target export structure."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST006",
            title="Target Test",
            description="Test target export",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        # Add target
        target = Target(
            target_id="T001",
            name="Target 1",
            relative_range_m=5000.0,
            relative_bearing_deg=90.0,
            speed_knots=12.0,
            course_deg=180.0,
            mmsi=970000001
        )
        scenario.targets = [target]

        json_data = exporter.generate_json(scenario)

        # Should have Own Ship + 1 target
        assert len(json_data["boats"]) == 2

        target_data = json_data["boats"][1]
        assert target_data["name"] == "Target 1"
        assert target_data["mmsi"] == 970000001

    def test_multiple_targets_color_assignment(self):
        """Test color assignment for multiple targets."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST007",
            title="Multiple Targets Test",
            description="Test multiple targets",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        # Add 3 targets
        targets = []
        for i in range(3):
            target = Target(
                target_id=f"T{i+1:03d}",
                name=f"Target {i+1}",
                relative_range_m=5000.0 + i * 1000,
                relative_bearing_deg=90.0 + i * 30,
                speed_knots=12.0,
                course_deg=180.0,
                mmsi=970000001 + i
            )
            targets.append(target)

        scenario.targets = targets

        json_data = exporter.generate_json(scenario)

        # Should have Own Ship + 3 targets
        assert len(json_data["boats"]) == 4

        # Verify different colors for targets
        colors = [boat["color"] for boat in json_data["boats"][1:]]
        assert len(set(colors)) == 3  # All different colors

    def test_json_pretty_printing(self):
        """Test JSON pretty-printing with indentation."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST008",
            title="Pretty Print Test",
            description="Test JSON formatting",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            exporter.export_scenario(scenario, filepath)

            # Read file and check formatting
            with open(filepath, 'r') as f:
                content = f.read()
                # Should have indentation (spaces)
                assert '  ' in content
                # Should have newlines
                assert '\n' in content

        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_export_with_sensors(self):
        """Test export with sensor configuration."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST009",
            title="Sensor Test",
            description="Test sensor export",
            duration_sec=300
        )

        # Own Ship with sensors
        sensors = SensorConfiguration(
            ais_enabled=True,
            radar_a_enabled=False,
            radar_b_enabled=True,
            eo_enabled=True
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0,
            sensors=sensors
        )
        scenario.own_ship = own_ship

        json_data = exporter.generate_json(scenario)

        # Sensors should be exported
        boat_data = json_data["boats"][0]
        assert "sensors" in boat_data or "visibility" in boat_data

    def test_generate_json_returns_dict(self):
        """Test generate_json returns dictionary."""
        exporter = JSONExporter()

        scenario = Scenario(
            scenario_id="TEST010",
            title="Return Type Test",
            description="Test return type",
            duration_sec=300
        )

        own_ship = OwnShip(
            position=GeoPosition(32.82, 34.98),
            speed_knots=10.0,
            course_deg=0.0
        )
        scenario.own_ship = own_ship

        json_data = exporter.generate_json(scenario)

        assert isinstance(json_data, dict)
        assert "boats" in json_data
        assert isinstance(json_data["boats"], list)
