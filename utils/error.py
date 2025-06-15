import pandas as pd
import numpy as np
from pyproj import Proj, Transformer
import matplotlib.pyplot as plt

#-----------------------------------------------------计算谷歌地球影像定位精度-------------------------------------------------------------
# # 读取Excel数据
# df = pd.read_excel("F:\\GNSSdata\\NAVTEST\\2025-01-04\\playground.xlsx", engine='openpyxl')
#
# # 定义坐标转换函数（WGS84转UTM）
# def wgs84_to_utm(lon, lat):
#     utm_zone = int((lon + 180) // 6 + 1)  # 自动计算UTM区域
#     proj_utm = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
#     x, y = proj_utm(lon, lat)
#     return x, y
#
# # 转换RTK和Google坐标到UTM
# rtk_utm = [wgs84_to_utm(lon, lat) for lon, lat in zip(df['RTK/IMU经度（°）'], df['RTK/IMU纬度（°）'])]
# google_utm = [wgs84_to_utm(lon, lat) for lon, lat in zip(df['Google经度（°）'], df['Google纬度（°）'])]
#
# # 添加UTM坐标到DataFrame
# df['RTK_X'] = [x for x, y in rtk_utm]
# df['RTK_Y'] = [y for x, y in rtk_utm]
# df['Google_X'] = [x for x, y in google_utm]
# df['Google_Y'] = [y for x, y in google_utm]
#
# #-----------------------------------------------------------------------------------
# # 计算XY方向误差和欧氏距离
# df['ΔX'] = df['RTK_X'] - df['Google_X']
# df['ΔY'] = df['RTK_Y'] - df['Google_Y']
# df['误差距离'] = np.sqrt(df['ΔX']**2 + df['ΔY']**2)
#
# # 计算统计指标
# stats = {
#     "平均误差 (米)": df['误差距离'].mean(),
#     "标准差 (米)": df['误差距离'].std(),
#     "RMSE (米)": np.sqrt((df['误差距离']**2).mean()),
#     "最大误差 (米)": df['误差距离'].max()
# }
# print(pd.Series(stats).to_string())
# #---------------------------------------------------------------------------------------
# # 散点图：RTK vs Google位置
# plt.figure(figsize=(10, 6))
# plt.scatter(df['RTK_X'], df['RTK_Y'], c='blue', label='RTK', s=20, alpha=0.7)
# plt.scatter(df['Google_X'], df['Google_Y'], c='red', label='Google Earth', s=20, alpha=0.7)
# plt.xlabel('UTM X (米)')
# plt.ylabel('UTM Y (米)')
# plt.title('RTK与谷歌地球坐标对比')
# plt.legend()
# plt.grid(True)
# plt.show()
#
# # 误差分布直方图
# plt.figure(figsize=(8, 5))
# plt.hist(df['误差距离'], bins=20, color='green', edgecolor='black')
# plt.xlabel('误差距离 (米)')
# plt.ylabel('频数')
# plt.title('误差距离分布直方图')
# plt.show()
#
# # 误差方向玫瑰图（极坐标）
# angles = np.arctan2(df['ΔY'], df['ΔX'])
# magnitudes = df['误差距离']
# plt.figure(figsize=(6, 6))
# ax = plt.subplot(111, projection='polar')
# ax.scatter(angles, magnitudes, alpha=0.5)
# ax.set_title('误差方向与大小分布')
# plt.show()
# #----------------------------------------------------------------------------------------------
# # 保存处理后的数据
# df.to_excel("analysis_result.xlsx", index=False)
#
# # 保存统计结果
# pd.Series(stats).to_excel("statistics.xlsx")



#------------------------------------------------------计算卫星定位误差------------------------------------------------------------------------------
# position_data = {}
# ground_truth_lat = 120.269685
# ground_truth_lon = 31.496133
# filename = 'F:\\GNSSdata\\RTKLIB\\myrtklib\\data\\spp.pos'
# with open(filename, 'r', encoding='utf-8') as f:
#     for line in f:
#         line = line.strip()
#                 # Skip comment lines starting with %
#         if line.startswith('%'):
#             continue
#
#         data = line.split()
#         if len(data) >= 15:  # Ensure we have all required fields
#             try:
#                 # Parse date and time
#                 date_str = data[0]
#                 time_str = data[1]
#                 timestamp = f"{date_str} {time_str}"
#
#                 lat = float(data[2])  # latitude in degrees
#                 long = float(data[3])  # longitude in degrees
#                 alt = float(data[4])  # height in meters
#
#                 position_data[timestamp] = {
#                     'lat': lat,
#                     'lon': long,
#                     'alt': alt,
#                 }
#             except (ValueError, IndexError) as e:
#                 continue


