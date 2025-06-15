import numpy as np
from math import sqrt, atan2, pi, sin, cos
from geopy.point import Point
from geopy.distance import geodesic

# class CoordinateTransform:
#     # WGS84 parameters
#     a = 6378137.0  # semi-major axis
#     f = 1/298.257223563  # flattening
#     e2 = 2*f - f*f  # eccentricity squared
#
#     @staticmethod
#     def ecef_to_lla(x, y, z):
#         """
#         Convert ECEF coordinates to Latitude, Longitude, Altitude (LLA)
#         Returns: tuple (lat, lon, alt) in degrees and meters
#         """
#         p = sqrt(x**2 + y**2)
#         theta = atan2(z*CoordinateTransform.a, p*(1-CoordinateTransform.e2))
#
#         lat = atan2(z + CoordinateTransform.e2*(1-CoordinateTransform.e2)*sin(theta)**3,
#                    p - CoordinateTransform.e2*cos(theta)**3)
#         lon = atan2(y, x)
#         n = CoordinateTransform.a/sqrt(1-CoordinateTransform.e2*sin(lat)**2)
#         alt = p/cos(lat) - n
#
#         return np.degrees(lat), np.degrees(lon), alt
#
#     @staticmethod
#     def lla_to_ecef(lat, lon, alt):
#         """
#         Convert Latitude, Longitude, Altitude (LLA) to ECEF
#         Parameters: lat, lon in degrees, alt in meters
#         Returns: tuple (x, y, z) in meters
#         """
#         lat_rad = np.radians(lat)
#         lon_rad = np.radians(lon)
#
#         n = CoordinateTransform.a/sqrt(1-CoordinateTransform.e2*sin(lat_rad)**2)
#         x = (n + alt)*cos(lat_rad)*cos(lon_rad)
#         y = (n + alt)*cos(lat_rad)*sin(lon_rad)
#         z = (n*(1-CoordinateTransform.e2) + alt)*sin(lat_rad)
#
#         return x, y, z
#
#     @staticmethod
#     def ecef_to_enu(sat_x, sat_y, sat_z, ref_x, ref_y, ref_z):
#         """
#         Convert ECEF coordinates to ENU (East-North-Up)
#         """
#         # First convert reference point to LLA
#         ref_lat, ref_lon, ref_alt = CoordinateTransform.ecef_to_lla(ref_x, ref_y, ref_z)
#         ref_lat_rad = np.radians(ref_lat)
#         ref_lon_rad = np.radians(ref_lon)
#
#         # Calculate satellite position relative to reference
#         dx = sat_x - ref_x
#         dy = sat_y - ref_y
#         dz = sat_z - ref_z
#
#         # Rotation matrix - ECEF to ENU
#         sin_lat = sin(ref_lat_rad)
#         cos_lat = cos(ref_lat_rad)
#         sin_lon = sin(ref_lon_rad)
#         cos_lon = cos(ref_lon_rad)
#
#         # Transform to ENU
#         e = -sin_lon*dx + cos_lon*dy
#         n = -sin_lat*cos_lon*dx - sin_lat*sin_lon*dy + cos_lat*dz
#         u = cos_lat*cos_lon*dx + cos_lat*sin_lon*dy + sin_lat*dz
#
#         return e, n, u
#
#     @staticmethod
#     def calculate_azimuth_elevation(e, n, u):
#         """
#         Calculate azimuth and elevation angles from ENU coordinates
#         Returns: tuple (azimuth, elevation) in degrees
#         """
#         horizontal_distance = sqrt(e**2 + n**2)
#         elevation = atan2(u, horizontal_distance)
#         azimuth = atan2(e, n)
#
#         # Convert to degrees
#         elevation_deg = elevation * 180/pi
#         azimuth_deg = azimuth * 180/pi
#
#         # Ensure azimuth is in [0, 360]
#         if azimuth_deg < 0:
#             azimuth_deg += 360
#
#         return azimuth_deg, elevation_deg
#
#     @staticmethod
#     def calculate_ground_distance(lat1, lon1, lat2, lon2):
#         """
#         Calculate ground distance between two points using geodesic distance
#         Parameters: lat1, lon1, lat2, lon2 in degrees
#         Returns: distance in meters
#         """
#         point1 = Point(lat1, lon1)
#         point2 = Point(lat2, lon2)
#         return geodesic(point1, point2).meters

from pyproj import Transformer

