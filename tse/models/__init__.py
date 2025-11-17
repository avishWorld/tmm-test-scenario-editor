"""
Data model classes for the TSE application.

This package contains all domain model classes representing
the scenario, targets, waypoints, sensors, and geographic data.
"""

from .scenario import Scenario
from .own_ship import OwnShip
from .target import Target, VesselType, AISClass, NavigationStatus
from .waypoint import Waypoint
from .sensor import SensorConfiguration, SensorDropout, SensorType
from .geo import GeoPosition, VesselDimensions
from .validation_report import ValidationReport, ValidationMessage, ValidationSeverity

__all__ = [
    # Core Models
    "Scenario",
    "OwnShip",
    "Target",
    "Waypoint",
    # Geographic Models
    "GeoPosition",
    "VesselDimensions",
    # Sensor Models
    "SensorConfiguration",
    "SensorDropout",
    "SensorType",
    # Validation Models
    "ValidationReport",
    "ValidationMessage",
    "ValidationSeverity",
    # Enums
    "VesselType",
    "AISClass",
    "NavigationStatus",
]