# #---------------------------------------------计算谷歌地球影像精度并进行可视化-----------------------------------------------
# import numpy as np
# import matplotlib.pyplot as plt
# from pyproj import Transformer
#
# import matplotlib.pyplot as plt
# # 设置中文字体为黑体（SimHei），确保支持中文显示
# plt.rcParams['font.sans-serif'] = ['SimHei']
# # 解决负号显示问题（若有负号相关绘图需求）
# plt.rcParams['axes.unicode_minus'] = False
#
# # 坐标数据（WGS84经纬度）
# rtk_points = {
#     'P1': (120.2538854, 31.47293789),
#     'P2': (120.253710893816, 31.4720045609211),
#     'P3': (120.254441340196, 31.4719200554348),
#     'P4': (120.254622549473, 31.4728645177419),
#     'P2-3': (120.254158472919, 31.4719211199189)
# }
#
# ge_points = {
#     'P1': (120.253889, 31.472944),
#     'P2': (120.253718, 31.472019),
#     'P3': (120.254441, 31.471917),
#     'P4': (120.254606, 31.472845),
#     'P2-3': (120.254162, 31.471930)
# }
#
# # 转换经纬度到UTM坐标系（无锡校区UTM Zone 50N）
# transformer = Transformer.from_crs("EPSG:4326", "EPSG:32650")
#
# # 存储误差数据
# errors = {
#     'names': [],
#     'delta_e': [],
#     'delta_n': [],
#     'delta_d': []
# }
#
# for name in rtk_points:
#     # RTK坐标转UTM
#     rtk_easting, rtk_northing = transformer.transform(
#         rtk_points[name][1], rtk_points[name][0]
#     )
#     # GE坐标转UTM
#     ge_easting, ge_northing = transformer.transform(
#         ge_points[name][1], ge_points[name][0]
#     )
#     # 计算各向误差
#     delta_e = ge_easting - rtk_easting
#     delta_n = ge_northing - rtk_northing
#     delta_d = np.sqrt(delta_e ** 2 + delta_n ** 2)
#     print(name,f"东向误差: {delta_e:.2f} m, 北向误差: {delta_n:.2f} m, 平面误差: {delta_d:.2f} m")
#
#     # 存储结果
#     errors['names'].append(name)
#     errors['delta_e'].append(delta_e)
#     errors['delta_n'].append(delta_n)
#     errors['delta_d'].append(delta_d)
#
# # 统计指标
# rmse_d = np.sqrt(np.mean(np.array(errors['delta_d']) ** 2))
# rmse_e = np.sqrt(np.mean(np.array(errors['delta_e']) ** 2))
# rmse_n = np.sqrt(np.mean(np.array(errors['delta_n']) ** 2))
#
# # 可视化
# plt.figure(figsize=(12, 8))
#
# # 子图1：东向误差（ΔE）
# plt.subplot(3, 1, 1)
# plt.bar(errors['names'], errors['delta_e'], color='skyblue', edgecolor='black', label='ΔE')
# plt.axhline(0, color='gray', linestyle='--')
# plt.ylabel('东向误差 (m)')
# plt.title('东向误差（正值为GE偏东，负值为偏西）')
#
# # 子图2：北向误差（ΔN）
# plt.subplot(3, 1, 2)
# plt.bar(errors['names'], errors['delta_n'], color='lightgreen', edgecolor='black', label='ΔN')
# plt.axhline(0, color='gray', linestyle='--')
# plt.ylabel('北向误差 (m)')
# plt.title('北向误差（正值为GE偏北，负值为偏南）')
#
# # 子图3：平面误差（ΔD）
# plt.subplot(3, 1, 3)
# plt.bar(errors['names'], errors['delta_d'], color='salmon', edgecolor='black', label='ΔD')
# plt.axhline(rmse_d, color='blue', linestyle='--', label=f'RMSE = {rmse_d:.2f} m')
# plt.ylabel('平面误差 (m)')
# plt.xlabel('测点')
# plt.title('平面误差与RMSE')
# plt.legend()
#
# plt.tight_layout()
# plt.show()
#
# # 输出统计结果
# print(f"东向RMSE: {rmse_e:.2f} m, 北向RMSE: {rmse_n:.2f} m, 平面RMSE: {rmse_d:.2f} m")
#----------------------------------------美化后的画图代码-----------------------------------------------
# import matplotlib.pyplot as plt
# import numpy as np
#
#  #设置中文字体为黑体（SimHei），确保支持中文显示
# plt.rcParams['font.sans-serif'] = ['SimHei']
# # 解决负号显示问题（若有负号相关绘图需求）
# plt.rcParams['axes.unicode_minus'] = False
#
# # 测点标签
# labels = ['P1', 'P2', 'P3', 'P4', 'P2-3']
#
# # 各向误差数据（单位：米）
# east_error = [0.32, 0.63, -0.02, -1.51, 0.31]
# north_error = [0.69, 1.62, -0.34, -2.21, 0.99]
# planar_error = [0.76, 1.74, 0.34, 2.68, 1.04]
#
# # 已知整体RMSE
# east_rmse = 0.76
# north_rmse = 1.35
# planar_rmse = 1.55
#
# # 设置画布
# x = np.arange(len(labels))
# width = 0.25
#
# plt.figure(figsize=(10, 6))
# plt.bar(x - width, east_error, width, label=f'东向误差 (RMSE = {east_rmse:.2f} m)', color='#1f77b4')
# plt.bar(x, north_error, width, label=f'北向误差 (RMSE = {north_rmse:.2f} m)', color='#ff7f0e')
# plt.bar(x + width, planar_error, width, label=f'平面误差 (RMSE = {planar_rmse:.2f} m)', color='#2ca02c')
#
# # 添加RMSE参考线
# plt.axhline(east_rmse, color='#1f77b4', linestyle='--', linewidth=1)
# plt.axhline(north_rmse, color='#ff7f0e', linestyle='--', linewidth=1)
# plt.axhline(planar_rmse, color='#2ca02c', linestyle='--', linewidth=1)
#
# # 格式设置
# plt.ylabel('误差 (m)', fontsize=12)
# plt.xlabel('测点', fontsize=12)
# plt.title('各测点误差与整体RMSE参考线（Google Earth影像）', fontsize=14)
# plt.xticks(x, labels, fontsize=11)
# plt.yticks(fontsize=11)
# plt.axhline(0, color='gray', linewidth=0.8, linestyle='--')
# plt.grid(True, linestyle='--', alpha=0.3)
# plt.legend(fontsize=10)
# plt.tight_layout()
#
# # 保存或显示图
# plt.savefig('google_earth_error_with_rmse_reference.png', dpi=300)
# plt.show()

