import numpy as np
from .coordinate_transform import CoordinateTransform

class VisibilityCalculator:
    def __init__(self, snr_threshold=30):
        self.snr_threshold = snr_threshold
        self.coord_transform = CoordinateTransform()

    def predict_satellite_visibility(self, sat_pos, receiver_pos, buildings):
        """
        Predict satellite visibility based on building geometry
        Buildings are simplified as vertical rectangles with two ground points and height
        """
        # Convert satellite position to ENU
        e, n, u = self.coord_transform.ecef_to_enu(
            sat_pos['X'], sat_pos['Y'], sat_pos['Z'],
            receiver_pos['X'], receiver_pos['Y'], receiver_pos['Z']
        )

        # Calculate satellite azimuth and elevation
        sat_azimuth, sat_elevation = self.coord_transform.calculate_azimuth_elevation(e, n, u)

        # Check each building's blocking effect
        for building in buildings:
            # Get building's two ground points in ENU
            e1, n1, _ = self.coord_transform.ecef_to_enu(
                building['point1_X'], building['point1_Y'], building['point1_Z'],
                receiver_pos['X'], receiver_pos['Y'], receiver_pos['Z']
            )
            e2, n2, _ = self.coord_transform.ecef_to_enu(
                building['point2_X'], building['point2_Y'], building['point2_Z'],
                receiver_pos['X'], receiver_pos['Y'], receiver_pos['Z']
            )

            # Calculate building face azimuth (perpendicular to the line between points)
            building_line_azimuth = np.degrees(np.arctan2(e2 - e1, n2 - n1))
            building_face_azimuth = (building_line_azimuth + 90) % 360

            # Calculate distance to building face
            # Project receiver-building vector onto normal vector of building face
            normal_vector = np.array([np.cos(np.radians(building_face_azimuth)), 
                                    np.sin(np.radians(building_face_azimuth))])
            receiver_to_building = np.array([e1, n1])  # Vector from receiver to building point 1
            distance = abs(np.dot(receiver_to_building, normal_vector))

            # Calculate building elevation angle
            building_elevation = np.degrees(np.arctan2(building['height'], distance))

            # Check if satellite is blocked by this building face
            azimuth_diff = abs((sat_azimuth - building_face_azimuth + 180) % 360 - 180)
            if (azimuth_diff < 90 and  # Satellite is in front of building face
                sat_elevation < building_elevation):  # Satellite is below building top edge
                return False

        return True

    def check_observed_visibility(self, snr):
        """
        Check satellite visibility based on SNR
        """
        return snr >= self.snr_threshold