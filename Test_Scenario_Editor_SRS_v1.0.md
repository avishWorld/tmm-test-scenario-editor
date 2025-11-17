# Software Requirements Specification (SRS)
## TMM Test Scenario Editor & Planner
### Maritime Simulation Scenario Configuration Tool

**Document ID:** TSE-SRS-001  
**Version:** 1.0  
**Date:** November 2025  
**Status:** Initial Release  
**Prepared by:** System Engineering Team  
**Classification:** Confidential

---

## Document Information

| **Field** | **Value** |
|-----------|-----------|
| **Document Title** | Software Requirements Specification - Test Scenario Editor |
| **Project** | CDA/TMM Testing & Validation |
| **Purpose** | Define software requirements for the TMM Test Scenario Editor & Planner |
| **Scope** | Interactive scenario configuration, map-based visualization, JSON export |

---

## Authorization Table

| **Role** | **Name** | **Approval Date** | **Signature** |
|----------|----------|-------------------|---------------|
| System Engineer | | | |
| Project Manager | | | |
| Testing Lead | | | |

---

## Table of Revisions

| **Ver. #** | **Description** | **Author** | **Date** |
|------------|-----------------|------------|----------|
| 1.0 | Initial Draft | System Engineering Team | November 2025 |

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Document Scope](#12-document-scope)
   - 1.3 [Document Conventions](#13-document-conventions)
   - 1.4 [Intended Audience](#14-intended-audience)
   - 1.5 [System Context](#15-system-context)
   - 1.6 [References](#16-references)

2. [Overall Description](#2-overall-description)
   - 2.1 [Product Perspective](#21-product-perspective)
   - 2.2 [Product Functions](#22-product-functions)
   - 2.3 [User Characteristics](#23-user-characteristics)
   - 2.4 [Operating Environment](#24-operating-environment)
   - 2.5 [Design and Implementation Constraints](#25-design-and-implementation-constraints)
   - 2.6 [Assumptions and Dependencies](#26-assumptions-and-dependencies)

3. [System Features](#3-system-features)
   - 3.1 [Scenario Configuration](#31-scenario-configuration)
   - 3.2 [Own Ship Definition](#32-own-ship-definition)
   - 3.3 [Target Management](#33-target-management)
   - 3.4 [Waypoint Management](#34-waypoint-management)
   - 3.5 [Sensor Configuration](#35-sensor-configuration)
   - 3.6 [Map Visualization](#36-map-visualization)
   - 3.7 [JSON Export](#37-json-export)
   - 3.8 [Scenario Validation](#38-scenario-validation)

4. [Functional Requirements](#4-functional-requirements)
   - 4.1 [Scenario Creation and Management](#41-scenario-creation-and-management)
   - 4.2 [Target Definition](#42-target-definition)
   - 4.3 [Route Planning](#43-route-planning)
   - 4.4 [Sensor and Dropout Configuration](#44-sensor-and-dropout-configuration)
   - 4.5 [Geographic Calculations](#45-geographic-calculations)
   - 4.6 [Data Persistence](#46-data-persistence)

5. [External Interface Requirements](#5-external-interface-requirements)
   - 5.1 [User Interfaces](#51-user-interfaces)
   - 5.2 [Software Interfaces](#52-software-interfaces)
   - 5.3 [Hardware Interfaces](#53-hardware-interfaces)
   - 5.4 [Communications Interfaces](#54-communications-interfaces)

6. [Performance Requirements](#6-performance-requirements)
   - 6.1 [Response Time](#61-response-time)
   - 6.2 [Throughput](#62-throughput)
   - 6.3 [Capacity](#63-capacity)
   - 6.4 [Resource Utilization](#64-resource-utilization)

7. [Non-Functional Requirements](#7-non-functional-requirements)
   - 7.1 [Usability](#71-usability)
   - 7.2 [Reliability](#72-reliability)
   - 7.3 [Maintainability](#73-maintainability)
   - 7.4 [Portability](#74-portability)

8. [Data Models and Specifications](#8-data-models-and-specifications)
   - 8.1 [Internal Data Model](#81-internal-data-model)
   - 8.2 [JSON Output Format](#82-json-output-format)
   - 8.3 [Coordinate Systems](#83-coordinate-systems)

9. [Verification and Validation](#9-verification-and-validation)
   - 9.1 [Verification Methods](#91-verification-methods)
   - 9.2 [Requirements Traceability](#92-requirements-traceability)

10. [Appendices](#10-appendices)
    - 10.1 [Glossary](#101-glossary)
    - 10.2 [Use Case Diagrams](#102-use-case-diagrams)
    - 10.3 [Example Scenarios](#103-example-scenarios)

---

# 1. Introduction

## 1.1 Purpose

This document specifies the software requirements for the **TMM Test Scenario Editor & Planner** (TSE), a graphical tool designed to facilitate the creation, visualization, and export of maritime test scenarios for the Track Management Module (TMM) of the CDA (Collision Detection & Avoidance) Naval System.

The TSE addresses the critical need for system engineers and test engineers to efficiently define complex multi-target maritime scenarios without manually editing JSON configuration files. The tool provides an intuitive, map-based interface for scenario planning, automatic coordinate transformation from relative positioning to absolute geodetic coordinates, and comprehensive validation to ensure scenarios are realistic and executable.

**Primary Objectives:**
- Simplify the creation of TMM test scenarios through visual, interactive tools
- Enable rapid scenario definition using relative positioning (range and bearing)
- Provide map-based visualization of scenario layouts with Own Ship, targets, and routes
- Automatically generate well-formed JSON configuration files for the world simulator
- Support flexible sensor configuration including detection visibility and temporal dropouts
- Validate scenarios against operational and technical constraints

## 1.2 Document Scope

This SRS covers the complete TSE application including:

**In Scope:**
- Interactive GUI for scenario configuration
- Map-based visualization with target placement and route planning
- Own Ship definition (position, kinematics, sensors)
- Target management (unlimited targets with individual configurations)
- Waypoint-based route planning for moving targets
- Sensor configuration (AIS, RADAR A/B, EO) per target
- Sensor dropout scheduling (temporal visibility windows)
- Relative-to-absolute coordinate transformation
- JSON export conforming to simulator input specification
- Scenario validation and error checking
- Project/scenario save/load functionality

**Out of Scope:**
- Real-time simulation execution (handled by separate simulator)
- 3D visualization
- Weather/environmental condition modeling
- Multi-user collaboration
- Integration with live sensor feeds
- Post-simulation analysis tools

## 1.3 Document Conventions

### Requirement Identifier Taxonomy

Requirements in this document use the following naming convention:

- **TSE-FUNC-XXX**: Functional requirements
- **TSE-UI-XXX**: User interface requirements
- **TSE-INTF-XXX**: Interface requirements
- **TSE-PERF-XXX**: Performance requirements
- **TSE-NF-XXX**: Non-functional requirements
- **TSE-DATA-XXX**: Data model requirements

Where **XXX** is a unique three-digit sequential number.

### Requirement Statement Format

All mandatory requirements use the keyword **"shall"**.  
Recommended features use **"should"**.  
Permitted or optional features use **"may"**.

### Units and Conventions

- **Distance**: Meters (m), Nautical Miles (NM)
- **Speed**: Knots, meters per second (m/s)
- **Angles**: Degrees (°) from true north (0-360°)
- **Time**: Seconds (s), coordinated universal time (UTC)
- **Coordinates**: WGS84 geodetic (latitude/longitude in decimal degrees)

## 1.4 Intended Audience

This document is intended for:

- **System Engineers**: Overall system design and requirements validation
- **Software Developers**: Implementation of TSE application
- **Test Engineers**: Understanding of scenario creation capabilities and constraints
- **Quality Assurance**: Verification and validation planning
- **Project Managers**: Project planning, resource allocation, and milestone tracking

## 1.5 System Context

The TSE operates as a **standalone desktop application** within the TMM development and testing ecosystem:

```
┌─────────────────────────────────────────────────────────┐
│              TMM Testing Ecosystem                       │
│                                                          │
│  ┌──────────────────┐                                   │
│  │  Test Scenario   │                                   │
│  │  Editor (TSE)    │                                   │
│  │  [THIS SYSTEM]   │                                   │
│  └────────┬─────────┘                                   │
│           │                                              │
│           │ JSON Export                                  │
│           ▼                                              │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  World Simulator │─────▶│   TMM Module     │        │
│  │  (Target Gen)    │ MQTT │  (System Under   │        │
│  │                  │      │   Test)          │        │
│  └──────────────────┘      └──────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Input Dependencies:**
- None (standalone scenario creation tool)

**Output Products:**
- JSON scenario configuration files (conforming to simulator input specification v0.6.0+)
- Project save files (TSE native format)

**Related Systems:**
- **World Simulator**: Consumes JSON scenarios to generate synthetic sensor data
- **TMM Module**: Receives simulated sensor data for testing and validation
- **CDA System**: Ultimate target system for TMM integration

## 1.6 References

1. **TMM SRS** - Track Management Module Software Requirements Specification v1.6
2. **CDA TLR** - CDA Top-Level Requirements v1.5
3. **Simulator Input Specification** - World Simulator JSON Format v0.6.0
4. **IEC 62388-2013** - Maritime navigation and radiocommunication equipment and systems - RADAR
5. **ITU-R M.1371** - Technical characteristics for AIS
6. **WGS84 Standard** - World Geodetic System 1984 Coordinate System

---

# 2. Overall Description

## 2.1 Product Perspective

The TMM Test Scenario Editor is a **new, standalone application** developed to address the growing complexity of TMM system testing. As the TMM system evolved to support multiple sensors, complex track fusion algorithms, and sophisticated scenario-based testing, the manual creation of JSON test scenarios became error-prone and time-consuming.

The TSE fills this gap by providing:
- A visual, map-based interface for intuitive scenario layout
- Automated coordinate transformations and calculations
- Built-in validation to catch configuration errors early
- Rapid iteration on scenario design

**System Context Diagram:**

```
External Systems          TSE Application           Output Artifacts
                    
User Input ──────▶  ┌─────────────────────┐
                    │                     │
Map Services ─────▶ │   Scenario Editor   │ ──────▶ JSON Files
                    │                     │
                    │  • GUI              │ ──────▶ Project Files
                    │  • Map Viewer       │
                    │  • Data Model       │ ──────▶ Reports
                    │  • Validator        │
                    │  • JSON Generator   │
                    │                     │
                    └─────────────────────┘
```

## 2.2 Product Functions

The TSE provides the following major functional areas:

### F1: Scenario Configuration
- Define scenario metadata (title, description, duration)
- Configure Own Ship initial state and kinematics
- Set simulation parameters (stopping conditions, coordinate system)

### F2: Target Management
- Add/remove/edit unlimited maritime targets
- Position targets using relative coordinates (range + bearing from Own Ship)
- Define target characteristics (vessel type, dimensions, MMSI, navigation status)
- Configure target kinematics (speed, course)

### F3: Route Planning
- Create multi-waypoint routes for moving targets
- Visual route editing on map interface
- Waypoint-level speed and course specification
- Route validation (continuity, timing, reachability)

### F4: Sensor Configuration
- Enable/disable sensors per target (AIS Class A/B, RADAR A, RADAR B, EO)
- Define sensor dropout windows (start time, end time, sensor type)
- Visualize sensor coverage and dropout timelines

### F5: Map-Based Visualization
- Interactive map display with zoom/pan
- Real-time visualization of Own Ship position
- Target placement with range rings and bearing lines
- Route visualization with waypoint markers
- Sensor coverage indicators

### F6: Validation & Export
- Real-time scenario validation with error/warning feedback
- JSON export conforming to simulator specification
- Validation checks for:
  - Target proximity (collision avoidance)
  - Sensor range limits (RADAR < 11 NM, etc.)
  - Timeline consistency
  - MMSI uniqueness
  - Speed/course realism

## 2.3 User Characteristics

### Primary Users: Test Engineers

**Profile:**
- Education: B.Sc. in Engineering (Electrical, Software, Systems)
- Experience: 2+ years in maritime systems or navigation
- Technical Skills: Familiar with maritime concepts (RADAR, AIS, navigation)
- Domain Knowledge: Understanding of sensor characteristics and limitations

**Usage Patterns:**
- Create 5-10 new scenarios per week
- Iterate on scenarios based on test results
- Reuse and modify existing scenarios
- Collaborate with system engineers on test planning

### Secondary Users: System Engineers

**Profile:**
- Education: B.Sc./M.Sc. in Systems Engineering
- Experience: 5+ years in defense/maritime systems
- Technical Skills: Requirements analysis, system architecture
- Domain Knowledge: Deep understanding of TMM algorithms and CDA system

**Usage Patterns:**
- Define high-level scenario requirements
- Review scenarios for technical correctness
- Create complex edge-case scenarios
- Validate scenarios against system requirements

## 2.4 Operating Environment

### Hardware Environment
- **Platform**: Desktop workstation or laptop
- **Processor**: x86_64 dual-core minimum, quad-core recommended
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 500 MB for application, 10 GB for map cache and projects
- **Display**: 1920x1080 resolution minimum, dual-monitor recommended
- **Input**: Mouse/trackpad, keyboard

### Software Environment
- **Operating System**: 
  - Windows 10/11 (64-bit)
  - Ubuntu 22.04+ (64-bit)
  - macOS 12+ (optional)
- **Runtime**: Python 3.10+ or standalone executable
- **Dependencies**:
  - Map rendering library (e.g., Folium, Leaflet.js)
  - JSON processing libraries
  - GUI framework (e.g., PyQt6, Electron)

### Network Environment
- **Internet Connection**: Optional (for online map tiles)
- **Offline Mode**: Supported with cached map tiles
- **Firewall**: No special requirements (standalone application)

## 2.5 Design and Implementation Constraints

### C1: Standards Compliance
- Output JSON must conform to World Simulator specification v0.6.0+
- Coordinate system must use WGS84 geodetic standard
- MMSI format must comply with ITU-R M.1371
- Distance/bearing calculations must use WGS84 ellipsoid model

### C2: Technology Constraints
- Application must run on standard desktop hardware (no specialized equipment)
- Map data must be obtainable from free/open sources (OpenStreetMap)
- No cloud services or external APIs required for core functionality

### C3: Performance Constraints
- Application startup time < 5 seconds
- Map rendering latency < 200 ms for pan/zoom operations
- JSON export time < 2 seconds for scenarios with 100 targets
- Memory footprint < 1 GB during normal operation

### C4: Usability Constraints
- Interface must be intuitive for first-time users with minimal training
- Common operations (add target, set waypoint) must require ≤ 3 clicks
- Visual feedback must be provided within 100 ms of user actions

### C5: Data Format Constraints
- JSON output must be human-readable (pretty-printed, not minified)
- File sizes must remain manageable (< 10 MB per scenario typically)
- Forward/backward compatibility with simulator versions

## 2.6 Assumptions and Dependencies

### Assumptions

**A1**: Users have basic familiarity with maritime navigation concepts (bearing, range, knots, nautical miles).

**A2**: Test scenarios will primarily focus on surface vessels; underwater or aerial targets are out of scope for initial release.

**A3**: Own Ship is assumed to have functional sensor suite (RADAR, AIS receiver, GPS, gyroscope, speed log).

**A4**: Map tile services (OpenStreetMap or equivalent) will remain freely available.

**A5**: JSON schema for simulator input will remain stable or provide backward compatibility.

**A6**: Typical scenarios will contain 2-50 targets; support for 100+ targets is a stretch goal.

### Dependencies

**D1**: **Python Ecosystem** (if implemented in Python): Availability of PyQt6, Folium, pandas, numpy libraries.

**D2**: **Map Tile Providers**: Continued availability of OpenStreetMap tiles or alternative free map services.

**D3**: **World Simulator**: Compatibility with output JSON format; simulator must accept generated scenarios.

**D4**: **Operating System**: Stable OS releases with no breaking changes to GUI frameworks.

**D5**: **User Training**: Availability of user documentation and training materials to onboard new users.

---

# 3. System Features

## 3.1 Scenario Configuration

**Description:**  
The Scenario Configuration feature provides global settings that define the overall test scenario, including metadata, simulation parameters, and Own Ship configuration.

**Priority:** High  
**Stimulus/Response Sequences:**
1. User selects "New Scenario" from File menu
2. System displays Scenario Configuration dialog
3. User enters scenario metadata and parameters
4. System validates inputs and updates scenario model

**Functional Requirements:**

**TSE-FUNC-001**: The system shall allow the user to specify a unique Scenario ID (alphanumeric, max 64 characters).

*Verification Method*: Test  
*Rationale*: Scenario ID is used for file naming and tracking  
*Priority*: High

**TSE-FUNC-002**: The system shall allow the user to enter a scenario title (UTF-8 text, max 128 characters).

*Verification Method*: Test  
*Rationale*: Human-readable scenario description for documentation  
*Priority*: High

**TSE-FUNC-003**: The system shall allow the user to enter a scenario description (UTF-8 text, max 512 characters).

*Verification Method*: Test  
*Rationale*: Detailed explanation of scenario purpose and configuration  
*Priority*: Medium

**TSE-FUNC-004**: The system shall allow the user to specify simulation duration in seconds (range: 10 - 86400 seconds).

*Verification Method*: Test  
*Rationale*: Defines length of scenario execution; 86400s = 24 hours maximum  
*Priority*: High

**TSE-FUNC-005**: The system shall support the following coordinate systems: Geodetic (WGS84).

*Verification Method*: Inspection  
*Rationale*: Aligns with maritime navigation standards and simulator requirements  
*Priority*: High

## 3.2 Own Ship Definition

**Description:**  
Own Ship configuration defines the reference vessel from which all relative positioning measurements are made, as well as the sensor suite available for target detection.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-010**: The system shall allow the user to specify Own Ship initial position as latitude and longitude in decimal degrees.

*Verification Method*: Test  
*Rationale*: Establishes origin for relative coordinate calculations  
*Acceptance Criteria*: Latitude [-90, +90], Longitude [-180, +180]  
*Priority*: High

**TSE-FUNC-011**: The system shall allow the user to specify Own Ship initial speed in knots (range: 0 - 40 knots).

*Verification Method*: Test  
*Rationale*: Defines Own Ship kinematics; 40 knots covers typical naval vessel speeds  
*Priority*: Medium

**TSE-FUNC-012**: The system shall allow the user to specify Own Ship initial course in degrees (range: 0 - 360°).

*Verification Method*: Test  
*Rationale*: Defines Own Ship heading for trajectory calculations  
*Priority*: Medium

**TSE-FUNC-013**: The system shall allow the user to configure Own Ship sensor suite, including: AIS receiver (enabled/disabled), RADAR A (enabled/disabled), RADAR B (enabled/disabled), EO system (enabled/disabled).

*Verification Method*: Test  
*Rationale*: Defines which sensors are available for detecting targets  
*Priority*: High

**TSE-FUNC-014**: The system shall validate Own Ship position is on water (not on land) using land/sea mask.

*Verification Method*: Test  
*Rationale*: Prevents invalid scenarios with Own Ship on land  
*Acceptance Criteria*: Warning if position is on land mass  
*Priority*: Medium

## 3.3 Target Management

**Description:**  
Target Management provides comprehensive tools for defining maritime targets, including positioning, kinematics, physical characteristics, and sensor visibility.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-020**: The system shall support the creation of unlimited targets within a single scenario (practical limit: 1000 targets for performance).

*Verification Method*: Test  
*Rationale*: Enables complex multi-target scenarios  
*Priority*: High

**TSE-FUNC-021**: The system shall allow the user to position targets using relative coordinates: range from Own Ship (meters), bearing from Own Ship (degrees true north).

*Verification Method*: Test  
*Rationale*: Intuitive positioning method; automatic conversion to absolute coordinates  
*Acceptance Criteria*: Range [40m, 20,000m], Bearing [0°, 360°]  
*Priority*: High

**TSE-FUNC-022**: The system shall automatically calculate absolute geographic coordinates (lat/lon) from relative positioning using WGS84 ellipsoid model with accuracy of ±10 meters at ranges up to 20 NM.

*Verification Method*: Analysis  
*Rationale*: Accurate geodetic transformations essential for realistic scenarios  
*Priority*: High

**TSE-FUNC-023**: The system shall assign each target a unique Target ID automatically (format: T1, T2, T3...).

*Verification Method*: Test  
*Rationale*: Ensures target identification in output JSON  
*Priority*: High

**TSE-FUNC-024**: The system shall allow the user to specify target speed in knots (range: 0 - 40 knots).

*Verification Method*: Test  
*Rationale*: Defines target kinematics  
*Priority*: High

**TSE-FUNC-025**: The system shall allow the user to specify target course in degrees (range: 0 - 360°).

*Verification Method*: Test  
*Rationale*: Defines target heading and velocity vector  
*Priority*: High

**TSE-FUNC-026**: The system shall provide predefined vessel types with default dimensions: Small_Boat (10-30m length), Medium_Cargo (50-100m), Large_Cargo (150-250m), Tanker (200-350m), Navigation_Buoy (5m).

*Verification Method*: Inspection  
*Rationale*: Simplifies target definition with realistic defaults  
*Priority*: Medium

**TSE-FUNC-027**: The system shall allow the user to specify custom target dimensions: length (meters), width (meters), height (meters).

*Verification Method*: Test  
*Rationale*: Enables precise target definition when defaults are insufficient  
*Acceptance Criteria*: Length [1m, 500m], Width [1m, 100m], Height [1m, 50m]  
*Priority*: Medium

**TSE-FUNC-028**: The system shall auto-generate unique MMSI numbers for AIS-equipped targets (9-digit format, starting from configurable base).

*Verification Method*: Test  
*Rationale*: Ensures MMSI uniqueness per ITU-R M.1371  
*Priority*: High

**TSE-FUNC-029**: The system shall allow the user to specify AIS class (A, B, or None) for each target.

*Verification Method*: Test  
*Rationale*: Defines AIS visibility and message characteristics  
*Priority*: High

**TSE-FUNC-030**: The system shall allow the user to specify navigation status for each target: Moored, At anchor, Under way using engine, Not under command.

*Verification Method*: Test  
*Rationale*: Provides realistic vessel status per AIS standards  
*Priority*: Low

## 3.4 Waypoint Management

**Description:**  
Waypoint Management enables the definition of multi-point routes for targets with time-varying kinematics, supporting realistic vessel trajectories and maneuvering scenarios.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-040**: The system shall allow the user to add unlimited waypoints to any target's route (practical limit: 100 waypoints per target).

*Verification Method*: Test  
*Rationale*: Supports complex maneuvering scenarios  
*Priority*: High

**TSE-FUNC-041**: The system shall require the first waypoint (WP1) to have Time=0 and match the target's initial position.

*Verification Method*: Test  
*Rationale*: Ensures route continuity from initial state  
*Priority*: High

**TSE-FUNC-042**: The system shall allow the user to specify for each waypoint: time of arrival (seconds from scenario start), position (relative range and bearing), speed at waypoint (knots), course at waypoint (degrees).

*Verification Method*: Test  
*Rationale*: Provides full kinematic control over trajectory  
*Priority*: High

**TSE-FUNC-043**: The system shall calculate and display estimated travel time between consecutive waypoints based on specified speeds.

*Verification Method*: Test  
*Rationale*: Helps users validate route timing consistency  
*Priority*: Medium

**TSE-FUNC-044**: The system shall validate waypoint sequences for timing consistency (waypoint times must be monotonically increasing).

*Verification Method*: Test  
*Rationale*: Prevents impossible backward-in-time routes  
*Priority*: High

**TSE-FUNC-045**: The system shall visualize routes on the map as connected line segments with directional arrows and waypoint markers.

*Verification Method*: Demonstration  
*Rationale*: Provides visual feedback of target trajectories  
*Priority*: Medium

**TSE-FUNC-046**: The system shall support route copying/pasting between targets to accelerate scenario creation.

*Verification Method*: Test  
*Rationale*: Improves user efficiency for similar routes  
*Priority*: Low

## 3.5 Sensor Configuration

**Description:**  
Sensor Configuration defines which detection sensors can observe each target and enables the specification of temporal visibility windows (sensor dropouts) for testing sensor failure modes.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-050**: The system shall allow the user to enable/disable the following sensors per target: AIS (Class A or B), RADAR A, RADAR B, Electro-Optical (EO).

*Verification Method*: Test  
*Rationale*: Controls target observability by Own Ship sensors  
*Priority*: High

**TSE-FUNC-051**: The system shall allow the user to define sensor dropout periods with: sensor type, start time (seconds), end time (seconds).

*Verification Method*: Test  
*Rationale*: Simulates sensor occlusion, clutter, or failure scenarios  
*Priority*: High

**TSE-FUNC-052**: The system shall support multiple non-overlapping dropout periods for each sensor-target combination.

*Verification Method*: Test  
*Rationale*: Enables complex intermittent visibility scenarios  
*Priority*: Medium

**TSE-FUNC-053**: The system shall validate that dropout periods fall within the scenario duration.

*Verification Method*: Test  
*Rationale*: Prevents invalid dropout definitions  
*Priority*: High

**TSE-FUNC-054**: The system shall warn the user if all sensors are simultaneously dropped out for any target (risk of track loss).

*Verification Method*: Test  
*Rationale*: Highlights potential unintended scenario configurations  
*Acceptance Criteria*: Warning dialog with option to proceed or modify  
*Priority*: Medium

**TSE-FUNC-055**: The system shall support a special "end time" value of -1 to indicate dropout persists until scenario end.

*Verification Method*: Test  
*Rationale*: Simplifies definition of permanent sensor loss  
*Priority*: Low

## 3.6 Map Visualization

**Description:**  
Map Visualization provides an interactive, geospatial view of the scenario layout, enabling intuitive target placement, route planning, and spatial relationship analysis.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-060**: The system shall display a zoomable, pannable map with geographic coordinates using OpenStreetMap or equivalent tile provider.

*Verification Method*: Demonstration  
*Rationale*: Provides geospatial context for scenario layout  
*Priority*: High

**TSE-FUNC-061**: The system shall display Own Ship position as a distinct marker with heading indicator.

*Verification Method*: Demonstration  
*Rationale*: Establishes reference point for relative positioning  
*Priority*: High

**TSE-FUNC-062**: The system shall display all targets as markers with target ID labels and vessel icons proportional to vessel size category.

*Verification Method*: Demonstration  
*Rationale*: Provides clear visualization of target locations  
*Priority*: High

**TSE-FUNC-063**: The system shall display range rings around Own Ship at configurable intervals (default: 1 NM, 5 NM, 10 NM).

*Verification Method*: Demonstration  
*Rationale*: Aids in range estimation and sensor coverage assessment  
*Priority*: Medium

**TSE-FUNC-064**: The system shall display bearing lines from Own Ship to each target when selected.

*Verification Method*: Demonstration  
*Rationale*: Visualizes relative bearing for positioning  
*Priority*: Medium

**TSE-FUNC-065**: The system shall display target routes as polylines with waypoint markers and time labels.

*Verification Method*: Demonstration  
*Rationale*: Shows target trajectories and timing  
*Priority*: High

**TSE-FUNC-066**: The system shall support interactive target placement by clicking on the map.

*Verification Method*: Test  
*Rationale*: Provides intuitive positioning method alternative to manual entry  
*Priority*: High

**TSE-FUNC-067**: The system shall support interactive waypoint placement by clicking on the map when a target is selected.

*Verification Method*: Test  
*Rationale*: Simplifies route definition  
*Priority*: High

**TSE-FUNC-068**: The system shall display sensor coverage zones when applicable: RADAR coverage (11 NM radius), EO field-of-view cone (if directional).

*Verification Method*: Demonstration  
*Rationale*: Visualizes detection capabilities  
*Priority*: Low

**TSE-FUNC-069**: The system shall provide map layer controls to show/hide: targets, routes, range rings, sensor coverage.

*Verification Method*: Test  
*Rationale*: Reduces visual clutter for complex scenarios  
*Priority*: Medium

**TSE-FUNC-070**: The system shall support offline mode using cached map tiles.

*Verification Method*: Test  
*Rationale*: Enables usage without internet connectivity  
*Priority*: Low

## 3.7 JSON Export

**Description:**  
JSON Export functionality generates well-formed JSON configuration files conforming to the World Simulator input specification, enabling seamless handoff from scenario design to simulation execution.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-080**: The system shall export scenarios as JSON files conforming to World Simulator specification v0.6.0+.

*Verification Method*: Inspection  
*Rationale*: Ensures simulator compatibility  
*Priority*: High

**TSE-FUNC-081**: The system shall include the following top-level JSON fields: version, title, description, coordinates, boats (array), stopping (object).

*Verification Method*: Inspection  
*Rationale*: Required by simulator specification  
*Priority*: High

**TSE-FUNC-082**: The system shall generate a "boats" array containing all targets with fields: boat_name, color, vessel_definition, safe_radius, speed[m/s], course, ROT, position (lat/lon), route (waypoint array), algorithm, sensors (object), nav_status, static (object with MMSI and dimensions).

*Verification Method*: Inspection  
*Rationale*: Complete target representation per simulator requirements  
*Priority*: High

**TSE-FUNC-083**: The system shall automatically convert speeds from knots to meters per second (1 knot = 0.51444 m/s).

*Verification Method*: Test  
*Rationale*: Simulator expects m/s units  
*Priority*: High

**TSE-FUNC-084**: The system shall calculate vessel dimensions sub-fields (a, b, c, d) from length and width: a = b = length/2, c = d = width/2.

*Verification Method*: Test  
*Rationale*: Simulator uses specific dimension representation  
*Priority*: High

**TSE-FUNC-085**: The system shall generate sensor configuration with "active" boolean and "inactive_time" arrays of [start, end] tuples.

*Verification Method*: Inspection  
*Rationale*: Defines sensor visibility windows  
*Priority*: High

**TSE-FUNC-086**: The system shall assign target colors: "blue" for moving targets (speed > 0), "yellow" for stationary targets (speed = 0).

*Verification Method*: Test  
*Rationale*: Visual differentiation in simulator  
*Priority*: Low

**TSE-FUNC-087**: The system shall format JSON with indentation (2 or 4 spaces) for human readability.

*Verification Method*: Inspection  
*Rationale*: Facilitates manual review and debugging  
*Priority*: Medium

**TSE-FUNC-088**: The system shall validate exported JSON against a JSON schema before writing to file.

*Verification Method*: Test  
*Rationale*: Catches format errors before simulator execution  
*Priority*: High

**TSE-FUNC-089**: The system shall provide an export preview dialog showing the generated JSON before saving.

*Verification Method*: Demonstration  
*Rationale*: Allows user verification before committing  
*Priority*: Medium

## 3.8 Scenario Validation

**Description:**  
Scenario Validation performs comprehensive checks on scenario configuration to detect errors, inconsistencies, and unrealistic parameters before export, preventing simulation failures and wasted testing time.

**Priority:** High

**Functional Requirements:**

**TSE-FUNC-100**: The system shall validate that all Target IDs are unique within a scenario.

*Verification Method*: Test  
*Rationale*: Prevents identifier conflicts  
*Priority*: High

**TSE-FUNC-101**: The system shall validate that all MMSI numbers are unique within a scenario.

*Verification Method*: Test  
*Rationale*: Complies with AIS uniqueness requirement  
*Priority*: High

**TSE-FUNC-102**: The system shall validate that target positions are within RADAR range of Own Ship (< 11 NM) or provide a warning.

*Verification Method*: Test  
*Rationale*: Targets beyond RADAR range may not be detected  
*Acceptance Criteria*: Warning message with option to proceed  
*Priority*: Medium

**TSE-FUNC-103**: The system shall validate minimum separation distance between targets (configurable, default 50 meters) and warn if violated.

*Verification Method*: Test  
*Rationale*: Prevents unintended collisions or merge scenarios  
*Priority*: High

**TSE-FUNC-104**: The system shall validate that target speeds are realistic (0-40 knots) and issue warnings for speeds > 30 knots.

*Verification Method*: Test  
*Rationale*: Flags potentially unrealistic configurations  
*Priority*: Medium

**TSE-FUNC-105**: The system shall validate that waypoint arrival times are achievable given distance and speed (considering straight-line travel).

*Verification Method*: Test  
*Rationale*: Prevents physically impossible routes  
*Acceptance Criteria*: Calculate required average speed; warn if > 40 knots  
*Priority*: High

**TSE-FUNC-106**: The system shall validate that sensor dropout periods do not overlap for the same sensor-target combination.

*Verification Method*: Test  
*Rationale*: Dropout overlaps indicate configuration error  
*Priority*: Medium

**TSE-FUNC-107**: The system shall validate that scenario duration is sufficient for all waypoint routes to complete.

*Verification Method*: Test  
*Rationale*: Warns of truncated trajectories  
*Priority*: Medium

**TSE-FUNC-108**: The system shall provide a validation report dialog listing all errors and warnings with severity levels (Error, Warning, Info).

*Verification Method*: Demonstration  
*Rationale*: Clear communication of validation results  
*Priority*: High

**TSE-FUNC-109**: The system shall prevent JSON export if critical errors exist; allow export with warnings after user confirmation.

*Verification Method*: Test  
*Rationale*: Ensures minimum quality threshold  
*Priority*: High

---

# 4. Functional Requirements

## 4.1 Scenario Creation and Management

**TSE-FUNC-110**: The system shall provide a "New Scenario" function that initializes a blank scenario with default parameters.

*Verification Method*: Test  
*Rationale*: Starting point for all scenario creation  
*Default Parameters*: Duration=60s, Own Ship at (32.08, 34.78), Speed=0  
*Priority*: High

**TSE-FUNC-111**: The system shall provide a "Save Project" function that persists the current scenario to a TSE project file (.tse format).

*Verification Method*: Test  
*Rationale*: Enables work-in-progress preservation  
*Priority*: High

**TSE-FUNC-112**: The system shall provide a "Load Project" function that restores a scenario from a TSE project file.

*Verification Method*: Test  
*Rationale*: Enables scenario reuse and modification  
*Priority*: High

**TSE-FUNC-113**: The system shall provide a "Save As" function to create a copy of the current scenario with a new name.

*Verification Method*: Test  
*Rationale*: Facilitates scenario variant creation  
*Priority*: Medium

**TSE-FUNC-114**: The system shall prompt the user to save unsaved changes when closing a scenario or exiting the application.

*Verification Method*: Test  
*Rationale*: Prevents data loss  
*Priority*: High

**TSE-FUNC-115**: The system shall maintain a recent files list (up to 10 entries) for quick access.

*Verification Method*: Test  
*Rationale*: Improves user efficiency  
*Priority*: Low

## 4.2 Target Definition

**TSE-FUNC-120**: The system shall provide an "Add Target" function accessible via toolbar button, menu, or map right-click.

*Verification Method*: Test  
*Rationale*: Primary method for populating scenarios  
*Priority*: High

**TSE-FUNC-121**: The system shall display a target properties dialog when a new target is added, with fields for all target parameters.

*Verification Method*: Demonstration  
*Rationale*: Centralized target configuration interface  
*Priority*: High

**TSE-FUNC-122**: The system shall allow bulk target creation by specifying count and distribution pattern (e.g., "create 10 targets in a grid at 1 NM spacing").

*Verification Method*: Test  
*Rationale*: Accelerates large scenario creation  
*Priority*: Low

**TSE-FUNC-123**: The system shall provide a "Duplicate Target" function that creates a copy of selected target with offset position.

*Verification Method*: Test  
*Rationale*: Simplifies creation of similar targets  
*Priority*: Medium

**TSE-FUNC-124**: The system shall provide a "Delete Target" function with confirmation prompt.

*Verification Method*: Test  
*Rationale*: Scenario cleanup capability  
*Priority*: High

**TSE-FUNC-125**: The system shall allow batch selection of multiple targets for coordinated editing (e.g., apply same sensor config to all selected).

*Verification Method*: Test  
*Rationale*: Efficiency for large scenarios  
*Priority*: Low

## 4.3 Route Planning

**TSE-FUNC-130**: The system shall display a "Route Editor" panel when a target with speed > 0 is selected.

*Verification Method*: Demonstration  
*Rationale*: Contextual UI for moving targets  
*Priority*: High

**TSE-FUNC-131**: The system shall allow waypoint addition by clicking on the map when Route Editor is active.

*Verification Method*: Test  
*Rationale*: Intuitive visual route planning  
*Priority*: High

**TSE-FUNC-132**: The system shall display waypoint properties (time, position, speed, course) in a table or list view.

*Verification Method*: Demonstration  
*Rationale*: Detailed waypoint inspection and editing  
*Priority*: High

**TSE-FUNC-133**: The system shall allow waypoint reordering by drag-and-drop in the waypoint list.

*Verification Method*: Test  
*Rationale*: Easy route sequence adjustment  
*Priority*: Medium

**TSE-FUNC-134**: The system shall allow waypoint deletion with automatic route segment recalculation.

*Verification Method*: Test  
*Rationale*: Route refinement capability  
*Priority*: High

**TSE-FUNC-135**: The system shall automatically calculate intermediate waypoint times based on distance and speed if user only specifies positions.

*Verification Method*: Test  
*Rationale*: Simplifies route definition  
*Acceptance Criteria*: Assume constant speed between waypoints  
*Priority*: Medium

**TSE-FUNC-136**: The system shall display route metrics: total distance, total duration, average speed.

*Verification Method*: Demonstration  
*Rationale*: Route feasibility assessment  
*Priority*: Low

## 4.4 Sensor and Dropout Configuration

**TSE-FUNC-140**: The system shall display a "Sensor Configuration" panel in target properties dialog with checkboxes for each sensor type.

*Verification Method*: Demonstration  
*Rationale*: Clear sensor enable/disable interface  
*Priority*: High

**TSE-FUNC-141**: The system shall display a "Dropout Schedule" table for each target, listing all configured dropouts.

*Verification Method*: Demonstration  
*Rationale*: Overview of visibility windows  
*Priority*: High

**TSE-FUNC-142**: The system shall allow dropout addition via "Add Dropout" button, opening a dialog with sensor type, start time, and end time fields.

*Verification Method*: Test  
*Rationale*: Structured dropout definition  
*Priority*: High

**TSE-FUNC-143**: The system shall validate dropout time ranges (start < end, both within scenario duration) and display error messages for invalid entries.

*Verification Method*: Test  
*Rationale*: Prevents invalid dropout definitions  
*Priority*: High

**TSE-FUNC-144**: The system shall visualize dropout periods as timelines or Gantt charts (optional advanced feature).

*Verification Method*: Demonstration  
*Rationale*: Enhanced dropout schedule comprehension  
*Priority*: Low

**TSE-FUNC-145**: The system shall allow dropout copying between targets.

*Verification Method*: Test  
*Rationale*: Efficiency for synchronized dropouts  
*Priority*: Low

## 4.5 Geographic Calculations

**TSE-FUNC-150**: The system shall use the WGS84 ellipsoid model for all distance and bearing calculations.

*Verification Method*: Analysis  
*Rationale*: Geodetic accuracy standard  
*Priority*: High

**TSE-FUNC-151**: The system shall implement the Haversine formula for distance calculations with accuracy of ±0.5% for distances up to 20 NM.

*Verification Method*: Test  
*Rationale*: Adequate accuracy for maritime scenarios  
*Priority*: High

**TSE-FUNC-152**: The system shall calculate forward azimuth (bearing from point A to point B) using WGS84 geodesics.

*Verification Method*: Test  
*Rationale*: Accurate bearing calculations  
*Priority*: High

**TSE-FUNC-153**: The system shall provide a utility function to calculate destination point given origin, range, and bearing (inverse geodetic problem).

*Verification Method*: Test  
*Rationale*: Core transformation for relative positioning  
*Priority*: High

**TSE-FUNC-154**: The system shall account for latitude in longitude-to-meters conversion (meters per degree longitude = 111320 * cos(latitude)).

*Verification Method*: Analysis  
*Rationale*: Accurate east-west distance calculations  
*Priority*: High

## 4.6 Data Persistence

**TSE-FUNC-160**: The system shall save TSE project files in JSON or XML format with complete scenario state.

*Verification Method*: Inspection  
*Rationale*: Human-readable, editable format  
*Priority*: High

**TSE-FUNC-161**: The system shall include metadata in project files: creation date, last modified date, TSE version, author (optional).

*Verification Method*: Inspection  
*Rationale*: Project tracking and version compatibility  
*Priority*: Medium

**TSE-FUNC-162**: The system shall implement file format versioning to support backward compatibility with older TSE project files.

*Verification Method*: Test  
*Rationale*: Enables upgrade path without data loss  
*Priority*: Medium

**TSE-FUNC-163**: The system shall detect file corruption on load and display an error message with recovery options (if possible).

*Verification Method*: Test  
*Rationale*: Robustness against file system errors  
*Priority*: Medium

**TSE-FUNC-164**: The system shall automatically create backup copies of project files before saving (configurable, default: keep 3 backups).

*Verification Method*: Test  
*Rationale*: Protection against save errors or user mistakes  
*Priority*: Low

---

# 5. External Interface Requirements

## 5.1 User Interfaces

### UI-001: Main Application Window

**TSE-UI-001**: The system shall display a main window with the following layout: Menu bar at top, Toolbar below menu bar, Map view occupying central area (≥60% of window width), Scenario tree/outline panel on left (≤20% width), Properties/configuration panel on right (≤25% width), Status bar at bottom.

*Verification Method*: Demonstration  
*Rationale*: Standard multi-panel IDE-style layout  
*Priority*: High

**TSE-UI-002**: The system shall provide resizable and collapsible side panels.

*Verification Method*: Test  
*Rationale*: User customization of workspace  
*Priority*: Medium

**TSE-UI-003**: The system shall save and restore window layout preferences between sessions.

*Verification Method*: Test  
*Rationale*: Consistency across usage sessions  
*Priority*: Low

### UI-002: Menu Structure

**TSE-UI-010**: The system shall provide a "File" menu with items: New Scenario, Open Project, Save Project, Save As, Export JSON, Recent Files, Exit.

*Verification Method*: Inspection  
*Priority*: High

**TSE-UI-011**: The system shall provide an "Edit" menu with items: Undo, Redo, Cut, Copy, Paste, Delete, Select All.

*Verification Method*: Inspection  
*Priority*: Medium

**TSE-UI-012**: The system shall provide a "Scenario" menu with items: Scenario Properties, Add Target, Validate Scenario.

*Verification Method*: Inspection  
*Priority*: High

**TSE-UI-013**: The system shall provide a "View" menu with items: Zoom In, Zoom Out, Fit All, Show/Hide Panels, Map Layers.

*Verification Method*: Inspection  
*Priority*: Medium

**TSE-UI-014**: The system shall provide a "Help" menu with items: User Guide, About.

*Verification Method*: Inspection  
*Priority*: Low

### UI-003: Toolbar

**TSE-UI-020**: The system shall provide a toolbar with icon buttons for: New, Open, Save, Add Target, Delete Target, Validate, Export JSON.

*Verification Method*: Demonstration  
*Rationale*: Quick access to common operations  
*Priority*: High

**TSE-UI-021**: The system shall display tooltips on mouse hover over toolbar buttons.

*Verification Method*: Test  
*Rationale*: Discoverability for new users  
*Priority*: Medium

### UI-004: Map Interface

**TSE-UI-030**: The system shall display map controls for zoom (+/-), pan (arrow keys or drag), and fit-to-bounds.

*Verification Method*: Demonstration  
*Priority*: High

**TSE-UI-031**: The system shall display a scale bar and coordinates of mouse cursor position.

*Verification Method*: Demonstration  
*Rationale*: Spatial awareness and measurement  
*Priority*: Medium

**TSE-UI-032**: The system shall highlight targets and waypoints on mouse hover with tooltips showing key properties.

*Verification Method*: Demonstration  
*Rationale*: Contextual information without cluttering map  
*Priority*: Medium

**TSE-UI-033**: The system shall support map layer toggling via checkboxes or buttons: Base Map, Targets, Routes, Range Rings, Sensor Coverage.

*Verification Method*: Test  
*Priority*: Medium

### UI-005: Dialog Boxes

**TSE-UI-040**: The system shall display modal dialog boxes for: Scenario Properties, Target Properties, Waypoint Properties, Dropout Configuration, Validation Results, Export Options.

*Verification Method*: Demonstration  
*Rationale*: Focused data entry and configuration  
*Priority*: High

**TSE-UI-041**: The system shall provide "OK", "Cancel", and "Apply" buttons in property dialogs where appropriate.

*Verification Method*: Inspection  
*Rationale*: Standard dialog interaction pattern  
*Priority*: High

**TSE-UI-042**: The system shall display validation feedback (red border, error icon) for invalid fields in dialogs before accepting user input.

*Verification Method*: Test  
*Rationale*: Immediate error detection  
*Priority*: High

### UI-006: Accessibility

**TSE-UI-050**: The system shall support keyboard shortcuts for common operations (Ctrl+N, Ctrl+O, Ctrl+S, Delete, etc.).

*Verification Method*: Test  
*Rationale*: Efficiency for power users  
*Priority*: Medium

**TSE-UI-051**: The system shall provide tab navigation through form fields.

*Verification Method*: Test  
*Rationale*: Keyboard-only navigation  
*Priority*: Medium

**TSE-UI-052**: The system shall use high-contrast colors for UI elements to ensure readability (WCAG 2.1 AA compliance).

*Verification Method*: Inspection  
*Rationale*: Accessibility for visually impaired users  
*Priority*: Low

## 5.2 Software Interfaces

### SI-001: Map Tile Provider

**TSE-INTF-001**: The system shall interface with OpenStreetMap tile servers using standard XYZ tile protocol (https://tile.openstreetmap.org/{z}/{x}/{y}.png).

*Verification Method*: Test  
*Rationale*: Free, widely available map data  
*Priority*: High

**TSE-INTF-002**: The system shall cache downloaded map tiles locally to reduce network usage and enable offline operation.

*Verification Method*: Test  
*Rationale*: Performance and offline capability  
*Cache Location*: User application data directory  
*Priority*: Medium

**TSE-INTF-003**: The system shall support alternative tile providers via configuration (e.g., Google Maps, Mapbox) if API keys are provided.

*Verification Method*: Test  
*Rationale*: Flexibility for different user environments  
*Priority*: Low

### SI-002: File System

**TSE-INTF-010**: The system shall read and write TSE project files (.tse) to the local file system using standard file I/O operations.

*Verification Method*: Test  
*Priority*: High

**TSE-INTF-011**: The system shall export JSON files to user-specified locations with .json extension.

*Verification Method*: Test  
*Priority*: High

**TSE-INTF-012**: The system shall handle file access errors gracefully (e.g., insufficient permissions, disk full) with user-friendly error messages.

*Verification Method*: Test  
*Rationale*: Robustness  
*Priority*: Medium

### SI-003: JSON Schema Validation

**TSE-INTF-020**: The system shall validate exported JSON against a JSON schema file (simulator_input_schema.json) using a JSON schema validator library.

*Verification Method*: Test  
*Rationale*: Ensures conformance to simulator requirements  
*Priority*: High

**TSE-INTF-021**: The system shall provide detailed error messages if JSON validation fails, including field names and error descriptions.

*Verification Method*: Test  
*Rationale*: Facilitates debugging of export errors  
*Priority*: High

## 5.3 Hardware Interfaces

**TSE-INTF-030**: The system shall utilize standard display output via operating system graphics APIs (no specialized display hardware required).

*Verification Method*: Inspection  
*Priority*: High

**TSE-INTF-031**: The system shall utilize standard input devices (mouse, keyboard) via operating system input APIs.

*Verification Method*: Inspection  
*Priority*: High

**TSE-INTF-032**: The system shall not require specialized hardware (e.g., GPS receivers, touchscreens, game controllers).

*Verification Method*: Inspection  
*Rationale*: Broad hardware compatibility  
*Priority*: High

## 5.4 Communications Interfaces

**TSE-INTF-040**: The system shall communicate with map tile servers over HTTPS on port 443.

*Verification Method*: Test  
*Rationale*: Standard web protocol  
*Priority*: High

**TSE-INTF-041**: The system shall respect HTTP cache headers and implement tile caching per tile server policies.

*Verification Method*: Test  
*Rationale*: Compliance with tile provider terms of service  
*Priority*: Medium

**TSE-INTF-042**: The system shall not require any other network communication for core functionality (no telemetry, cloud services, or updates).

*Verification Method*: Inspection  
*Rationale*: Privacy and offline operation  
*Priority*: High

---

# 6. Performance Requirements

## 6.1 Response Time

**TSE-PERF-001**: The system shall start up (from launch to main window display) in ≤ 5 seconds on hardware meeting minimum specifications.

*Verification Method*: Test  
*Measurement*: Time from process start to window ready state  
*Priority*: High

**TSE-PERF-002**: The system shall respond to user input (button click, menu selection) within 100 milliseconds.

*Verification Method*: Test  
*Measurement*: Time from input event to visual feedback  
*Rationale*: Perceived instant responsiveness  
*Priority*: High

**TSE-PERF-003**: The system shall render map pan/zoom operations within 200 milliseconds at 95th percentile.

*Verification Method*: Test  
*Measurement*: Time from pan/zoom request to map redraw complete  
*Rationale*: Smooth map interaction  
*Priority*: High

**TSE-PERF-004**: The system shall update target positions on map within 50 milliseconds after parameter changes.

*Verification Method*: Test  
*Measurement*: Time from field value change to map marker update  
*Priority*: Medium

**TSE-PERF-005**: The system shall complete JSON export for scenarios with ≤100 targets within 2 seconds.

*Verification Method*: Test  
*Measurement*: Time from "Export" button click to file written to disk  
*Priority*: High

## 6.2 Throughput

**TSE-PERF-010**: The system shall support creation and management of scenarios containing up to 1000 targets without performance degradation.

*Verification Method*: Test  
*Acceptance Criteria*: Map rendering remains ≤ 200ms, UI responsiveness ≤ 100ms  
*Priority*: Medium

**TSE-PERF-011**: The system shall support routes with up to 100 waypoints per target without performance degradation.

*Verification Method*: Test  
*Rationale*: Supports complex maneuvering scenarios  
*Priority*: Low

**TSE-PERF-012**: The system shall handle map tile loading at a rate of ≥ 50 tiles per second when zooming or panning.

*Verification Method*: Test  
*Rationale*: Smooth map interaction even at high zoom levels  
*Priority*: Medium

## 6.3 Capacity

**TSE-PERF-020**: The system shall support scenario durations up to 24 hours (86,400 seconds) without overflow or precision issues.

*Verification Method*: Test  
*Rationale*: Long-duration testing scenarios  
*Priority*: Medium

**TSE-PERF-021**: The system shall limit project file size to ≤ 100 MB for scenarios with 1000 targets and 100 waypoints each.

*Verification Method*: Test  
*Rationale*: Manageable file sizes for version control and transfer  
*Priority*: Low

**TSE-PERF-022**: The system shall cache up to 10,000 map tiles (approximately 2 GB) before evicting least-recently-used tiles.

*Verification Method*: Test  
*Rationale*: Balance between offline capability and disk usage  
*Priority*: Medium

## 6.4 Resource Utilization

**TSE-PERF-030**: The system shall consume ≤ 1 GB of RAM during normal operation (scenario with 100 targets).

*Verification Method*: Test  
*Measurement*: Peak memory usage via OS tools  
*Priority*: High

**TSE-PERF-031**: The system shall consume ≤ 2 GB of RAM for large scenarios (1000 targets).

*Verification Method*: Test  
*Rationale*: Runs on systems with 4 GB total RAM  
*Priority*: Medium

**TSE-PERF-032**: The system shall utilize ≤ 50% of one CPU core during idle state (map displayed, no user interaction).

*Verification Method*: Test  
*Rationale*: Low background resource consumption  
*Priority*: Medium

**TSE-PERF-033**: The system shall utilize ≤ 200% of CPU capacity (2 full cores) during compute-intensive operations (e.g., large JSON export, validation of 1000-target scenario).

*Verification Method*: Test  
*Rationale*: Efficient use of modern multi-core processors  
*Priority*: Medium

---

# 7. Non-Functional Requirements

## 7.1 Usability

**TSE-NF-001**: The system shall enable a trained user to create a basic scenario (Own Ship + 2 targets + 1 route) within 5 minutes.

*Verification Method*: Test (user study)  
*Rationale*: Efficiency metric for common use case  
*Priority*: High

**TSE-NF-002**: The system shall provide context-sensitive help via "?" buttons or help icons in dialogs.

*Verification Method*: Inspection  
*Rationale*: Discoverability of features  
*Priority*: Medium

**TSE-NF-003**: The system shall include a searchable user manual in HTML or PDF format.

*Verification Method*: Inspection  
*Rationale*: Comprehensive reference documentation  
*Priority*: Medium

**TSE-NF-004**: The system shall provide undo/redo for all editing operations with a stack depth of at least 20 actions.

*Verification Method*: Test  
*Rationale*: Error recovery and experimentation  
*Priority*: High

**TSE-NF-005**: The system shall use consistent terminology throughout the UI and documentation (e.g., always "Target" not "Vessel" or "Boat").

*Verification Method*: Inspection  
*Rationale*: Reduces cognitive load  
*Priority*: Medium

**TSE-NF-006**: The system shall display progress indicators (progress bar or spinner) for operations taking > 1 second.

*Verification Method*: Test  
*Rationale*: User feedback for long operations  
*Priority*: Medium

## 7.2 Reliability

**TSE-NF-010**: The system shall have a Mean Time Between Failures (MTBF) of ≥ 100 hours of active use.

*Verification Method*: Test (extended operation)  
*Measurement*: Crashes per usage hour  
*Priority*: High

**TSE-NF-011**: The system shall recover gracefully from exceptions and display user-friendly error messages rather than crashing.

*Verification Method*: Test (fault injection)  
*Rationale*: Robustness  
*Priority*: High

**TSE-NF-012**: The system shall implement auto-save of unsaved work every 5 minutes (configurable) to a temporary file.

*Verification Method*: Test  
*Rationale*: Protection against crashes or power loss  
*Priority*: Medium

**TSE-NF-013**: The system shall detect and recover from auto-save files on startup after an abnormal termination.

*Verification Method*: Test  
*Rationale*: Data recovery  
*Priority*: Medium

**TSE-NF-014**: The system shall validate all user inputs and reject invalid data with clear error messages before processing.

*Verification Method*: Test  
*Rationale*: Prevents garbage-in-garbage-out scenarios  
*Priority*: High

## 7.3 Maintainability

**TSE-NF-020**: The system shall be developed using a modular architecture with clear separation of concerns: UI layer, business logic layer, data access layer.

*Verification Method*: Inspection (code review)  
*Rationale*: Facilitates testing and future enhancements  
*Priority*: High

**TSE-NF-021**: The system shall include unit tests with ≥ 80% code coverage for business logic and calculations.

*Verification Method*: Analysis (coverage report)  
*Rationale*: Ensures correctness and supports refactoring  
*Priority*: Medium

**TSE-NF-022**: The system shall include comprehensive inline code comments and API documentation.

*Verification Method*: Inspection  
*Rationale*: Knowledge transfer and maintenance  
*Priority*: Medium

**TSE-NF-023**: The system shall log errors, warnings, and key user actions to a log file for troubleshooting.

*Verification Method*: Test  
*Log Location*: User application data directory  
*Priority*: Medium

**TSE-NF-024**: The system shall use configuration files (JSON, YAML, or INI) for settings that may vary between deployments (map tile URLs, default parameters, etc.).

*Verification Method*: Inspection  
*Rationale*: Customization without code changes  
*Priority*: Low

## 7.4 Portability

**TSE-NF-030**: The system shall run on Windows 10/11, Ubuntu 22.04+, and optionally macOS 12+ without modification (cross-platform).

*Verification Method*: Test  
*Rationale*: Broad user base support  
*Priority*: High

**TSE-NF-031**: The system shall minimize dependencies on OS-specific APIs and use cross-platform libraries where possible.

*Verification Method*: Inspection  
*Rationale*: Simplifies multi-platform support  
*Priority*: Medium

**TSE-NF-032**: The system shall package as a standalone executable (Windows .exe, Linux AppImage, macOS .app) with all dependencies bundled.

*Verification Method*: Test  
*Rationale*: Simplified installation and deployment  
*Priority*: High

**TSE-NF-033**: The system shall document any platform-specific installation or configuration steps in a README file.

*Verification Method*: Inspection  
*Rationale*: User guidance for deployment  
*Priority*: Medium

---

# 8. Data Models and Specifications

## 8.1 Internal Data Model

The TSE maintains an in-memory data model representing the scenario configuration. The following UML-style class diagram illustrates key entities:

```
Scenario
├── scenario_id: String
├── title: String
├── description: String
├── duration_sec: Integer
├── coordinate_system: String
├── own_ship: OwnShip
├── targets: List<Target>
└── validation_results: ValidationReport

OwnShip
├── position: GeoPosition
├── speed_knots: Float
├── course_deg: Float
└── sensors: SensorSuite

Target
├── target_id: String
├── name: String
├── position: GeoPosition (derived from relative positioning)
├── relative_range_m: Float
├── relative_bearing_deg: Float
├── speed_knots: Float
├── course_deg: Float
├── vessel_type: VesselType
├── dimensions: VesselDimensions
├── mmsi: Integer (9-digit)
├── ais_class: String ('A', 'B', or 'None')
├── nav_status: String
├── route: List<Waypoint>
├── sensors: SensorConfiguration
└── dropouts: List<SensorDropout>

Waypoint
├── index: Integer
├── time_sec: Float
├── position: GeoPosition (derived from relative positioning)
├── relative_range_m: Float
├── relative_bearing_deg: Float
├── speed_knots: Float
└── course_deg: Float

SensorConfiguration
├── ais_enabled: Boolean
├── radar_a_enabled: Boolean
├── radar_b_enabled: Boolean
└── eo_enabled: Boolean

SensorDropout
├── sensor_type: String ('AIS_A', 'RADAR_A', 'RADAR_B', 'EO')
├── start_time_sec: Float
├── end_time_sec: Float
└── dropout_index: Integer

GeoPosition
├── latitude_deg: Float
└── longitude_deg: Float

VesselDimensions
├── length_m: Float
├── width_m: Float
├── height_m: Float
├── a_m: Float (derived: length/2)
├── b_m: Float (derived: length/2)
├── c_m: Float (derived: width/2)
└── d_m: Float (derived: width/2)
```

**TSE-DATA-001**: The system shall maintain the internal data model in memory during active editing, with changes reflected immediately in the UI.

*Verification Method*: Inspection  
*Priority*: High

**TSE-DATA-002**: The system shall serialize the internal data model to JSON or XML format for project file persistence.

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-003**: The system shall implement input validation constraints at the data model level (e.g., speed range 0-40 knots).

*Verification Method*: Test  
*Rationale*: Centralized validation logic  
*Priority*: High

## 8.2 JSON Output Format

The system exports scenarios in JSON format conforming to the World Simulator Input Specification v0.6.0+. 

**Example Output Structure:**

```json
{
  "version": "0.6.0",
  "title": "Test Scenario - 2 Targets Static",
  "description": "Basic fusion test with 2 stationary targets",
  "coordinates": "geodetic",
  "boats": [
    {
      "boat_name": "target1",
      "color": "yellow",
      "vessel_definition": "powered vessel",
      "safe_radius": 300.2,
      "speed[m/s]": 0.0,
      "course": 0,
      "ROT": 0.05,
      "position": {
        "lat": 32.086352,
        "lon": 34.787497
      },
      "route": [
        {"lat": 32.086352, "lon": 34.787497}
      ],
      "algorithm": "dead reckoning",
      "sensors": {
        "AIS_A": {
          "class": "A",
          "active": true,
          "inactive_time": []
        },
        "RADAR_A": {
          "active": true,
          "inactive_time": []
        },
        "RADAR_B": {
          "active": true,
          "inactive_time": []
        }
      },
      "nav_status": "Moored",
      "static": {
        "id": 0,
        "mmsi": 375385000,
        "dimensions": {
          "length": 200.0,
          "width": 32.0,
          "height": 8.0,
          "a": 100.0,
          "b": 100.0,
          "c": 16.0,
          "d": 16.0
        }
      }
    }
  ],
  "stopping": {
    "type": "time",
    "time": {
      "time": 60
    }
  }
}
```

**TSE-DATA-010**: The system shall export JSON with UTF-8 encoding.

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-011**: The system shall format JSON with 2-space indentation for readability.

*Verification Method*: Inspection  
*Priority*: Medium

**TSE-DATA-012**: The system shall include all mandatory fields per simulator specification (version, title, coordinates, boats, stopping).

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-013**: The system shall generate unique sequential "id" values for targets starting from 0.

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-014**: The system shall set "algorithm" field to "dead reckoning" for all targets.

*Verification Method*: Inspection  
*Rationale*: Simulator default trajectory algorithm  
*Priority*: Medium

**TSE-DATA-015**: The system shall set "ROT" (rate of turn) field to 0.05 as default value.

*Verification Method*: Inspection  
*Rationale*: Simulator compatibility  
*Priority*: Low

## 8.3 Coordinate Systems

**TSE-DATA-020**: The system shall use WGS84 geodetic coordinates (latitude, longitude) as the primary coordinate reference system.

*Verification Method*: Inspection  
*Rationale*: Global standard for maritime navigation  
*Priority*: High

**TSE-DATA-021**: The system shall represent latitude in decimal degrees with range [-90°, +90°], positive north.

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-022**: The system shall represent longitude in decimal degrees with range [-180°, +180°], positive east.

*Verification Method*: Test  
*Priority*: High

**TSE-DATA-023**: The system shall store coordinates with precision of at least 6 decimal places (~0.1 meter resolution).

*Verification Method*: Test  
*Rationale*: Sub-meter positioning accuracy  
*Priority*: Medium

**TSE-DATA-024**: The system shall use true north (0°) as the reference for all bearing measurements.

*Verification Method*: Test  
*Rationale*: Maritime navigation convention  
*Priority*: High

**TSE-DATA-025**: The system shall represent bearings as angles in degrees with range [0°, 360°), clockwise from north.

*Verification Method*: Test  
*Priority*: High

---

# 9. Verification and Validation

## 9.1 Verification Methods

This section defines the methods used to verify that the TSE meets its specified requirements.

### V1: Test

**Description**: Execute the system with defined inputs and verify outputs match expected results.

**Applicable Requirements**: Functional requirements, performance requirements, usability requirements.

**Test Types**:
- **Unit Tests**: Verify individual functions and classes (e.g., coordinate transformations, validation logic).
- **Integration Tests**: Verify interactions between components (e.g., UI → business logic → data model).
- **System Tests**: Verify end-to-end workflows (e.g., create scenario → export JSON → validate against simulator).
- **Performance Tests**: Measure response times, throughput, and resource utilization under load.
- **Usability Tests**: Observe users performing representative tasks and collect metrics (time, errors, satisfaction).

**Test Environment**:
- Development workstations (Windows, Linux, macOS)
- Automated CI/CD pipeline for regression testing
- User acceptance testing with representative end users

### V2: Inspection

**Description**: Manual review of artifacts (code, documentation, UI) to verify compliance with requirements.

**Applicable Requirements**: Interface requirements, documentation requirements, standards compliance.

**Inspection Types**:
- **Code Review**: Verify code quality, architecture, and adherence to coding standards.
- **Document Review**: Verify completeness and accuracy of user manuals, help text, and specifications.
- **UI Review**: Verify menu structure, dialog layouts, and visual design against UI requirements.

### V3: Analysis

**Description**: Apply mathematical or logical analysis to verify correctness of algorithms and designs.

**Applicable Requirements**: Calculation accuracy, algorithmic correctness, architectural soundness.

**Analysis Types**:
- **Mathematical Verification**: Verify coordinate transformation algorithms using geodetic reference calculations.
- **Complexity Analysis**: Verify performance characteristics (e.g., O(n) behavior of validation algorithm).
- **Coverage Analysis**: Verify test coverage percentages using code coverage tools.

### V4: Demonstration

**Description**: Operate the system and show that it exhibits required behavior in real time.

**Applicable Requirements**: Visual/interactive requirements (map display, UI responsiveness).

**Demonstration Types**:
- **Feature Demonstrations**: Show stakeholders that key features work as intended.
- **Live Validation**: Demonstrate end-to-end scenario creation and export in front of reviewers.

## 9.2 Requirements Traceability

**TSE-NF-040**: The system development shall maintain a Requirements Traceability Matrix (RTM) linking each requirement to:
- Source (stakeholder need, system requirement, design constraint)
- Implementation (code modules, configuration files)
- Verification method and test cases
- Verification status (Not Started, In Progress, Verified, Failed)

*Verification Method*: Inspection  
*Rationale*: Ensures all requirements are addressed and verified  
*Priority*: High

**Example RTM Entry:**

| Req ID | Requirement | Source | Verification Method | Test Case ID | Status |
|--------|-------------|--------|---------------------|--------------|--------|
| TSE-FUNC-022 | Calculate absolute coordinates from relative positioning | User Need: Intuitive Positioning | Analysis, Test | TC-CALC-001 | Verified |

---

# 10. Appendices

## 10.1 Glossary

| **Term** | **Definition** |
|----------|----------------|
| **AIS** | Automatic Identification System; maritime VHF radio system for vessel identification and tracking. |
| **Bearing** | The horizontal angle (in degrees) from true north to a target, measured clockwise (0-360°). |
| **CDA** | Collision Detection & Avoidance; the overarching naval system for preventing maritime collisions. |
| **Dropout** | A time period during which a sensor does not detect a target (simulating occlusion, clutter, or failure). |
| **EO** | Electro-Optical; a vision-based sensor system (cameras, thermal imaging). |
| **Geodetic Coordinates** | Latitude and longitude specified on an ellipsoidal model of the Earth (e.g., WGS84). |
| **Global Track** | A fused track representing a single physical target, combining data from multiple sensors. |
| **Knot** | Unit of speed equal to one nautical mile per hour (1 knot ≈ 0.51444 m/s). |
| **MMSI** | Maritime Mobile Service Identity; a unique 9-digit identifier for AIS-equipped vessels. |
| **Nautical Mile (NM)** | Unit of distance equal to 1852 meters. |
| **Own Ship** | The reference vessel from which all relative measurements are made (the vessel carrying the CDA system). |
| **RADAR** | RAdio Detection And Ranging; a sensor that uses radio waves to detect and locate objects. |
| **Range** | The distance (typically in meters or nautical miles) from a reference point (usually Own Ship) to a target. |
| **TMM** | Track Management Module; the CDA subsystem responsible for multi-sensor data fusion. |
| **Waypoint** | A geographic position along a route, typically with associated timing and kinematic parameters. |
| **WGS84** | World Geodetic System 1984; the standard coordinate system for GPS and maritime navigation. |

## 10.2 Use Case Diagrams

### UC-001: Create New Scenario

**Actor**: Test Engineer

**Preconditions**: Application is running.

**Main Flow**:
1. User selects "File → New Scenario"
2. System displays Scenario Properties dialog
3. User enters scenario metadata and Own Ship configuration
4. User clicks "OK"
5. System initializes new scenario and displays empty map centered on Own Ship

**Postconditions**: Empty scenario is created and ready for target addition.

### UC-002: Add Target

**Actor**: Test Engineer

**Preconditions**: Scenario is open.

**Main Flow**:
1. User clicks "Add Target" button in toolbar
2. System displays Target Properties dialog
3. User specifies relative position (range, bearing), speed, course, vessel type, and sensor configuration
4. User clicks "OK"
5. System calculates absolute position, assigns unique Target ID and MMSI
6. System adds target to scenario and displays marker on map

**Postconditions**: Target is added to scenario and visible on map.

### UC-003: Define Route with Waypoints

**Actor**: Test Engineer

**Preconditions**: Scenario is open; moving target (speed > 0) is selected.

**Main Flow**:
1. System displays Route Editor panel
2. User clicks on map to add waypoints sequentially
3. For each waypoint, system records position, prompts for speed and course
4. System displays route as polyline with waypoint markers
5. User reviews and adjusts waypoint parameters in Route Editor panel
6. System validates route for timing consistency and reachability

**Postconditions**: Complete route is defined for selected target.

### UC-004: Configure Sensor Dropouts

**Actor**: Test Engineer

**Preconditions**: Scenario is open; target is selected.

**Main Flow**:
1. User opens Target Properties dialog
2. User navigates to "Sensor Dropouts" tab
3. User clicks "Add Dropout"
4. User specifies sensor type, start time, and end time
5. System validates dropout parameters (start < end, within scenario duration)
6. System adds dropout to target configuration
7. User repeats steps 3-6 for additional dropouts

**Postconditions**: Dropout schedule is configured for target.

### UC-005: Validate and Export Scenario

**Actor**: Test Engineer

**Preconditions**: Scenario is defined with Own Ship and at least one target.

**Main Flow**:
1. User selects "Scenario → Validate Scenario"
2. System performs comprehensive validation checks
3. System displays Validation Report with any errors/warnings
4. User reviews validation results; if errors exist, user corrects scenario
5. User selects "File → Export JSON"
6. System displays Export Options dialog (file path, format settings)
7. User specifies output file name and path
8. System generates JSON, validates against schema, writes to file
9. System displays "Export successful" message

**Postconditions**: JSON scenario file is created and ready for simulator.

## 10.3 Example Scenarios

### Example 1: Basic Fusion Test

**Objective**: Verify TMM can fuse data from all sensors for stationary targets.

**Configuration**:
- **Own Ship**: Lat 32.08°, Lon 34.78°, Speed 0 knots
- **Duration**: 60 seconds
- **Target 1**: Range 1000m, Bearing 45°, Speed 0 knots, All sensors enabled
- **Target 2**: Range 1500m, Bearing 270°, Speed 0 knots, All sensors enabled
- **Sensors**: AIS, RADAR A, RADAR B, EO - all active throughout
- **Expected Result**: 2 Global Tracks created with data from all 4 sensors

### Example 2: Moving Targets with Routes

**Objective**: Test track prediction and coasting during sensor dropouts.

**Configuration**:
- **Own Ship**: Lat 32.08°, Lon 34.78°, Speed 0 knots
- **Duration**: 120 seconds
- **Target 1**: 
  - Initial: Range 800m, Bearing 30°, Speed 10 knots, Course 45°
  - Waypoints: WP1 (0s), WP2 (40s), WP3 (80s), WP4 (120s)
- **Target 2**: 
  - Initial: Range 1200m, Bearing 180°, Speed 15 knots, Course 180°
- **Target 3**: 
  - Initial: Range 2000m, Bearing 315°, Speed 8 knots, Course 270°
  - No AIS (only RADAR + EO)
- **Dropout**: RADAR A on Target 2 from 40-60 seconds
- **Expected Result**: 3 Global Tracks with continuous tracking, Target 2 coasts during RADAR A dropout

### Example 3: Complex Multi-Target Scenario

**Objective**: Stress-test TMM with many targets, merges, and dropouts.

**Configuration**:
- **Own Ship**: Moving at 5 knots, course 90°
- **Duration**: 300 seconds
- **Targets**: 20 targets at various ranges (500m - 10 NM) and bearings
- **Routes**: 10 targets have multi-waypoint routes
- **Sensors**: Mixed configuration (some with all sensors, some without AIS, some with intermittent RADAR)
- **Dropouts**: Multiple overlapping dropouts creating complex visibility patterns
- **Expected Result**: All targets tracked, merge/split events handled correctly

---

**END OF DOCUMENT**

---

**Document Approval:**

| **Role** | **Name** | **Date** | **Signature** |
|----------|----------|----------|---------------|
| Author | System Engineering Team | November 2025 | |
| Reviewer | | | |
| Approver | | | |

---

**Distribution List:**
- System Engineering Team
- Software Development Team
- Testing & QA Team
- Project Management
- Stakeholders

---

**Revision History:**

| **Version** | **Date** | **Author** | **Changes** |
|-------------|----------|------------|-------------|
| 1.0 | November 2025 | System Engineering Team | Initial release |

---

**Document Control:**
- **File Name**: TSE-SRS-001_v1.0.md
- **Location**: Project Documentation Repository
- **Classification**: Confidential
- **Retention**: 7 years from project completion
