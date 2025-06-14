from utils.data_parser import DataParser
import os

#解析卫星数据
# file_path = "files\\satellite_data.txt"  # 你的数据文件路径
# absolute_file_path = os.path.abspath(file_path)
# parsed_data = DataParser.parse_satellite_data(absolute_file_path)
# ✅ 遍历并打印解析的数据
# for epoch, satellites in parsed_data.items():
#     print(f"\n📅 Epoch Time: {epoch}")
#     for sat in satellites:
#         print(
#             f"   🛰️ Satellite ID: {sat['satellite_id'].ljust(4)} | "
#             f"X: {str(sat['X']).rjust(16)} | "
#             f"Y: {str(sat['Y']).rjust(16)} | "
#             f"Z: {str(sat['Z']).rjust(16)} | "
#             f"SNR: {str(sat['SNR']).rjust(5)}"
#         )
#-------------------------------------------------------------------------------------------------------

# #解析定位文件数据
# file_path = "files\\initial_positions.pos"  # 你的数据文件路径
# absolute_file_path = os.path.abspath(file_path)
# position_data = DataParser.parse_position_data(absolute_file_path)
# print("📌 解析的位置信息：")
# for timestamp, data in position_data.items():
#     print(f"⏳ 时间: {timestamp}")
#     print(f"   🌍 ECEF 坐标: X={data['X']:.3f}, Y={data['Y']:.3f}, Z={data['Z']:.3f}")
#     print(f"   🗺️ 原始 WGS84 坐标: 纬度={data['original_lat']:.6f}, 经度={data['original_lon']:.6f}, 高度={data['original_height']:.2f}")
#     print("-" * 80)  # 分隔线

#-------------------------------------------------------------------------------------------------------

# #解析建筑文件数据
# data=DataParser()
# buildings = data.parse_building_data("files\\buildings.txt")
# for i, building in enumerate(buildings):
#     polygon = building["polygon"]
#     height = building["height"]
#     center = building["center"]
#
#     print(f"建筑 {i + 1}:")
#     print(f"  高度: {height}")
#     print(f"  中心点 (ECEF): ({center.x}, {center.y}, {center.z})")
#     print(f"  多边形顶点:")
#     for coord in polygon.exterior.coords:
#         print(f"    {coord}")
#     print("-")

#----------------------------------------------------------------------------------------------------------

# #3D 可视化
# import numpy as np
# import trimesh
# import matplotlib.pyplot as plt
#
# def create_building_mesh(polygon, height):
#     """生成建筑三维网格（ENU坐标系下）"""
#     vertices_2d = np.array(polygon)
#     vertices_bottom = np.hstack([vertices_2d, np.zeros((len(vertices_2d), 1))])
#     vertices_top = np.hstack([vertices_2d, np.full((len(vertices_2d), 1), height)])
#     vertices = np.vstack([vertices_bottom, vertices_top])
#
#     faces = []
#     n = len(vertices_2d)
#
#     # 底面三角剖分（假设凸多边形）
#     for i in range(1, n-1):
#         faces.append([0, i, i+1])
#
#     # 顶面三角剖分
#     for i in range(1, n-1):
#         faces.append([n, n+i, n+i+1])
#
#     # 侧面四边形拆分为三角形
#     for i in range(n):
#         i_next = (i + 1) % n
#         i_top = i + n
#         i_next_top = i_next + n
#         faces.append([i, i_next, i_next_top])
#         faces.append([i, i_next_top, i_top])
#
#     return trimesh.Trimesh(vertices=vertices, faces=faces)
#
# # 示例多边形（四边形）
# polygon = [(0, 0), (1, 0), (1, 1), (0, 1)]
# height = 2.0
#
# # 生成3D建筑网格
# mesh = create_building_mesh(polygon, height)
#
# # 显示3D模型
# mesh.show()
import logging
from shapely.geometry import Polygon, Point
# from pyproj import Transformer
from utils.coordinate_transform import CoordinateTransform


#-----------------------------------------------------------------------------------------------------
import csv
import os

# input_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-08\\P4\\rtklib_vs\\satpos.txt'
# output_csv = 'F:\\GNSSdata\\Android GNSS data\\2025-04-08\\all_snr_output.csv'
# snr_data = []

# with open(input_file, 'r', encoding='utf-8') as f:
#     for line in f:
#         line = line.strip()
#         if line.startswith('time'):
#             continue
#         else:
#             data = line.split()
#             snr = float(data[3])
#             snr_data.append(snr)
#
# # 检查输出文件是否已存在
# file_exists = os.path.exists(output_csv)
#
# # 追加写入 CSV 文件
# with open(output_csv, 'a', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#
#     # 仅首次写入表头
#     if not file_exists:
#         writer.writerow(['Index', 'SNR'])
#
#     # 获取当前文件已有多少行数据，用于继续编号
#     start_index = 1
#     if file_exists:
#         with open(output_csv, 'r', encoding='utf-8') as f:
#             existing_rows = sum(1 for _ in f) - 1  # 不算表头
#             start_index = existing_rows + 1
#
#     for idx, snr in enumerate(snr_data, start=start_index):
#         writer.writerow([idx, snr])
#--------------------------------------------手机采集的数据SNR分布-------------------------------------------
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # 读取 CSV 文件
# csv_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-08\\all_snr_output.csv'
# df = pd.read_csv(csv_file)
#
# # 🔍 排除 SNR 为 0 的数据
# df = df[df['SNR'] > 0]
# df['SNR'] = df['SNR']/1000
# # 1️⃣ 折线图（观察信噪比随编号变化）
# plt.figure(figsize=(10, 4))
# plt.plot(df['Index'], df['SNR'], color='blue', linewidth=1)
# plt.title('SNR Trend (SNR > 0)')
# plt.xlabel('Index')
# plt.ylabel('SNR (dB-Hz)')
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
# # 2️⃣ 直方图（观察 SNR 分布情况）
# plt.figure(figsize=(6, 4))
# plt.hist(df['SNR'], bins=30, color='skyblue', edgecolor='black')
# plt.title('SNR Distribution ')
# plt.xlabel('SNR (dB-Hz)')
# plt.ylabel('Count')
# plt.axvline(df['SNR'].mean(), color='red', linestyle='--', label=f'Mean = {df["SNR"].mean():.2f}')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
# # 3️⃣ 箱线图（可选：查看是否有异常值）
# plt.figure(figsize=(4, 5))
# plt.boxplot(df['SNR'], vert=True)
# plt.title('SNR Boxplot (SNR > 0)')
# plt.ylabel('SNR (dB-Hz)')
# plt.grid(True)
# plt.tight_layout()
# plt.show()

#------------------------------------------------

import numpy as np
from utils.density_clustering import shadow_matching_density_clustering
# 生成模拟数据（20个候选点）
np.random.seed(42)
scores = np.hstack([
    np.random.uniform(0, 10, (20, 1)),  # 分数列
    np.random.normal(loc=[-2687743, 4299652, 3855193], scale=50, size=(20, 3))  # ECEF坐标
])

# 调用函数
result = shadow_matching_density_clustering(
    scores=scores,
    eps=3,      # 邻域半径（根据网格分辨率动态调整）
    min_samples=3,
    score_threshold_ratio=0.4
)

print("Final ECEF Position:", result)