#------------------------------------------------单个点手机定位误差分析-----------------------------------------------
# import numpy as np
# from pyproj import Transformer
#
#
# def calculate_position_errors(pos_file, true_lon, true_lat):
#     """
#     解析RTKPOST生成的.pos文件，计算东向、北向及平面误差的均值与RMSE。
#
#     参数：
#         pos_file (str): .pos文件路径
#         true_lon (float): 真实经度（WGS84）
#         true_lat (float): 真实纬度（WGS84）
#
#     返回：
#         dict: 包含东向、北向、平面误差的均值与RMSE的字典。
#     """
#
#     # 自动确定UTM分区
#     def get_utm_epsg(lon, lat):
#         zone = int((lon + 180) // 6 + 1)
#         return 32600 + zone if lat >= 0 else 32700 + zone
#
#     utm_epsg = get_utm_epsg(true_lon, true_lat)
#     transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{utm_epsg}")
#
#     # 转换真实坐标到UTM
#     true_easting, true_northing = transformer.transform(true_lat, true_lon)
#
#     # 读取.pos文件并计算误差
#     east_errors, north_errors, plane_errors = [], [], []
#
#     with open(pos_file, 'r') as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("%"):  # 跳过注释行和空行
#                 continue
#
#             parts = line.split()
#             if len(parts) < 4:  # 确保至少包含时间、纬度、经度、高度
#                 continue
#
#             try:
#                 # 解析纬度为第3列（索引2），经度为第4列（索引3）
#                 lat = float(parts[2])
#                 lon = float(parts[3])
#             except (IndexError, ValueError):
#                 continue
#
#             # 转换当前坐标到UTM
#             current_easting, current_northing = transformer.transform(lat, lon)
#
#             # 计算误差
#             e_error = current_easting - true_easting
#             n_error = current_northing - true_northing
#             p_error = np.sqrt(e_error ** 2 + n_error ** 2)
#
#             east_errors.append(abs(e_error))
#             north_errors.append(abs(n_error))
#             plane_errors.append(abs(p_error))
#
#     # 计算统计量
#     stats = {
#         "East": {
#             "Mean": np.mean(east_errors),
#             "RMSE": np.sqrt(np.mean(np.square(east_errors))),
#             "Min": np.min(east_errors),
#             "Max": np.max(east_errors),
#         },
#         "North": {
#             "Mean": np.mean(north_errors),
#             "RMSE": np.sqrt(np.mean(np.square(north_errors))),
#             "Min": np.min(north_errors),
#             "Max": np.max(north_errors),
#         },
#         "Planar": {
#             "Mean": np.mean(plane_errors),
#             "RMSE": np.sqrt(np.mean(np.square(plane_errors))),
#             "Min": np.min(plane_errors),
#             "Max": np.max(plane_errors),
#         }
#     }
#
#     return stats
#
# #P2   120.2537109, 31.47200456
#
#
# # 示例调用
# if __name__ == "__main__":
#     results = calculate_position_errors("F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P1).pos", 120.269673 , 31.496200)
#     # 输出结果
#     for direction in results:
#         print(f"{direction} Error:")
#         print(f"  Min = {results[direction]['Min']:.4f} m")
#         print(f"  Max = {results[direction]['Max']:.4f} m")
#         print(f"  Mean = {results[direction]['Mean']:.4f} m")
#         print(f"  RMSE = {results[direction]['RMSE']:.4f} m\n")


