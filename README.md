# TMM Test Scenario Editor & Planner (TSE)

**Version:** 0.1.0
**Status:** 🚧 Under Development

Maritime Simulation Scenario Configuration Tool for the Track Management Module (TMM) of the CDA (Collision Detection & Avoidance) Naval System.

---

## Overview

The TSE is a graphical desktop application that enables system engineers and test engineers to efficiently create, visualize, and export complex multi-target maritime test scenarios for the TMM module. It provides an intuitive, map-based interface for scenario planning with automatic coordinate transformations and comprehensive validation.

### Key Features

- **Interactive Map-Based Visualization**: Place targets and plan routes on an OpenStreetMap interface
- **Relative Positioning**: Intuitive target placement using range and bearing from Own Ship
- **Automatic Coordinate Transformation**: Converts relative positions to WGS84 geodetic coordinates
- **Route Planning**: Multi-waypoint routes with time-varying kinematics
- **Sensor Configuration**: Configure AIS, RADAR A/B, and EO sensors with temporal dropout schedules
- **Comprehensive Validation**: Real-time scenario validation against operational and technical constraints
- **JSON Export**: Generates well-formed configuration files for the World Simulator

---

## System Requirements

### Hardware
- **Platform**: Desktop workstation or laptop
- **Processor**: x86_64 dual-core minimum, quad-core recommended
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 500 MB for application, 10 GB for map cache and projects
- **Display**: 1920x1080 resolution minimum, dual-monitor recommended

### Software
- **Operating System**:
  - Windows 10/11 (64-bit)
  - Ubuntu 22.04+ (64-bit)
  - macOS 12+ (optional)
- **Python**: 3.10 or higher (for source installation)
- **Internet Connection**: Optional (for online map tiles)

---

## הנחיות התקנה בעברית / Hebrew Installation Guide

### דרישות מקדימות

