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



import numpy as np
from .coordinate_transform import CoordinateTransform
from shapely.geometry import Polygon, Point, LineString
import trimesh
from trimesh.ray import ray_triangle

class VisibilityCalculator:
    def __init__(self, snr_threshold=30):
        self.snr_threshold = snr_threshold
        self.coord_transform = CoordinateTransform()


    @staticmethod
    def should_check_building(sat_ecef, ground_ecef, building_ecef):
        """判断是否需要检查建筑遮挡"""
        az_s = compute_azimuth(ground_ecef, sat_ecef)  # 计算卫星方位角
        az_b = compute_azimuth(ground_ecef, building_ecef)  # 计算建筑中心点方位角

        delta_az = abs(az_s - az_b) % 360  # 计算方位角夹角
        if abs(delta_az - 180) < 15:  # 若夹角接近 180°（阈值可调整）
            return False  # 说明卫星和地面点在建筑的同侧，无需检测
        return True  # 需要进行遮挡检测

    def check_observed_visibility(self, snr):
        """
        Check satellite visibility based on SNR
        """
        return snr >= self.snr_threshold * 1000



def compute_azimuth(ecef_source, ecef_target):
    """计算 ecef_target 相对于 ecef_source 的方位角（Azimuth）"""
    dx, dy, _ = np.array(ecef_target) - np.array(ecef_source)
    azimuth = np.degrees(np.arctan2(dy, dx)) % 360
    return azimuth



#--------------------------------ECEF下创建建筑网格---------------------------------------------
def create_building_mesh(bottom_ecef,top_ecef):
    """基于 ENU 坐标系生成建筑网格（底面 polygon_2d，顶面沿 U 轴提升 height）"""
    vertices = np.vstack([bottom_ecef,top_ecef])

    faces = []
    n = len(bottom_ecef)

    # 底面三角剖分
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])

    # 顶面三角剖分
    for i in range(1, n - 1):
        faces.append([n, n + i, n + i + 1])

    # 侧面四边形拆分为三角形
    for i in range(n):
        i_next = (i + 1) % n
        i_top, i_next_top = i + n, i_next + n
        faces.append([i, i_next, i_next_top])
        faces.append([i, i_next_top, i_top])

    faces = [face for face in faces if all(0 <= idx < len(vertices) for idx in face)]

    # print(vertices, faces)
    return trimesh.Trimesh(vertices=vertices, faces=faces)


def preprocess_buildings(buildings):
    """预处理建筑物，将其转换为 ENU 坐标网格"""
    #ref_lon, ref_lat, ref_alt = CoordinateTransform.convert_ecef_to_wgs(*ref_ecef)
    # ref_lon, ref_lat, ref_alt = CoordinateTransform.convert_ecef_to_wgs(ref_ecef[0], ref_ecef[1], ref_ecef[2])


    building_meshes = []
    for building in buildings:
        polygon_geo = building["polygon"]   #wgs84坐标下的多边形
        height = building["height"]

        # 将建筑底面转换为 ECEF 坐标
        bottom_ecef = [CoordinateTransform().convert_wgs_to_ecef(lat, lon, 12) for lat, lon in polygon_geo.exterior.coords]
        bottom_ecef = bottom_ecef[:-1]  #去掉最后一个重复点

        # 顶面角点（高度叠加）
        # top_ecef = [(x, y, z + height * np.cos(np.radians(lat))) for (lat, _), (x, y, z) in zip(polygon_geo.exterior.coords, bottom_ecef)]
        top_ecef = [(x, y, z + height) for (x, y, z) in bottom_ecef]
        top_ecef = top_ecef[:-1]  #去掉最后一个重复点
        # print(bottom_ecef)

        # 创建建筑 3D 网格
        building_mesh = create_building_mesh(np.array(bottom_ecef),np.array(top_ecef))

        building_meshes.append(building_mesh)

    return building_meshes


# ------------------  遮挡检测逻辑 ------------------

def should_check_building(sat_ecef, ground_ecef, building_ecef):
    """判断是否需要检查建筑遮挡"""
    az_s = compute_azimuth(ground_ecef, sat_ecef)  # 计算卫星方位角
    az_b = compute_azimuth(ground_ecef, building_ecef)  # 计算建筑中心点方位角

    delta_az = abs(az_s - az_b) % 360  # 计算方位角夹角
    if abs(delta_az - 180) < 15:  # 若夹角接近 180°（阈值可调整）
        return False  # 说明卫星和地面点在建筑的同侧，无需检测
    return True  # 需要进行遮挡检测



def is_occluded_ecef(sat_ecef, grid_ecef, buildings_meshes_ecef):
    """
    兼容性遮挡判断（支持有无 pyembree 的环境）
    """
    ray_origin = np.array(sat_ecef)
    ray_direction = np.array(grid_ecef) - ray_origin
    ray_length = np.linalg.norm(ray_direction)
    if ray_length < 1e-6:  # 避免零向量
        return False
    ray_dir_normalized = ray_direction / ray_length

    # 如果有 pyembree 加速
    if trimesh.ray.has_embree:
        all_buildings = trimesh.util.concatenate(buildings_meshes_ecef)
        intersector = trimesh.ray.ray_pyembree.RayMeshIntersector(all_buildings)
        locations, _, _ = intersector.intersects_location(
            ray_origins=[ray_origin],
            ray_directions=[ray_dir_normalized]
        )
        return any(np.linalg.norm(loc - ray_origin) < ray_length for loc in locations)

    # 无 pyembree 时的纯 Python 实现
    else:
        # 遍历所有建筑的所有三角形
        for mesh in buildings_meshes_ecef:
            # 获取三角形的顶点坐标 [n_triangles, 3, 3]
            triangles = mesh.triangles
            #print("三角形数据:", triangles)

            # 批量检测射线与三角形的相交
            hits = ray_triangle.ray_triangle_id(
                ray_origins=np.array([ray_origin]),
                ray_directions=np.array([ray_dir_normalized]),
                triangles=triangles
            )

            # 如果存在有效交点且距离小于射线长度
            if hits[0].size > 0 and hits[0][0] != -1:
                return True
        return False
