import math
import logging
import requests
from typing import List, Tuple, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points 
    on the Earth in kilometers using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 3)


def haversine_matrix(coordinates: List[Tuple[float, float]], avg_speed_kmh: float = 30.0) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Compute a 2D distance matrix (km) and travel duration matrix (minutes)
    for a list of (lat, lon) coordinates using Haversine formula and average speed.
    """
    n = len(coordinates)
    distance_matrix = [[0.0] * n for _ in range(n)]
    duration_matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                distance_matrix[i][j] = 0.0
                duration_matrix[i][j] = 0.0
            else:
                dist = haversine_distance(
                    coordinates[i][0], coordinates[i][1],
                    coordinates[j][0], coordinates[j][1]
                )
                distance_matrix[i][j] = round(dist, 2)
                # Duration in minutes: (dist / avg_speed_kmh) * 60
                duration_min = (dist / avg_speed_kmh) * 60.0
                duration_matrix[i][j] = round(duration_min, 2)

    return distance_matrix, duration_matrix


class OSRMService:
    def __init__(self, base_url: str = None, timeout: int = 10):
        self.base_url = (base_url or settings.OSRM_SERVER_URL).rstrip('/')
        self.timeout = timeout

    def get_table_matrix(
        self, coordinates: List[Tuple[float, float]]
    ) -> Tuple[List[List[float]], List[List[float]], bool, str]:
        """
        Request distance matrix (km) and duration matrix (minutes) from OSRM Table API.
        Input coordinates: List of (latitude, longitude) tuples.
        Returns: (distance_matrix_km, duration_matrix_min, is_fallback, source)
        """
        if not coordinates:
            return [], [], False, "empty"

        if len(coordinates) == 1:
            return [[0.0]], [[0.0]], False, "osrm"

        # OSRM expects coordinates in lon,lat format separated by semicolons
        coord_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
        url = f"{self.base_url}/table/v1/driving/{coord_str}?annotations=distance,duration"

        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok":
                    raw_distances = data.get("distances", [])
                    raw_durations = data.get("durations", [])

                    # Convert distances from meters to km
                    distances_km = [
                        [round(d / 1000.0, 2) if d is not None else 9999.0 for d in row]
                        for row in raw_distances
                    ]
                    # Convert durations from seconds to minutes
                    durations_min = [
                        [round(dur / 60.0, 2) if dur is not None else 9999.0 for dur in row]
                        for row in raw_durations
                    ]

                    return distances_km, durations_min, False, "osrm"
                else:
                    logger.warning(f"OSRM Table API returned non-Ok code: {data.get('code')}")
            else:
                logger.warning(f"OSRM Table API returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"OSRM Table API request failed or timed out: {str(e)}")

        # Fallback to Haversine matrix if OSRM is unreachable
        logger.info("Falling back to Haversine distance matrix computation.")
        dist_mat, dur_mat = haversine_matrix(coordinates)
        return dist_mat, dur_mat, True, "haversine_fallback"

    def get_route_geometry(
        self, waypoints: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Request route geometry, distance, and duration for a sequence of waypoints from OSRM Route API.
        Input waypoints: List of (latitude, longitude) tuples.
        Returns dict containing distance_km, duration_minutes, geometry_coordinates [lat, lon], is_fallback, source.
        """
        if not waypoints:
            return {
                "distance_km": 0.0,
                "duration_minutes": 0.0,
                "geometry_coordinates": [],
                "is_fallback": False,
                "source": "empty"
            }

        if len(waypoints) == 1:
            return {
                "distance_km": 0.0,
                "duration_minutes": 0.0,
                "geometry_coordinates": [[waypoints[0][0], waypoints[0][1]]],
                "is_fallback": False,
                "source": "single_point"
            }

        coord_str = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
        url = f"{self.base_url}/route/v1/driving/{coord_str}?overview=full&geometries=geojson&steps=true"

        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    distance_km = round(route.get("distance", 0.0) / 1000.0, 2)
                    duration_min = round(route.get("duration", 0.0) / 60.0, 2)

                    # GeoJSON coordinates are [lon, lat]. Convert to [lat, lon] for Leaflet
                    raw_coords = route.get("geometry", {}).get("coordinates", [])
                    lat_lon_coords = [[lat, lon] for lon, lat in raw_coords]

                    return {
                        "distance_km": distance_km,
                        "duration_minutes": duration_min,
                        "geometry_coordinates": lat_lon_coords,
                        "is_fallback": False,
                        "source": "osrm"
                    }
                else:
                    logger.warning(f"OSRM Route API returned non-Ok code: {data.get('code')}")
            else:
                logger.warning(f"OSRM Route API returned HTTP status {response.status_code}")
        except Exception as e:
            logger.warning(f"OSRM Route API request failed: {str(e)}")

        # Fallback straight line polyline and Haversine distance sum
        logger.info("Falling back to straight-line polyline for route geometry.")
        total_dist = 0.0
        for i in range(len(waypoints) - 1):
            total_dist += haversine_distance(
                waypoints[i][0], waypoints[i][1],
                waypoints[i+1][0], waypoints[i+1][1]
            )

        duration_min = round((total_dist / 30.0) * 60.0, 2)
        fallback_coords = [[lat, lon] for lat, lon in waypoints]

        return {
            "distance_km": round(total_dist, 2),
            "duration_minutes": duration_min,
            "geometry_coordinates": fallback_coords,
            "is_fallback": True,
            "source": "haversine_fallback"
        }

osrm_service = OSRMService()
