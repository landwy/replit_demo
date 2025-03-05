import numpy as np
from math import sqrt, atan2, pi, sin, cos
from geopy.point import Point
from geopy.distance import geodesic

class CoordinateTransform:
    # WGS84 parameters
    a = 6378137.0  # semi-major axis
    f = 1/298.257223563  # flattening
    e2 = 2*f - f*f  # eccentricity squared

    @staticmethod
    def ecef_to_lla(x, y, z):
        """
        Convert ECEF coordinates to Latitude, Longitude, Altitude (LLA)
        Returns: tuple (lat, lon, alt) in degrees and meters
        """
        p = sqrt(x**2 + y**2)
        theta = atan2(z*CoordinateTransform.a, p*(1-CoordinateTransform.e2))

        lat = atan2(z + CoordinateTransform.e2*(1-CoordinateTransform.e2)*sin(theta)**3, 
                   p - CoordinateTransform.e2*cos(theta)**3)
        lon = atan2(y, x)
        N = CoordinateTransform.a/sqrt(1-CoordinateTransform.e2*sin(lat)**2)
        alt = p/cos(lat) - N

        return np.degrees(lat), np.degrees(lon), alt

    @staticmethod
    def lla_to_ecef(lat, lon, alt):
        """
        Convert Latitude, Longitude, Altitude (LLA) to ECEF
        Parameters: lat, lon in degrees, alt in meters
        Returns: tuple (x, y, z) in meters
        """
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)

        N = CoordinateTransform.a/sqrt(1-CoordinateTransform.e2*sin(lat_rad)**2)
        x = (N + alt)*cos(lat_rad)*cos(lon_rad)
        y = (N + alt)*cos(lat_rad)*sin(lon_rad)
        z = (N*(1-CoordinateTransform.e2) + alt)*sin(lat_rad)

        return x, y, z

    @staticmethod
    def ecef_to_enu(sat_x, sat_y, sat_z, ref_x, ref_y, ref_z):
        """
        Convert ECEF coordinates to ENU (East-North-Up)
        """
        # First convert reference point to LLA
        ref_lat, ref_lon, ref_alt = CoordinateTransform.ecef_to_lla(ref_x, ref_y, ref_z)
        ref_lat_rad = np.radians(ref_lat)
        ref_lon_rad = np.radians(ref_lon)

        # Calculate satellite position relative to reference
        dx = sat_x - ref_x
        dy = sat_y - ref_y
        dz = sat_z - ref_z

        # Rotation matrix - ECEF to ENU
        sin_lat = sin(ref_lat_rad)
        cos_lat = cos(ref_lat_rad)
        sin_lon = sin(ref_lon_rad)
        cos_lon = cos(ref_lon_rad)

        # Transform to ENU
        e = -sin_lon*dx + cos_lon*dy
        n = -sin_lat*cos_lon*dx - sin_lat*sin_lon*dy + cos_lat*dz
        u = cos_lat*cos_lon*dx + cos_lat*sin_lon*dy + sin_lat*dz

        return e, n, u

    @staticmethod
    def calculate_azimuth_elevation(e, n, u):
        """
        Calculate azimuth and elevation angles from ENU coordinates
        Returns: tuple (azimuth, elevation) in degrees
        """
        horizontal_distance = sqrt(e**2 + n**2)
        elevation = atan2(u, horizontal_distance)
        azimuth = atan2(e, n)

        # Convert to degrees
        elevation_deg = elevation * 180/pi
        azimuth_deg = azimuth * 180/pi

        # Ensure azimuth is in [0, 360]
        if azimuth_deg < 0:
            azimuth_deg += 360

        return azimuth_deg, elevation_deg

    @staticmethod
    def calculate_ground_distance(lat1, lon1, lat2, lon2):
        """
        Calculate ground distance between two points using geodesic distance
        Parameters: lat1, lon1, lat2, lon2 in degrees
        Returns: distance in meters
        """
        point1 = Point(lat1, lon1)
        point2 = Point(lat2, lon2)
        return geodesic(point1, point2).meters