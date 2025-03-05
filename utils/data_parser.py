import pandas as pd
import numpy as np
from datetime import datetime
import logging

class DataParser:
    @staticmethod
    def parse_satellite_data(filename):
        """
        Parse satellite data from TXT file
        Format:
        time YYYY/MM/DD HH:MM:SS.SSS
        X Y Z SNR SATELLITE_ID
        Returns: Dictionary with epoch times as keys and satellite data as values
        """
        satellite_data = {}
        current_epoch = None

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('time'):
                    current_epoch = line.split(' ', 1)[1]  # Get everything after 'time '
                    satellite_data[current_epoch] = []
                    logging.info(f"Processing epoch {current_epoch}")
                else:
                    # Parse X, Y, Z, SNR, and Satellite ID
                    data = line.split()
                    if current_epoch and len(data) >= 5:  # Ensure we have all fields including Satellite ID
                        sat_data = {
                            'X': float(data[0]),
                            'Y': float(data[1]),
                            'Z': float(data[2]),
                            'SNR': float(data[3]),
                            'satellite_id': data[4]  # Add satellite ID
                        }
                        satellite_data[current_epoch].append(sat_data)
                        logging.debug(f"Added satellite {data[4]} with SNR {data[3]}")

        logging.info(f"Total epochs processed: {len(satellite_data)}")
        return satellite_data

    @staticmethod
    def parse_position_data(filename):
        """
        Parse initial position data from POS file
        Format:
        DATE TIME LAT LON HEIGHT Q NS SDN SDE SDU SDNE SDEU SDUN AGE RATIO VN VE VU SDVN SDVE SDVU SDVNE SDVEU SDVUN
        Returns: Dictionary with epoch times as keys and position data as values
        """
        position_data = {}

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comment lines starting with %
                if line.startswith('%'):
                    logging.debug(f"Skipping comment line: {line[:50]}...")
                    continue

                data = line.split()
                if len(data) >= 15:  # Ensure we have all required fields
                    try:
                        # Parse date and time
                        date_str = data[0]
                        time_str = data[1]
                        timestamp = f"{date_str} {time_str}"

                        # Convert lat/lon to ECEF coordinates
                        lat = float(data[2])  # latitude in degrees
                        lon = float(data[3])  # longitude in degrees
                        height = float(data[4])  # height in meters

                        from .coordinate_transform import CoordinateTransform
                        x, y, z = CoordinateTransform.lla_to_ecef(lat, lon, height)

                        position_data[timestamp] = {
                            'X': x,
                            'Y': y,
                            'Z': z,
                            'original_lat': lat,
                            'original_lon': lon,
                            'original_height': height
                        }
                        logging.debug(f"Processed position data for {timestamp}")
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Could not parse line: {line}")
                        continue

        logging.info(f"Total positions processed: {len(position_data)}")
        return position_data

    @staticmethod
    def parse_building_data(filename):
        """
        Parse building information
        Format: X Y Z HEIGHT
        Returns: List of buildings with ground coordinates and heights
        """
        buildings = []

        with open(filename, 'r') as f:
            for line in f:
                data = line.strip().split()
                if len(data) >= 4:  # Ensure we have enough fields
                    buildings.append({
                        'X': float(data[0]),
                        'Y': float(data[1]),
                        'Z': float(data[2]),
                        'height': float(data[3])
                    })

        logging.info(f"Total buildings processed: {len(buildings)}")
        return buildings