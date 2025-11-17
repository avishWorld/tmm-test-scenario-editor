"""
Sensor configuration data model classes.

Requirements:
- TSE-FUNC-050: Sensor enable/disable per target
- TSE-FUNC-051: Sensor dropout periods
- TSE-FUNC-052: Multiple non-overlapping dropouts
- TSE-FUNC-053: Dropouts within scenario duration
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class SensorType(Enum):
    """
    Enumeration of sensor types.

    Requirements: TSE-FUNC-050
    """
    AIS_A = "AIS_A"
    AIS_B = "AIS_B"
    RADAR_A = "RADAR_A"
    RADAR_B = "RADAR_B"
    EO = "EO"


@dataclass
class SensorConfiguration:
    """
    Sensor enable/disable configuration for a target.

    Attributes:
        ais_enabled: AIS sensor enabled flag
        radar_a_enabled: RADAR A enabled flag
        radar_b_enabled: RADAR B enabled flag
        eo_enabled: Electro-Optical sensor enabled flag

    Requirements: TSE-FUNC-050
    """
    ais_enabled: bool = True
    radar_a_enabled: bool = True
    radar_b_enabled: bool = True
    eo_enabled: bool = True


@dataclass
class SensorDropout:
    """
    Represents a sensor dropout period (temporal invisibility window).

    Attributes:
        sensor_type: Type of sensor that drops out
        start_time_sec: Dropout start time (seconds from scenario start)
        end_time_sec: Dropout end time (seconds) or -1 for scenario end
        dropout_index: Sequential index of this dropout

    Requirements:
        - TSE-FUNC-051: Dropout period definition
        - TSE-FUNC-055: end_time=-1 for permanent dropout
    """
    sensor_type: SensorType
    start_time_sec: float
    end_time_sec: float  # -1 means until scenario end
    dropout_index: int = 0

    def __post_init__(self):
        """Validate dropout times."""
        if self.start_time_sec < 0:
            raise ValueError("Dropout start time must be >= 0")

        # Allow end_time = -1 for "until scenario end" (TSE-FUNC-055)
        if self.end_time_sec != -1 and self.end_time_sec <= self.start_time_sec:
            raise ValueError("Dropout end time must be > start time (or -1)")

    def overlaps_with(self, other: 'SensorDropout') -> bool:
        """
        Check if this dropout overlaps with another dropout.

        Requirements: TSE-FUNC-106 (overlap validation)
        """
        if self.sensor_type != other.sensor_type:
            return False

        # Handle -1 end times
        self_end = self.end_time_sec if self.end_time_sec != -1 else float('inf')
        other_end = other.end_time_sec if other.end_time_sec != -1 else float('inf')

        return not (self_end <= other.start_time_sec or other_end <= self.start_time_sec)
