import pandas as pd
import numpy as np
import pyproj

# 读取CSV文件
csv_path = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\GNSS_SM\\gnss_sm_preproc(P1).csv'
df = pd.read_csv(csv_path)

# 真实参考点（经纬度）  (单位：度）
# P1
true_lat =31.496194
true_lon =120.269652

# P2
# true_lat =31.496033
# true_lon =120.269650

# P3
# true_lat =31.495794
# true_lon =120.269597

# ECEF -> UTM转换器
ecef = pyproj.CRS('EPSG:4978')  # ECEF
utm = pyproj.CRS('EPSG:32651')  # 例如香港在UTM Zone 50N (EPSG:32650)，根据你实际情况改
transformer_ecef_to_utm = pyproj.Transformer.from_crs(ecef, utm, always_xy=True)

# WGS84经纬度 -> UTM
transformer_wgs84_to_utm = pyproj.Transformer.from_crs('EPSG:4326', utm, always_xy=True)
ref_east, ref_north = transformer_wgs84_to_utm.transform(true_lon, true_lat)

# 存储误差
east_errors = []
horizontal_errors = []

# 遍历每个历元
for index, row in df.iterrows():
    x, y, z = row['X'], row['Y'], row['Z']
    east, north, _ = transformer_ecef_to_utm.transform(x, y, z)

    east_error = east - ref_east
    north_error = north - ref_north
    horizontal_error = np.sqrt(east_error**2 + north_error**2)

    east_errors.append(east_error)
    horizontal_errors.append(horizontal_error)

# 转成数组方便计算
east_errors = np.array(east_errors)
horizontal_errors = np.array(horizontal_errors)

# 统计东向误差小于8.5米的历元数量和比例
east_within_threshold = np.sum(np.abs(east_errors) < 8.5)
east_within_ratio = east_within_threshold / len(east_errors)

# 统计水平误差小于8.5米的历元数量和比例
horizontal_within_threshold = np.sum(horizontal_errors < 8.5)
horizontal_within_ratio = horizontal_within_threshold / len(horizontal_errors)

# 打印结果
print(f'东向误差小于8.5米的历元数量：{east_within_threshold}，占比：{east_within_ratio:.2%}')
print(f'水平误差小于8.5米的历元数量：{horizontal_within_threshold}，占比：{horizontal_within_ratio:.2%}')