#---------------------------------------------------------------------------分析手机定位误差并保存文件----------------------------------------------
# import numpy as np
# import csv
# import os
# from datetime import datetime
# from pyproj import Transformer
#
#
# def calculate_rtk_errors(pos_file, true_lon, true_lat, output_csv="results.csv"):
#     """
#     解析.pos文件并计算结果，将统计量追加到CSV文件
#
#     参数：
#         pos_file (str): .pos文件路径
#         true_lon (float): 真实经度（WGS84）
#         true_lat (float): 真实纬度（WGS84）
#         output_csv (str): 输出CSV文件路径
#     """
#
#     # 自动确定UTM分区
#     def get_utm_epsg(lon, lat):
#         zone = int((lon + 180) // 6 + 1)
#         return 32600 + zone if lat >= 0 else 32700 + zone
#
#     utm_epsg = get_utm_epsg(true_lon, true_lat)
#     transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{utm_epsg}")
#
#     # 转换真实坐标到UTM
#     true_easting, true_northing = transformer.transform(true_lat, true_lon)
#
#     # 读取数据
#     east_errors, north_errors, plane_errors = [], [], []
#
#     with open(pos_file, 'r') as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("%"):
#                 continue
#
#             parts = line.split()
#             if len(parts) < 4:
#                 continue
#
#             try:
#                 lat = float(parts[2])
#                 lon = float(parts[3])
#             except (IndexError, ValueError):
#                 continue
#
#             # 坐标转换
#             current_easting, current_northing = transformer.transform(lat, lon)
#
#             # 计算误差
#             e_error = current_easting - true_easting
#             n_error = current_northing - true_northing
#             p_error = np.sqrt(e_error ** 2 + n_error ** 2)
#
#             east_errors.append(abs(e_error))
#             north_errors.append(abs(n_error))
#             plane_errors.append(abs(p_error))
#
#     # 计算统计指标
#     stats = {
#         "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "East Min": np.min(east_errors) if east_errors else np.nan,
#         "East Max": np.max(east_errors) if east_errors else np.nan,
#         "East Mean": np.mean(east_errors) if east_errors else np.nan,
#         "East RMSE": np.sqrt(np.mean(np.square(east_errors))) if east_errors else np.nan,
#         "North Min": np.min(north_errors) if north_errors else np.nan,
#         "North Max": np.max(north_errors) if north_errors else np.nan,
#         "North Mean": np.mean(north_errors) if north_errors else np.nan,
#         "North RMSE": np.sqrt(np.mean(np.square(north_errors))) if north_errors else np.nan,
#         "2D Min": np.min(plane_errors) if plane_errors else np.nan,
#         "2D Max": np.max(plane_errors) if plane_errors else np.nan,
#         "2D Mean": np.mean(plane_errors) if plane_errors else np.nan,
#         "2D RMSE": np.sqrt(np.mean(np.square(plane_errors))) if plane_errors else np.nan
#     }
#
#     # 定义CSV列顺序
#     fieldnames = [
#         "Timestamp",
#         "East Min", "East Max", "East Mean", "East RMSE",
#         "North Min", "North Max", "North Mean", "North RMSE",
#         "2D Min", "2D Max", "2D Mean", "2D RMSE"
#     ]
#
#     # 写入/追加到CSV文件
#     file_exists = os.path.isfile(output_csv)
#
#     with open(output_csv, 'a', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#
#         if not file_exists:
#             writer.writeheader()
#
#         writer.writerow(stats)
#
#     return stats
#
# #调用
# if __name__ == "__main__":
#     # 真实坐标示例
#     results = calculate_rtk_errors(
#         pos_file="F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P1).pos",
#         # true_lat = 31.496089,
#         # true_lon = 120.269727,
#         true_lat=31.496194,
#         true_lon = 120.269652,
#         output_csv="F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P1)_errors(new).csv"
#     )
#     print("Results saved to CSV:")
#     print(results)
#
# #-------------------------------------------手机定位平滑后的误差---------------------------------------------
# import csv
# import os
# import numpy as np
# from datetime import datetime
# from pyproj import Transformer
#
# def compute_error_stats(lat_list, lon_list, transformer, true_easting, true_northing):
#     east_errors, north_errors, plane_errors = [], [], []
#
#     for lat, lon in zip(lat_list, lon_list):
#         easting, northing = transformer.transform(lon, lat)  # 注意顺序：lon, lat
#         e_error = easting - true_easting
#         n_error = northing - true_northing
#         p_error = np.sqrt(e_error ** 2 + n_error ** 2)
#
#         east_errors.append(abs(e_error))
#         north_errors.append(abs(n_error))
#         plane_errors.append(p_error)
#
#     # 计算统计量
#     stats = {
#         "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "East Min": np.min(east_errors) if east_errors else np.nan,
#         "East Max": np.max(east_errors) if east_errors else np.nan,
#         "East Mean": np.mean(east_errors) if east_errors else np.nan,
#         "East RMSE": np.sqrt(np.mean(np.square(east_errors))) if east_errors else np.nan,
#         "North Min": np.min(north_errors) if north_errors else np.nan,
#         "North Max": np.max(north_errors) if north_errors else np.nan,
#         "North Mean": np.mean(north_errors) if north_errors else np.nan,
#         "North RMSE": np.sqrt(np.mean(np.square(north_errors))) if north_errors else np.nan,
#         "2D Min": np.min(plane_errors) if plane_errors else np.nan,
#         "2D Max": np.max(plane_errors) if plane_errors else np.nan,
#         "2D Mean": np.mean(plane_errors) if plane_errors else np.nan,
#         "2D RMSE": np.sqrt(np.mean(np.square(plane_errors))) if plane_errors else np.nan
#     }
#
#     return stats
#
# def analyze_csv_file(csv_path, true_lat, true_lon, output_csv):
#     # 初始化转换器（WGS84 -> UTM Zone 48N 为例）
#     transformer = Transformer.from_crs("EPSG:4326", "EPSG:32651", always_xy=True)
#     true_easting, true_northing = transformer.transform(true_lon, true_lat)
#
#     # 读取 CSV 中的经纬度
#     lat_list, lon_list = [], []
#
#     with open(csv_path, 'r') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             try:
#                 lat = float(row['Latitude'])
#                 lon = float(row['Longitude'])
#                 lat_list.append(lat)
#                 lon_list.append(lon)
#             except (KeyError, ValueError):
#                 continue  # 忽略有问题的行
#
#     # 计算误差统计
#     stats = compute_error_stats(lat_list, lon_list, transformer, true_easting, true_northing)
#
#     # 定义输出字段顺序
#     fieldnames = [
#         "Timestamp",
#         "East Min", "East Max", "East Mean", "East RMSE",
#         "North Min", "North Max", "North Mean", "North RMSE",
#         "2D Min", "2D Max", "2D Mean", "2D RMSE"
#     ]
#
#     # 写入结果
#     file_exists = os.path.isfile(output_csv)
#     with open(output_csv, 'a', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         if not file_exists:
#             writer.writeheader()
#         writer.writerow(stats)
#
# # === 示例调用 ===
# # 替换为你的真实路径和真值位置
# input_csv = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P6)_smoothed.csv'
# output_csv = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P6)_smoothed_errors(new).csv'
#
#
# true_lat =31.496365
# true_lon =120.269643
#
#
#
#
# analyze_csv_file(input_csv, true_lat, true_lon, output_csv)





