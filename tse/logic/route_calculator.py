"""
Route calculation utilities for waypoint-based navigation.

Requirements:
- TSE-FUNC-043: Route distance/time calculations
- TSE-FUNC-135: Route metrics display
- TSE-FUNC-044: Waypoint timing validation
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

from tse.models.waypoint import Waypoint
from tse.utils.geo_calc import haversine_distance, forward_azimuth
from tse.utils.unit_conversion import knots_to_ms, ms_to_knots


@dataclass
class RouteLeg:
    """
    Represents a leg (segment) between two waypoints.

    Attributes:
        from_waypoint: Starting waypoint
        to_waypoint: Ending waypoint
        distance_m: Distance in meters
        bearing_deg: Bearing from start to end in degrees
        required_speed_knots: Required speed to reach next waypoint on time
        time_duration_sec: Time duration for this leg
    """
    from_waypoint: Waypoint
    to_waypoint: Waypoint
    distance_m: float
    bearing_deg: float
    required_speed_knots: float
    time_duration_sec: float


@dataclass
class RouteMetrics:
    """
    Overall route metrics and statistics.

    Attributes:
        total_distance_m: Total route distance in meters
        total_distance_nm: Total route distance in nautical miles
        total_time_sec: Total time duration in seconds
        average_speed_knots: Average speed over entire route
        max_speed_knots: Maximum required speed
        min_speed_knots: Minimum required speed
        num_waypoints: Number of waypoints
        num_legs: Number of route legs
        legs: List of individual route legs
    """
    total_distance_m: float
    total_distance_nm: float
    total_time_sec: float
    average_speed_knots: float
    max_speed_knots: float
    min_speed_knots: float
    num_waypoints: int
    num_legs: int
    legs: List[RouteLeg]


class RouteCalculator:
    """
    Calculates route metrics, timing, and required speeds.

    Requirements: TSE-FUNC-043, TSE-FUNC-135
    """

    # Nautical mile to meters conversion
    NM_TO_METERS = 1852.0

    @staticmethod
    def calculate_route_metrics(waypoints: List[Waypoint]) -> Optional[RouteMetrics]:
        """
        Calculate comprehensive metrics for a route.

        Args:
            waypoints: List of waypoints (must be sorted by time)

        Returns:
            RouteMetrics object or None if route is invalid

        Requirements: TSE-FUNC-135
        """
        if not waypoints or len(waypoints) < 2:
            return None

        # Calculate legs
        legs = RouteCalculator._calculate_legs(waypoints)
        if not legs:
            return None

        # Calculate totals
        total_distance_m = sum(leg.distance_m for leg in legs)
        total_distance_nm = total_distance_m / RouteCalculator.NM_TO_METERS

        # Time from first to last waypoint
        total_time_sec = waypoints[-1].time_sec - waypoints[0].time_sec

        # Speed statistics
        speeds = [leg.required_speed_knots for leg in legs]
        max_speed_knots = max(speeds) if speeds else 0.0
        min_speed_knots = min(speeds) if speeds else 0.0

        # Average speed (distance/time)
        if total_time_sec > 0:
            average_speed_ms = total_distance_m / total_time_sec
            average_speed_knots = ms_to_knots(average_speed_ms)
        else:
            average_speed_knots = 0.0

        return RouteMetrics(
            total_distance_m=total_distance_m,
            total_distance_nm=total_distance_nm,
            total_time_sec=total_time_sec,
            average_speed_knots=average_speed_knots,
            max_speed_knots=max_speed_knots,
            min_speed_knots=min_speed_knots,
            num_waypoints=len(waypoints),
            num_legs=len(legs),
            legs=legs
        )

    @staticmethod
    def _calculate_legs(waypoints: List[Waypoint]) -> List[RouteLeg]:
        """
        Calculate individual route legs between waypoints.

        Args:
            waypoints: List of waypoints

        Returns:
            List of RouteLeg objects
        """
        legs = []

        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]

            if not wp1.position or not wp2.position:
                continue

            # Calculate distance
            distance_m = haversine_distance(
                wp1.position.latitude,
                wp1.position.longitude,
                wp2.position.latitude,
                wp2.position.longitude
            )

            # Calculate bearing
            bearing_deg = forward_azimuth(
                wp1.position.latitude,
                wp1.position.longitude,
                wp2.position.latitude,
                wp2.position.longitude
            )

            # Calculate time duration
            time_duration_sec = wp2.time_sec - wp1.time_sec

            # Calculate required speed
            if time_duration_sec > 0:
                speed_ms = distance_m / time_duration_sec
                required_speed_knots = ms_to_knots(speed_ms)
            else:
                required_speed_knots = 0.0

            leg = RouteLeg(
                from_waypoint=wp1,
                to_waypoint=wp2,
                distance_m=distance_m,
                bearing_deg=bearing_deg,
                required_speed_knots=required_speed_knots,
                time_duration_sec=time_duration_sec
            )
            legs.append(leg)

        return legs

    @staticmethod
    def calculate_leg_distance(wp1: Waypoint, wp2: Waypoint) -> float:
        """
        Calculate distance between two waypoints.

        Args:
            wp1: First waypoint
            wp2: Second waypoint

        Returns:
            Distance in meters

        Requirements: TSE-FUNC-043
        """
        if not wp1.position or not wp2.position:
            return 0.0

        return haversine_distance(
            wp1.position.latitude,
            wp1.position.longitude,
            wp2.position.latitude,
            wp2.position.longitude
        )

    @staticmethod
    def calculate_required_speed(wp1: Waypoint, wp2: Waypoint) -> float:
        """
        Calculate required speed to reach wp2 from wp1 on time.

        Args:
            wp1: Starting waypoint
            wp2: Destination waypoint

        Returns:
            Required speed in knots

        Requirements: TSE-FUNC-044
        """
        distance_m = RouteCalculator.calculate_leg_distance(wp1, wp2)
        time_duration_sec = wp2.time_sec - wp1.time_sec

        if time_duration_sec <= 0:
            return 0.0

        speed_ms = distance_m / time_duration_sec
        return ms_to_knots(speed_ms)

    @staticmethod
    def calculate_eta(waypoint: Waypoint, distance_m: float, speed_knots: float) -> float:
        """
        Calculate estimated time of arrival given distance and speed.

        Args:
            waypoint: Starting waypoint
            distance_m: Distance to travel in meters
            speed_knots: Travel speed in knots

        Returns:
            ETA in seconds from scenario start
        """
        if speed_knots <= 0:
            return waypoint.time_sec

        speed_ms = knots_to_ms(speed_knots)
        travel_time_sec = distance_m / speed_ms

        return waypoint.time_sec + travel_time_sec

    @staticmethod
    def is_route_reachable(waypoints: List[Waypoint], max_speed_knots: float = 40.0) -> Tuple[bool, Optional[int]]:
        """
        Check if a route is physically reachable given maximum speed.

        Args:
            waypoints: List of waypoints
            max_speed_knots: Maximum vessel speed in knots

        Returns:
            Tuple of (is_reachable, first_unreachable_waypoint_index)

        Requirements: TSE-FUNC-105
        """
        if not waypoints or len(waypoints) < 2:
            return (True, None)

        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]

            required_speed = RouteCalculator.calculate_required_speed(wp1, wp2)

            if required_speed > max_speed_knots:
                return (False, i + 1)

        return (True, None)

    @staticmethod
    def format_distance(distance_m: float) -> str:
        """
        Format distance for display.

        Args:
            distance_m: Distance in meters

        Returns:
            Formatted string (e.g., "5.2 NM (9,630 m)")
        """
        distance_nm = distance_m / RouteCalculator.NM_TO_METERS
        return f"{distance_nm:.2f} NM ({distance_m:,.0f} m)"

    @staticmethod
    def format_time(time_sec: float) -> str:
        """
        Format time duration for display.

        Args:
            time_sec: Time in seconds

        Returns:
            Formatted string (e.g., "5m 30s" or "1h 23m 45s")
        """
        hours = int(time_sec // 3600)
        minutes = int((time_sec % 3600) // 60)
        seconds = int(time_sec % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    @staticmethod
    def format_speed(speed_knots: float) -> str:
        """
        Format speed for display.

        Args:
            speed_knots: Speed in knots

        Returns:
            Formatted string (e.g., "12.5 kts (6.4 m/s)")
        """
        speed_ms = knots_to_ms(speed_knots)
        return f"{speed_knots:.1f} kts ({speed_ms:.1f} m/s)"