לפני שמתחילים, ודא שמותקנים במחשב:
- **Python 3.10 או גרסה חדשה יותר** - [הורד כאן](https://www.python.org/downloads/)
- **Git** - [הורד כאן](https://git-scm.com/downloads)
- **חיבור לאינטרנט** (להורדת תלויות)

### שלב 1: הורדת הפרויקט

פתח חלון Command Prompt / Terminal ובצע:

```bash
# בחר תיקייה שבה תרצה לשמור את הפרויקט
cd Desktop

# שכפל את הפרויקט מ-GitHub
git clone https://github.com/avishWorld/tmm-test-scenario-editor.git

# היכנס לתיקיית הפרויקט
cd tmm-test-scenario-editor
```

**חלופה:** אם אין לך Git, הורד את הפרויקט כקובץ ZIP:
1. לך ל-https://github.com/avishWorld/tmm-test-scenario-editor
2. לחץ על הכפתור הירוק "Code" ⇒ "Download ZIP"
3. חלץ את הקובץ לתיקייה שבחרת
4. פתח Command Prompt / Terminal בתיקייה שחילצת

### שלב 2: יצירת סביבת Python וירטואלית

הפעל בחלון הטרמינל:

```bash
# צור סביבה וירטואלית (מבודדת) לפרויקט
python -m venv venv
```

**הערה:** במערכות מסוימות צריך להשתמש ב-`python3` במקום `python`

### שלב 3: הפעלת הסביבה הוירטואלית

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

לאחר ההפעלה, תראה `(venv)` בתחילת השורה בטרמינל - זה אומר שהסביבה הוירטואלית פעילה.

### שלב 4: התקנת תלויות הפרויקט

```bash
# התקן את כל הספריות הנדרשות
pip install -r requirements.txt
```

**הערה:** התקנה זו עשויה לקחת מספר דקות (במיוחד PyQt6).

### שלב 5: התקנת הפרויקט במצב פיתוח

```bash
# התקן את TSE במצב עריכה (development mode)
pip install -e .
```

### שלב 6: הרצת האפליקציה

יש לך שתי אפשרויות להריץ את התוכנה:

**אפשרות 1:**
```bash
python -m tse.main
```

**אפשרות 2:**
```bash
tse
```

### פתרון בעיות נפוצות

**בעיה: "python is not recognized"**
- ודא ש-Python מותקן ונוסף ל-PATH
- נסה להשתמש ב-`python3` במקום `python`
- התקן מחדש את Python וסמן "Add Python to PATH"

**בעיה: "pip is not recognized"**
- השתמש ב-`python -m pip` במקום `pip`

**בעיה: שגיאות בהתקנת PyQt6**
- ב-Linux: התקן `sudo apt-get install python3-pyqt6`
- ב-macOS: התקן `brew install pyqt6`

**בעיה: שגיאות הרשאות (Permission Denied)**
- אל תשתמש ב-`sudo` עם pip
- ודא שהסביבה הוירטואלית פעילה (צריך לראות `(venv)` בטרמינל)

### עדכון הפרויקט

כדי לקבל את הגרסה העדכנית ביותר:

```bash
# ודא שהסביבה הוירטואלית פעילה
# ב-Windows: venv\Scripts\activate
# ב-Linux/macOS: source venv/bin/activate

# משוך שינויים מ-GitHub
git pull origin main

# עדכן תלויות (במידת הצורך)
pip install -r requirements.txt --upgrade
```

### יציאה מהסביבה הוירטואלית

כאשר מסיימים לעבוד:

```bash
deactivate
```

---

## Installation (English)

### Option 1: From Source (Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/avishWorld/tmm-test-scenario-editor.git
   cd tmm-test-scenario-editor
   ```

2. **Create Python virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install TSE in development mode**:
   ```bash
   pip install -e .
   ```

6. **Run the application**:
   ```bash
   python -m tse.main
   ```
   or
   ```bash
   tse
   ```

### Option 2: Standalone Executable (Coming Soon)

Standalone installers will be available after Phase 10 (Deployment):
- Windows: `.exe` installer
- Linux: `.AppImage`
- macOS: `.app` bundle

---

## Quick Start

1. **Launch the application**
2. **Create a New Scenario**: File → New Scenario
3. **Configure Own Ship**: Set position, speed, course, and sensors
4. **Add Targets**: Click "Add Target" or right-click on map
5. **Position Targets**: Enter range and bearing from Own Ship
6. **Define Routes**: For moving targets, add waypoints by clicking on map
7. **Configure Sensors**: Enable/disable sensors and define dropout windows
8. **Validate Scenario**: Scenario → Validate Scenario
9. **Export JSON**: File → Export JSON

---

## Project Structure

```
tse/
├── main.py                      # Application entry point
├── models/                      # Data model layer
│   ├── scenario.py
│   ├── own_ship.py
│   ├── target.py
│   ├── waypoint.py
│   ├── sensor.py
│   ├── geo.py
│   └── validation_report.py
├── ui/                          # User interface layer
│   ├── main_window.py
│   ├── dialogs/
│   ├── panels/
│   ├── widgets/
│   ├── map_view.py
│   ├── map_layers/
│   └── map_tools/
├── logic/                       # Business logic layer
│   ├── scenario_manager.py
│   ├── route_calculator.py
│   └── undo_stack.py
├── validation/                  # Validation engine
│   ├── validator.py
│   ├── route_validator.py
│   └── dropout_validator.py
├── io/                          # Data access layer
│   ├── project_file.py
│   ├── json_exporter.py
│   └── json_schema_validator.py
├── utils/                       # Utilities
│   ├── geo_calc.py
│   └── unit_conversion.py
└── resources/                   # Resources
    ├── simulator_input_schema.json
    ├── icons/
    └── stylesheets/

tests/                           # Test suite
├── test_models/
├── test_geo/
├── test_validation/
├── test_io/
├── test_logic/
├── test_ui/
├── integration/
└── performance/

docs/                            # Documentation
├── user_manual/
└── api_docs/
```

---

## Development Status

**Current Phase:** Phase 0 - Project Initiation & Planning

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation plan and progress tracking.

### Requirements Status
- **Total Requirements**: 185
- **Completed**: 0 (0%)
- **In Progress**: 0 (0%)
- **Not Started**: 185 (100%)

### Test Coverage
- **Target**: 80%
- **Current**: 0%

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tse --cov-report=html

# Run specific test file
pytest tests/test_models/test_geo.py

# Run performance tests
pytest tests/performance/
```

### Code Quality

```bash
# Format code
black tse/

# Lint code
flake8 tse/

# Type checking
mypy tse/
```

### Building Documentation

```bash
cd docs/
make html
```

---

## Contributing

Development follows the implementation plan defined in [PROJECT_PLAN.md](PROJECT_PLAN.md).

### Coding Standards
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maintain 80%+ test coverage for business logic
- Document all public APIs with docstrings
- Include requirement IDs in comments (e.g., `# TSE-FUNC-022`)

### Git Workflow
- Create feature branches from `main`
- One requirement per commit when possible
- Update PROJECT_PLAN.md with progress
- All tests must pass before merging

---

## Documentation

- **Software Requirements Specification**: [Test_Scenario_Editor_SRS_v1.0.md](Test_Scenario_Editor_SRS_v1.0.md)
- **Implementation Plan**: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **User Manual**: Coming in Phase 10
- **API Documentation**: Coming in Phase 10

---

## Technology Stack

- **Language**: Python 3.10+
- **GUI Framework**: PyQt6
- **Map Visualization**: Folium + Leaflet.js (embedded in QWebEngineView)
- **Geospatial Calculations**: geopy + pyproj (WGS84 ellipsoid)
- **Data Validation**: pydantic + jsonschema
- **Testing**: pytest + pytest-qt
- **Packaging**: PyInstaller

---

## License

[License information to be determined]

---

## Contact

- **Project**: CDA/TMM Testing & Validation
- **Team**: System Engineering Team
- **Status**: Confidential

---

## Acknowledgments

- OpenStreetMap contributors for map tiles
- Python open-source community
- TMM and CDA development teams

---

**Last Updated**: 2025-11-17
**Document Version**: 1.0
