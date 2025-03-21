import pandas as pd
import numpy as np
from datetime import datetime
import logging
from shapely.geometry import Polygon, Point
# from pyproj import Transformer
from utils.coordinate_transform import CoordinateTransform


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

                        # position_data[timestamp] = {
                        #     'X': x,
                        #     'Y': y,
                        #     'Z': z,
                        # }
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

                # 创建 Shapely 多边形对象
                #polygon = Polygon([(x, y) for x, y, z in ecef_coordinates])
                #polygon = Polygon([(p[0], p[1]) for p in ecef_coordinates])  # 确保是 (x, y) 坐标
                polygon = Polygon([(p[0], p[1]) for p in coordinates])  # 确保是 (x, y) 坐标
                center_point = Point(center_x, center_y, center_z)

                # 存储建筑信息
                buildings.append({"polygon": polygon, "height": height, "center": center_point})

            return buildings
#
# import pandas as pd
# import os
# #--------------------------------------合并文件夹中的所有csv文件---------------------------------------------------
# # 设定 CSV 文件所在的目录
# folder_path = "F:\\GNSSdata\\rf_train\\merged_snr"
#
# # 获取所有 CSV 文件
# csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
#
# # 读取并合并所有 CSV 文件
# df_list = [pd.read_csv(os.path.join(folder_path, file)) for file in csv_files]
# merged_df = pd.concat(df_list, ignore_index=True)
#
# # 保存合并后的文件
# merged_df.to_csv("F:\\GNSSdata\\rf_train\\merged_snr\\merged_snr.csv", index=False)

#-------------------------------------------------取snr最大值-------------------------------------------------
# import pandas as pd
#
# # 读取 CSV 文件
# df = pd.read_csv('F:\\GNSSdata\\rf_train\\merged_stat.csv')
#
# # 假设 SNR 数据存储在 'snr1' 和 'snr2' 列
# df['snr'] = df[['SNR0', 'SNR1']].max(axis=1)
#
# # 删除原来的 SNR 列（如果不需要保留）
# df.drop(columns=['SNR0', 'SNR1'], inplace=True)
#
# # 保存到新的 CSV 文件
# df.to_csv('F:\\GNSSdata\\rf_train\\merged_snr_stat.csv', index=False)
#
# print("合并完成，结果保存在 merged_snr_stat.csv")


#-------------------------------------------读取.stat文件并存储为csv文件---------------------------------------------------
# import csv
# import datetime
#
#
# def gps_time(gps_week, gps_tow):
#     """将 GPS 周和周内秒转换为 gps时间"""
#     gps_epoch = datetime.datetime(1980, 1, 6, 0, 0, 0)  # GPS时间起点
#
#     gtime = gps_epoch + datetime.timedelta(weeks=gps_week, seconds=gps_tow)
#     return gtime.strftime("%Y/%m/%d %H:%M:%S")
#
#
# # 输入和输出文件路径
# input_file = "F:\\GNSSdata\\KLTDataset\\GNSS\\20231109\\spp.pos.stat"  # 替换为你的文件路径
# output_file = "F:\\GNSSdata\\rf_train\\stat.csv"
#
# # 存储解析后的数据
# satellite_data = []
#
# # 读取文件
# with open(input_file, "r") as f:
#     gps_week, gps_tow = None, None  # 存储GPS时间信息
#     for line in f:
#         parts = line.strip().split(",")
#         if not parts:
#             continue
#
#         if parts[0] == "$CLK":
#             gps_week = int(parts[1])  # GPS周
#             gps_tow = float(parts[2])  # GPS周内秒
#
#         elif parts[0] == "$SAT" and gps_week is not None and gps_tow is not None:
#             satellite = parts[3]  # 卫星 ID
#
#             azimuth = float(parts[5])   #方位角
#             elevation = float(parts[6]) #仰角
#             resp = float(parts[7])  # 伪距残差 (resp)
#             # snr0 = float(parts[9])  # 信噪比 (SNR)
#             # snr1 = float(parts[10])
#             snr = float(max(parts[9],parts[10]))
#             time = gps_time(gps_week, gps_tow)  # 转换时间
#
#             # 保存数据
#             satellite_data.append([time, satellite, snr, resp, azimuth, elevation])
#
# # 将数据写入 CSV 文件
# with open(output_file, "w", newline="") as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(["time", "satellite", "snr", "resp", "azimuth", "elevation"])  # 写入表头
#     writer.writerows(satellite_data)
#
# print(f"数据已保存至 {output_file}")



#---------------------------------------将stat.csv中的resp值加入到merged_data合并-----------------------------------------
# import pandas as pd
#
# # 读取 CSV 文件
# stat = pd.read_csv("F:\\GNSSdata\\rf_train\\stat.csv")
# merged_data = pd.read_csv("F:\\GNSSdata\\rf_train\\merged_snr.csv")
#
# # 确保时间列的格式一致
# # stat421["time"] = pd.to_datetime(stat421["time"])
# # merged_data421["time"] = pd.to_datetime(merged_data421["time"])
#
# # 选择 stat需要合并的列
# stat_subset = stat[["time", "satellite", "resp"]]
#
# # 通过 "时间" 和 "卫星ID" 进行合并，仅保留匹配的数据
# merged_result = pd.merge(merged_data, stat_subset, on=["time", "satellite"], how="inner")
#
#
# # 保存合并后的数据
# merged_result.to_csv("F:\\GNSSdata\\rf_train\\merged_snr_stat1.csv", index=False)
# print("合并完成，结果已保存至 merged_snr_stat1.csv")



#------------------------------------------伪距残差归一化-------------------------------------------
# import pandas as pd
#
# file_path = 'F:\\GNSSdata\\rf_train\\merged_snr_stat1.csv'
# df = pd.read_csv(file_path, dtype={'time': str})
# print(df.head(10))
#
# # 处理SNR特征
# df['snr'] = df['snr'] / 1000
#
# df['normalized_resp'] = df.groupby('time')['resp'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))
#
#
# # 保存修正后的数据
# df.to_csv("F:\\GNSSdata\\rf_train\\normalized.csv", index=False)








