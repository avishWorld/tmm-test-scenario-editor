# TMM Test Scenario Editor - Comprehensive Testing Plan

**Document Version:** 1.0
**Created:** 2025-11-18
**Status:** 🟡 IN PROGRESS

---

## OVERVIEW

This document outlines a comprehensive testing strategy for the TMM Test Scenario Editor project, covering unit tests, integration tests, and validation tests for all components.

### Testing Goals

1. **Code Coverage:** Achieve ≥80% code coverage across all modules
2. **Reliability:** Ensure all critical paths are tested
3. **Integration:** Verify correct interaction between components
4. **Validation:** Confirm business logic and data validation
5. **Regression:** Prevent future bugs with comprehensive test suite

### Test Framework

- **Framework:** pytest
- **Mocking:** unittest.mock
- **Coverage:** pytest-cov
- **Structure:** Mirror source structure in tests/

---

## TESTING PHASES

### Phase 1: Unit Tests - Models (Priority: HIGH)

All data model classes with validation logic.

#### 1.1 GeoPosition Tests (`tests/models/test_geo.py`)

**Test Cases:**
- ✅ Valid latitude/longitude ranges (-90 to 90, -180 to 180)
- ✅ Invalid coordinates rejection
- ✅ Equality comparison
- ✅ String representation
- ✅ Serialization/deserialization

**Requirements:** TSE-DATA-020 to TSE-DATA-025

#### 1.2 VesselDimensions Tests (`tests/models/test_geo.py`)

**Test Cases:**
- ✅ Valid dimensions (positive values)
- ✅ Invalid dimensions rejection (negative/zero)
- ✅ Typical vessel sizes (small boat, cargo ship, etc.)
- ✅ Serialization/deserialization

**Requirements:** TSE-DATA-026

#### 1.3 SensorConfiguration Tests (`tests/models/test_sensor.py`)

**Test Cases:**
- ✅ Default sensor states (all enabled)
- ✅ Individual sensor enable/disable
- ✅ All sensors disabled warning
- ✅ Serialization/deserialization

**Requirements:** TSE-FUNC-050 to TSE-FUNC-055

#### 1.4 SensorDropout Tests (`tests/models/test_sensor.py`)

**Test Cases:**
- ✅ Valid dropout creation (sensor, start, end)
- ✅ Invalid time ranges (end < start)
- ✅ Zero-duration dropout handling
- ✅ Sensor type validation
- ✅ Duration calculation

**Requirements:** TSE-FUNC-052 to TSE-FUNC-055

#### 1.5 Waypoint Tests (`tests/models/test_waypoint.py`)

**Test Cases:**
- ✅ WP1 constraints (time=0, initial position)
- ✅ Subsequent waypoint creation
- ✅ Time ordering validation
- ✅ Speed/course value ranges
- ✅ Position validation
- ✅ Serialization/deserialization

**Requirements:** TSE-FUNC-040 to TSE-FUNC-046

#### 1.6 Target Tests (`tests/models/test_target.py`)

**Test Cases:**
- ✅ Target creation with all fields
- ✅ Relative positioning (range 40-20,000m)
- ✅ Bearing validation (0-360°)
- ✅ Speed/course validation
- ✅ MMSI validation (9 digits)
- ✅ Vessel type assignment
- ✅ AIS configuration
- ✅ Route assignment
- ✅ Serialization/deserialization

**Requirements:** TSE-FUNC-020 to TSE-FUNC-030

#### 1.7 OwnShip Tests (`tests/models/test_own_ship.py`)

**Test Cases:**
- ✅ Own Ship creation with position
- ✅ Speed/course validation
- ✅ Sensor configuration
- ✅ Dropout management
- ✅ Serialization/deserialization

**Requirements:** TSE-FUNC-010 to TSE-FUNC-014

#### 1.8 Scenario Tests (`tests/models/test_scenario.py`)

**Test Cases:**
- ✅ Scenario creation with metadata
- ✅ Duration validation (≥10 sec, ≤24 hours)
- ✅ Own Ship assignment
- ✅ Target list management (add/remove)
- ✅ Unique target ID enforcement
- ✅ Coordinate system selection
- ✅ Serialization/deserialization

**Requirements:** TSE-FUNC-001 to TSE-FUNC-005

---

### Phase 2: Unit Tests - Utilities (Priority: HIGH)

#### 2.1 Geographic Calculations (`tests/utils/test_geo_calc.py`)

**Test Cases:**
- ✅ `haversine_distance()` - accuracy ±0.5% up to 20 NM
  - Same point (0 distance)
  - Short distances (< 1 NM)
  - Medium distances (1-10 NM)
  - Long distances (10-20 NM)
  - Antipodal points
- ✅ `forward_azimuth()` - bearing calculation
  - North/South/East/West directions
  - Diagonal directions
  - Reverse azimuth
