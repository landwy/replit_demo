import numpy as np
from .coordinate_transform import CoordinateTransform

class VisibilityCalculator:
    def __init__(self, snr_threshold=30):
        self.snr_threshold = snr_threshold
        self.coord_transform = CoordinateTransform()

    def predict_satellite_visibility(self, sat_pos, receiver_pos, buildings):
        """
        Predict satellite visibility based on building geometry
        """
        # Convert to ENU
        e, n, u = self.coord_transform.ecef_to_enu(
            sat_pos['X'], sat_pos['Y'], sat_pos['Z'],
            receiver_pos['X'], receiver_pos['Y'], receiver_pos['Z']
        )
        
        # Calculate azimuth and elevation
        azimuth, elevation = self.coord_transform.calculate_azimuth_elevation(e, n, u)
        
        # Check building shadows
        for building in buildings:
            # Calculate building elevation angle at receiver
            building_e, building_n, _ = self.coord_transform.ecef_to_enu(
                building['X'], building['Y'], building['Z'],
                receiver_pos['X'], receiver_pos['Y'], receiver_pos['Z']
            )
            
            building_azimuth = np.degrees(np.arctan2(building_e, building_n))
            if building_azimuth < 0:
                building_azimuth += 360
                
            # Calculate building elevation angle
            distance = np.sqrt(building_e**2 + building_n**2)
            building_elevation = np.degrees(np.arctan2(building['height'], distance))
            
            # Check if satellite is blocked
            if (abs(azimuth - building_azimuth) < 5 and  # Within azimuth tolerance
                elevation < building_elevation):
                return False
                
        return True

    def check_observed_visibility(self, snr):
        """
        Check satellite visibility based on SNR
        """
        return snr >= self.snr_threshold
