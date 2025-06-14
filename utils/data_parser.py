import pandas as pd
import numpy as np
from datetime import datetime
import logging
from shapely.geometry import Polygon, Point
# from pyproj import Transformer
from utils.coordinate_transform import CoordinateTransform
import csv


#wgs84_to_ecef = CoordinateTransform.
#ecef_to_wgs84 = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)

transformer = CoordinateTransform()

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

        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('time'):
                    current_epoch = line.split(' ', 1)[1]  # Get everything after 'time '
                    satellite_data[current_epoch] = []
                    logging.info(f"Processing epoch {current_epoch}")
                else:
                    # Parse X, Y, Z, SNR, and Satellite ID
                    data = line.split()
                    if current_epoch and len(data) >= 5 and float(data[0])!=0:  # Ensure we have all fields including Satellite ID

                        sat_data = {
                            'X': float(data[0]),
                            'Y': float(data[1]),
                            'Z': float(data[2]),
                            'SNR': float(data[3]),
                            'satellite_id': data[4],  # Add satellite ID
                            'azimuth': data[5],
                            'elevation': data[6],
                            'resp': data[7],
                        }
                        satellite_data[current_epoch].append(sat_data)
                        logging.debug(f"Added satellite {data[4]} with SNR {data[3]}")

        logging.info(f"Total epochs processed: {len(satellite_data)}")
        return satellite_data

    @staticmethod
    def parse_satellite_data_cov(filename):
        """
        Parse satellite data from TXT file
        Format:
        time YYYY/MM/DD HH:MM:SS.SSS
        X Y Z SNR SATELLITE_ID
        Returns: Dictionary with epoch times as keys and satellite data as values
        """
        satellite_data = {}
        cov_data = {}
        current_epoch = None

        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('time'):
                    current_epoch = line.split(' ', 1)[1]  # Get everything after 'time '
                    satellite_data[current_epoch] = []
                    logging.info(f"Processing epoch {current_epoch}")
                else:
                    # Parse X, Y, Z, SNR, and Satellite ID
                    data = line.split()
                    if current_epoch and len(data) >= 5 and float(
                            data[0]) != 0:  # Ensure we have all fields including Satellite ID
                        C_G = np.array([[float(data[8]), float(data[11]), float(data[14])],
                                        [float(data[9]), float(data[12]), float(data[15])],
                                        [float(data[10]), float(data[13]), float(data[16])]])
                        sat_data = {
                            'X': float(data[0]),
                            'Y': float(data[1]),
                            'Z': float(data[2]),
                            'SNR': float(data[3]),
                            'satellite_id': data[4],  # Add satellite ID
                            'azimuth': data[5],
                            'elevation': data[6],
                            'resp': data[7],
                        }
                        satellite_data[current_epoch].append(sat_data)
                        logging.debug(f"Added satellite {data[4]} with SNR {data[3]}")
                        cov_data[current_epoch] = C_G

        logging.info(f"Total epochs processed: {len(satellite_data)}")
        return satellite_data, cov_data

    @staticmethod
    def parse_position_data(filename):
        """
        Parse initial position data from POS file
        Format:
        DATE TIME LAT LON HEIGHT Q NS SDN SDE SDU SDNE SDEU SDUN AGE RATIO VN VE VU SDVN SDVE SDVU SDVNE SDVEU SDVUN
        Returns: Dictionary with epoch times as keys and position data as values
        """
        position_data = {}

        with open(filename, 'r', encoding='utf-8') as f:
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

                        x = float(data[2])  # latitude in degrees
                        y = float(data[3])  # longitude in degrees
                        z = float(data[4])  # height in meters

                        position_data[timestamp] = {
                            'lat': x,
                            'lon': y,
                            'alt': z,
                        }
                        logging.debug(f"Processed position data for {timestamp}")
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Could not parse line: {line}")
                        continue

        logging.info(f"Total positions processed: {len(position_data)}")
        return position_data

    @staticmethod
    def parse_position_csv(file_path):
        position_data = {}

        with open(file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)  # 默认分隔符是逗号
            print(reader.fieldnames)  # 确认列名是否正确

            for row in reader:
                timestamp = row['Timestamp'].strip()
                position_data[timestamp] = {
                    'lat': float(row['Latitude']),
                    'lon': float(row['Longitude']),
                    'alt': float(row['Height'])
                }

        return position_data

    @staticmethod
    def parse_building_data(file_path):
        """
        从TXT文件加载建筑信息，并返回包含建筑多边形、高度和中心点的列表。
        :param file_path: TXT文件路径
        :return: buildings (列表，每个元素为 {"polygon": Polygon, "height": float, "center": Point})
        """
        buildings = []

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(' ')
                if len(parts) < 6 or len(parts) % 2 != 0:
                    print(f"⚠️ 警告：跳过格式错误的行 -> {line.strip()}")
                    continue

                    # 解析建筑ID（可忽略）
                building_id = parts[0]

                # 解析建筑高度
                try:
                    height = float(parts[1])
                except ValueError:
                    print(f"⚠️ 警告：建筑 {building_id} 高度解析失败，跳过该建筑")
                    continue

                # 解析中心点坐标
                try:
                    center_lon, center_lat = float(parts[2]), float(parts[3])
                except ValueError:
                    print(f"⚠️ 警告：建筑 {building_id} 中心点坐标解析失败，跳过该建筑")
                    continue

                # 解析角点坐标（成对读取）
                try:
                    coordinates = [(float(parts[i]), float(parts[i + 1])) for i in range(4, len(parts), 2)]
                except ValueError:
                    print(f"⚠️ 警告：建筑 {building_id} 角点坐标解析失败，跳过该建筑")
                    continue

                # 确保至少是一个有效的多边形（>=3个点）
                if len(coordinates) < 3:
                    print(f"⚠️ 警告：建筑 {building_id} 角点数量不足，跳过该建筑")
                    continue

                # 中心点转换
                center_x, center_y, center_z = transformer.convert_wgs_to_ecef(center_lon, center_lat, 0)
                # 角点转换
                ecef_coordinates = [transformer.convert_wgs_to_ecef(lon, lat, 0) for lon, lat in coordinates]

                # 创建多边形对象
                polygon = Polygon([(p[0], p[1]) for p in coordinates])  # 确保是 (x, y) 坐标
                center_point = Point(center_x, center_y, center_z)

                # 存储建筑信息
                buildings.append({"polygon": polygon, "height": height, "center": center_point})

            return buildings

    @staticmethod
    def parse_building_data_new(file_path):
        """
        从TXT文件加载建筑信息，并返回包含建筑多边形、高度和中心点的列表。
        :param file_path: TXT文件路径
        :return: buildings (列表，每个元素为 {"polygon": Polygon, "height": float, "center": Point})
        """
        buildings = []

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(' ')
                if len(parts) < 6 or len(parts) % 2 != 0:
                    print(f"⚠️ 警告：跳过格式错误的行 -> {line.strip()}")
                    continue

                    # 解析建筑ID（可忽略）
                building_id = parts[0]

                # 解析建筑高度
                try:
                    height = float(parts[1])
                except ValueError:
                    print(f"⚠️ 警告：建筑 {building_id} 高度解析失败，跳过该建筑")
                    continue

                # 解析角点坐标（成对读取）
                try:
                    coordinates = [(float(parts[i]), float(parts[i + 1])) for i in range(2, len(parts), 2)]
                except ValueError:
                    print(f"⚠️ 警告：建筑 {building_id} 角点坐标解析失败，跳过该建筑")
                    continue

                # 角点转换
                ecef_coordinates = [transformer.convert_wgs_to_ecef(lon, lat, 0) for lon, lat in coordinates]

                # 创建多边形对象
                polygon = Polygon([(p[0], p[1]) for p in coordinates])  # 确保是 (x, y) 坐标


                # 存储建筑信息
                buildings.append({"polygon": polygon, "height": height, 'P1':coordinates[0], 'P2':coordinates[1]})

            return buildings





    @staticmethod
    def parse_gnss_stat_file(file_path):
        gnssdatas = []  # 存储多个历元的数据
        current_epoch_satdata = []
        week = tow = posx = posy = posz = None

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split(',')

            if line.startswith('$POS'):
                # 如果不是第一个历元，就保存上一个历元
                if week is not None and current_epoch_satdata:
                    gnssdata = {
                        "position": (posx, posy, posz),
                        "time": (week, tow),
                        "satdata": current_epoch_satdata
                    }
                    gnssdatas.append(gnssdata)
                    current_epoch_satdata = []

                week = int(parts[1])
                tow = float(parts[2])
                posx = float(parts[3])
                posy = float(parts[4])
                posz = float(parts[5])

            elif line.startswith('$SAT'):
                sat_id = parts[3]
                az = float(parts[5])
                el = float(parts[6])
                resp = float(parts[7])
                snr = int(parts[10])
                sat_info = {
                    "sat": sat_id,
                    "az": az,
                    "el": el,
                    "snr": snr,
                    "resp": resp
                }
                current_epoch_satdata.append(sat_info)

        # 保存最后一个历元
        if week is not None and current_epoch_satdata:
            gnssdata = {
                "position": (posx, posy, posz),
                "time": (week, tow),
                "satdata": current_epoch_satdata
            }
            gnssdatas.append(gnssdata)

        return gnssdatas