class CoordinateTransform:
    def __init__(self):
        # 定义坐标转换器

        self.ecef_to_wgs = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)
        self.ecef_to_utm = Transformer.from_crs("EPSG:4978", "EPSG:32651", always_xy=True)
        self.utm_to_ecef = Transformer.from_crs("EPSG:32651", "EPSG:4978", always_xy=True)
        self.wgs_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32651", always_xy=True)
        self.utm_to_wgs = Transformer.from_crs("EPSG:32651", "EPSG:4326", always_xy=True)
        self.wgs_to_ecef = Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)
        # WGS84 椭球高转换为 EGM96 地形高
        self.wgs84_to_egm96 = Transformer.from_crs("EPSG:4326", "EPSG:3855", always_xy=True)


    def convert_ecef_to_wgs(self, x, y, z):
        """ ECEF 转 WGS84 """
        return self.ecef_to_wgs.transform(x, y, z)

    def convert_ecef_to_utm(self, x, y, z):
        """ ECEF 转 UTM """
        return self.ecef_to_utm.transform(x, y, z)

    def convert_utm_to_ecef(self, x, y, z):
        """ UTM 转 ECEF """
        return self.utm_to_ecef.transform(x, y, z)

    def convert_utm_to_wgs(self, x, y, z):
        """ UTM 转 WGS84 """
        return self.utm_to_wgs.transform(x, y, z)

    def convert_wgs_to_utm(self, lon, lat, alt):
        """ WGS84 转 UTM """
        return self.wgs_to_utm.transform(lon, lat, alt)

    def convert_wgs_to_ecef(self, lon, lat, alt):
        """ WGS84 转 ECEF """
        return self.wgs_to_ecef.transform(lon, lat, alt)

    def convert_wgs_to_egm96(self, lon, lat, alt):
        return self.wgs84_to_egm96.transform(lon, lat, alt)  # h 是原始高度

    def convert_ecef_to_enu(self,x, y, z, ref_lon, ref_lat, ref_alt):
        """将 ECEF 坐标转换为以 (ref_lat, ref_lon, ref_alt) 为原点的 ENU 坐标"""
        x_ref, y_ref, z_ref = self.wgs_to_ecef.transform(ref_lon, ref_lat, ref_alt)
        dx, dy, dz = x - x_ref, y - y_ref, z - z_ref

        ref_lat_rad = np.radians(ref_lat)
        ref_lon_rad = np.radians(ref_lon)

        slon, clon = np.sin(ref_lon_rad), np.cos(ref_lon_rad)
        slat, clat = np.sin(ref_lat_rad), np.cos(ref_lat_rad)

        e = -slon * dx + clon * dy
        n = -slat * clon * dx - slat * slon * dy + clat * dz
        u = clat * clon * dx + clat * slon * dy + slat * dz

        return e, n, u


    def convert_enu_to_ecef(self, e, n, u, ref_lon, ref_lat, ref_alt):
        """将 ENU 坐标转换为 ECEF 坐标"""
        ref_lat_rad = np.radians(ref_lat)
        ref_lon_rad = np.radians(ref_lon)

        slon, clon = np.sin(ref_lon_rad), np.cos(ref_lon_rad)
        slat, clat = np.sin(ref_lat_rad), np.cos(ref_lat_rad)

        dx = -slon * e - slat * clon * n + clat * clon * u
        dy = clon * e - slat * slon * n + clat * slon * u
        dz = clat * n + slat * u

        x_ref, y_ref, z_ref = self.wgs_to_ecef.transform(ref_lon, ref_lat, ref_alt)
        x = x_ref + dx
        y = y_ref + dy
        z = z_ref + dz

        return x, y, z


# transformer = CoordinateTransform()
# # 测试 ECEF -> WGS84
# x, y, z = 0, 0, 6356752.31  # 预期：纬度接近 90° (极点)
# lon, lat, alt = transformer.convert_ecef_to_wgs(x, y, z)
# print(f"ECEF → WGS84: ({x}, {y}, {z}) → ({lon}, {lat}, {alt})")
#
# # 测试 WGS84 -> ECEF
# lon, lat, alt = 0, 90, 0  # 预期：Z 轴方向
# x, y, z = transformer.convert_wgs_to_ecef(lon, lat, alt)
# print(f"WGS84 → ECEF: ({lon}, {lat}, {alt}) → ({x}, {y}, {z})")