- ✅ `destination_point()` - accuracy ±10m up to 20 NM
  - Various distances and bearings
  - Boundary conditions
- ✅ `calculate_relative_position()` - range/bearing from reference
- ✅ `meters_per_degree_longitude()` - latitude-dependent scaling

**Requirements:** TSE-FUNC-151 to TSE-FUNC-154

#### 2.2 Unit Conversions (`tests/utils/test_unit_conversion.py`)

**Test Cases:**
- ✅ Knots ↔ m/s conversions
- ✅ Degrees ↔ radians conversions
- ✅ Nautical miles ↔ meters conversions
- ✅ Round-trip conversions (no precision loss)
- ✅ Zero and negative values
- ✅ Alias functions (knots_to_ms, ms_to_knots)

**Requirements:** TSE-FUNC-083

---

### Phase 3: Unit Tests - Validation (Priority: HIGH)

#### 3.1 Route Validator (`tests/validation/test_route_validator.py`)

**Test Cases:**
- ✅ Valid route validation
- ✅ WP1 constraints (time=0, position matches)
- ✅ Time ordering (monotonic increase)
- ✅ Waypoint count (≥2)
- ✅ Speed limits (0-40 kts)
- ✅ Course limits (0-360°)
- ✅ Route reachability (distance vs. speed)
- ✅ Empty route handling
- ✅ Single waypoint route

**Requirements:** TSE-FUNC-105 to TSE-FUNC-107

#### 3.2 Dropout Validator (`tests/validation/test_dropout_validator.py`)

**Test Cases:**
- ✅ Valid dropout validation
- ✅ Time range validation (end > start)
- ✅ Scenario duration validation
- ✅ Overlap detection (same sensor)
- ✅ Multiple dropouts for same sensor
- ✅ Different sensors no conflict
- ✅ Empty dropout list

**Requirements:** TSE-FUNC-053 to TSE-FUNC-055

#### 3.3 Main Validator (`tests/validation/test_validator.py`)

**Test Cases:**
- ✅ Complete scenario validation
- ✅ Scenario metadata validation
- ✅ Own Ship validation
- ✅ Target validation (all fields)
- ✅ Unique target ID validation
- ✅ Duplicate MMSI detection
- ✅ Range/proximity validation
- ✅ Error/warning separation
- ✅ Validation summary generation

**Requirements:** TSE-FUNC-100 to TSE-FUNC-109

---

### Phase 4: Unit Tests - Logic (Priority: MEDIUM)

#### 4.1 Route Calculator (`tests/logic/test_route_calculator.py`)

**Test Cases:**
- ✅ Route metrics calculation
  - Total distance
  - Total time
  - Average speed
  - Maximum speed
- ✅ Leg-by-leg calculations
- ✅ Route reachability check
- ✅ Empty route handling
- ✅ Single waypoint handling

**Requirements:** TSE-FUNC-046, TSE-FUNC-107

#### 4.2 Scenario Manager (`tests/logic/test_scenario_manager.py`)

**Test Cases:**
- ✅ New scenario creation (defaults)
- ✅ Current scenario tracking
- ✅ Modified state tracking
- ✅ Recent files list (max 10)
- ✅ Recent files persistence (QSettings)
- ✅ Clear recent files

**Requirements:** TSE-FUNC-110, TSE-FUNC-114

---

### Phase 5: Unit Tests - I/O (Priority: HIGH)

#### 5.1 Project File I/O (`tests/io/test_project_file.py`)

**Test Cases:**
- ✅ Save project to .tse file
- ✅ Load project from .tse file
- ✅ Round-trip (save → load → compare)
- ✅ File format versioning
- ✅ Metadata preservation
- ✅ Invalid file handling
- ✅ Missing file handling
- ✅ Corrupted JSON handling
- ✅ Version compatibility

**Requirements:** TSE-FUNC-111, TSE-FUNC-112

#### 5.2 JSON Exporter (`tests/io/test_json_exporter.py`)

**Test Cases:**
- ✅ Complete scenario export
- ✅ Own Ship export (boats[0])
- ✅ Target export (boats[1..n])
- ✅ Waypoint export
- ✅ Sensor configuration export
- ✅ Dropout export
- ✅ Unit conversions (knots → m/s)
- ✅ Dimension calculations (a, b, c, d)
- ✅ Valid JSON output
- ✅ Empty/minimal scenario export

**Requirements:** TSE-FUNC-080 to TSE-FUNC-087

#### 5.3 JSON Schema Validator (`tests/io/test_json_schema_validator.py`)

**Test Cases:**
- ✅ Valid JSON validation
- ✅ Invalid JSON rejection
- ✅ Schema violation detection
- ✅ Missing required fields
- ✅ Type mismatches
- ✅ Range violations
- ✅ Error message clarity

**Requirements:** TSE-FUNC-088, TSE-INTF-020

---

### Phase 6: Integration Tests (Priority: HIGH)

