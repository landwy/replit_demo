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