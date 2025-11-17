"""
Geographic data model classes.

Requirements:
- TSE-DATA-020: WGS84 geodetic coordinates
- TSE-DATA-021: Latitude range [-90°, +90°]
- TSE-DATA-022: Longitude range [-180°, +180°]
- TSE-DATA-023: Precision ≥ 6 decimal places
- TSE-DATA-024: True north (0°) reference
- TSE-DATA-025: Bearing range [0°, 360°)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GeoPosition:
    """
    Represents a geographic position using WGS84 coordinates.

    Attributes:
        latitude_deg: Latitude in decimal degrees [-90, +90], positive north
        longitude_deg: Longitude in decimal degrees [-180, +180], positive east

    Requirements:
        - TSE-DATA-020: WGS84 coordinate system
        - TSE-DATA-021: Latitude validation
        - TSE-DATA-022: Longitude validation
        - TSE-DATA-023: 6+ decimal places precision
    """
    latitude_deg: float
    longitude_deg: float

    def __post_init__(self):
        """Validate coordinate ranges."""
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError(f"Latitude {self.latitude_deg} out of range [-90, +90]")
        if not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError(f"Longitude {self.longitude_deg} out of range [-180, +180]")

    def __str__(self) -> str:
        """String representation with 6 decimal places."""
        return f"({self.latitude_deg:.6f}, {self.longitude_deg:.6f})"


@dataclass
class VesselDimensions:
    """
    Represents vessel physical dimensions.

    Attributes:
        length_m: Vessel length in meters
        width_m: Vessel width in meters
        height_m: Vessel height in meters
        a_m: Derived dimension (length/2)
        b_m: Derived dimension (length/2)
        c_m: Derived dimension (width/2)
        d_m: Derived dimension (width/2)

    Requirements:
        - TSE-FUNC-027: Custom dimensions support
        - TSE-FUNC-084: Dimension sub-fields calculation
    """
    length_m: float
    width_m: float
    height_m: float
    a_m: Optional[float] = None
    b_m: Optional[float] = None
    c_m: Optional[float] = None
    d_m: Optional[float] = None

    def __post_init__(self):
        """Calculate derived dimensions."""
        if self.a_m is None:
            self.a_m = self.length_m / 2.0
        if self.b_m is None:
            self.b_m = self.length_m / 2.0
        if self.c_m is None:
            self.c_m = self.width_m / 2.0
        if self.d_m is None:
            self.d_m = self.width_m / 2.0

        # Validate ranges (TSE-FUNC-027)
        if not 1.0 <= self.length_m <= 500.0:
            raise ValueError(f"Length {self.length_m} out of range [1, 500] meters")
        if not 1.0 <= self.width_m <= 100.0:
            raise ValueError(f"Width {self.width_m} out of range [1, 100] meters")
        if not 1.0 <= self.height_m <= 50.0:
            raise ValueError(f"Height {self.height_m} out of range [1, 50] meters")