#### 6.1 Model Integration (`tests/integration/test_models.py`)

**Test Cases:**
- ✅ Scenario → OwnShip → Waypoints (full chain)
- ✅ Scenario → Targets → Routes
- ✅ Target → Relative Position → Absolute Position
- ✅ Sensor Configuration → Dropouts
- ✅ Complex scenario with multiple targets

**Requirements:** Integration between all models

#### 6.2 Validation Integration (`tests/integration/test_validation.py`)

**Test Cases:**
- ✅ Scenario validation with routes
- ✅ Scenario validation with dropouts
- ✅ Multi-target validation
- ✅ Cross-target validation (ID uniqueness)
- ✅ Cascading validation errors

**Requirements:** TSE-FUNC-100 to TSE-FUNC-109

#### 6.3 I/O Integration (`tests/integration/test_io.py`)

**Test Cases:**
- ✅ Complete workflow: Create → Save → Load → Validate
- ✅ Create → Export JSON → Validate Schema
- ✅ Load → Modify → Save → Verify Changes
- ✅ Multiple save/load cycles

**Requirements:** TSE-FUNC-080, TSE-FUNC-111, TSE-FUNC-112

#### 6.4 Geographic Calculations Integration (`tests/integration/test_geo.py`)

**Test Cases:**
- ✅ Target placement using relative positioning
- ✅ Route distance calculations
- ✅ Multi-waypoint route metrics
- ✅ Real-world scenario (Haifa port example)

**Requirements:** TSE-FUNC-020 to TSE-FUNC-022, TSE-FUNC-151 to TSE-FUNC-154

---

### Phase 7: End-to-End Tests (Priority: MEDIUM)

#### 7.1 Complete Workflow (`tests/e2e/test_complete_workflow.py`)

**Test Cases:**
- ✅ Full scenario creation workflow
- ✅ Export to simulator JSON
- ✅ Validation at each step
- ✅ Save and reload
- ✅ Multiple modifications

**Requirements:** All functional requirements

#### 7.2 Real-World Scenarios (`tests/e2e/test_scenarios.py`)

**Test Cases:**
- ✅ Simple scenario (1 Own Ship, 1 Target)
- ✅ Medium scenario (1 Own Ship, 5 Targets)
- ✅ Complex scenario (1 Own Ship, 20 Targets, routes, dropouts)
- ✅ Maritime exercises (realistic configurations)

**Requirements:** All functional requirements

---

## TEST EXECUTION PLAN

### Execution Order

1. **Phase 1:** Models unit tests (foundation)
2. **Phase 2:** Utilities unit tests (dependencies)
3. **Phase 3:** Validation unit tests (business logic)
4. **Phase 4:** Logic unit tests
5. **Phase 5:** I/O unit tests
6. **Phase 6:** Integration tests
7. **Phase 7:** E2E tests

### Success Criteria

- ✅ All tests pass
- ✅ Code coverage ≥80%
- ✅ No critical bugs found
- ✅ All requirements covered by tests

### Test Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tse --cov-report=html --cov-report=term

# Run specific test file
pytest tests/models/test_geo.py -v

# Run specific test
pytest tests/models/test_geo.py::test_valid_geoposition -v

# Run tests by marker
pytest -m "unit" -v
pytest -m "integration" -v
```

---

## TEST DATA

### Sample Coordinates

- **Haifa Port:** 32.82°N, 34.98°E
- **Tel Aviv:** 32.08°N, 34.78°E
- **Eilat:** 29.55°N, 34.95°E

### Sample Vessels

- **Cargo Ship:** Length 200m, Width 30m, Speed 15 kts
- **Patrol Boat:** Length 50m, Width 8m, Speed 25 kts
- **Fishing Vessel:** Length 15m, Width 5m, Speed 8 kts

---

## CURRENT STATUS

| Phase | Status | Progress | Tests Written | Tests Passing |
|-------|--------|----------|---------------|---------------|
| Phase 1 | ⚪ NOT STARTED | 0% | 0/60 | 0/0 |
| Phase 2 | ⚪ NOT STARTED | 0% | 0/15 | 0/0 |
| Phase 3 | ⚪ NOT STARTED | 0% | 0/25 | 0/0 |
| Phase 4 | ⚪ NOT STARTED | 0% | 0/12 | 0/0 |
| Phase 5 | ⚪ NOT STARTED | 0% | 0/20 | 0/0 |
| Phase 6 | ⚪ NOT STARTED | 0% | 0/15 | 0/0 |
| Phase 7 | ⚪ NOT STARTED | 0% | 0/8 | 0/0 |

**Total:** 0/155 tests written, 0/0 passing

---

## NOTES

- UI tests are excluded (require Qt test framework, complex setup)
- Focus on business logic, models, and data flow
- Mock external dependencies (file system, Qt widgets where needed)
- Use fixtures for common test data
- Each test should be independent and repeatable
