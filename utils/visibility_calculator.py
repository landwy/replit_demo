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

    @staticmethod
    def predict_satellite_visibility(sat_ecef, ground_ecef, buildings):
        """
        判断卫星到地面点的信号是否被建筑遮挡。
        :param sat_ecef: 卫星ECEF坐标 (x, y, z)
        :param ground_ecef: 地面点ECEF坐标 (x, y, z)
        :param buildings: 解析出的建筑信息列表
        :return: 是否被遮挡 (True = 遮挡, False = 无遮挡)
        """
        #ground_x, ground_y, ground_z = ground_ecef
        #satellite_point = (sat_ecef['X'], sat_ecef['Y'], sat_ecef['Z'])
        # #signal_path = LineString([satellite_point, ground_point])  # 生成卫星到地面点的直线

        sat_x, sat_y, sat_z = sat_ecef['X'], sat_ecef['Y'], sat_ecef['Z']
        ground_x, ground_y, ground_z = ground_ecef['X'], ground_ecef['Y'], ground_ecef['Z']
        signal_path = LineString([(sat_x, sat_y, sat_z), (ground_x, ground_y, ground_z)])

        for building in buildings:
            base_polygon = building["polygon"]
            height = building["height"]

            # 将地面多边形扩展到3D，形成建筑侧面
            building_walls = []
            coords = list(base_polygon.exterior.coords)
            for i in range(len(coords) - 1):
                p1 = (coords[i][0], coords[i][1], 0)
                p2 = (coords[i + 1][0], coords[i + 1][1], 0)
                p3 = (coords[i + 1][0], coords[i + 1][1], height)
                p4 = (coords[i][0], coords[i][1], height)

                wall = Polygon([p1, p2, p3, p4])
                building_walls.append(wall)

            # 检查信号路径是否与任何建筑侧面相交
            for wall in building_walls:
                if signal_path.intersects(wall):
                    return True  # 信号被遮挡
        return False  # 信号未遮挡

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


# ------------------  建筑网格创建 ------------------

# def create_building_mesh(polygon_2d, height):
#     """基于 ENU 坐标系生成建筑网格（底面 polygon_2d，顶面沿 U 轴提升 height）"""
#     vertices_bottom = np.hstack([polygon_2d, np.zeros((len(polygon_2d), 1))])
#     vertices_top = np.hstack([polygon_2d, np.full((len(polygon_2d), 1), height)])
#     vertices = np.vstack([vertices_bottom, vertices_top])
#
#     faces = []
#     n = len(polygon_2d)
#
#     # 底面三角剖分
#     for i in range(1, n - 1):
#         faces.append([0, i, i + 1])
#
#     # 顶面三角剖分
#     for i in range(1, n - 1):
#         faces.append([n, n + i, n + i + 1])
#
#     # 侧面四边形拆分为三角形
#     for i in range(n):
#         i_next = (i + 1) % n
#         i_top, i_next_top = i + n, i_next + n
#         faces.append([i, i_next, i_next_top])
#         faces.append([i, i_next_top, i_top])
#
#     return trimesh.Trimesh(vertices=vertices, faces=faces)
#
#
# def preprocess_buildings(buildings, ref_lon, ref_lat, ref_alt):
#     """预处理建筑物，将其转换为 ENU 坐标网格"""
#     #ref_lon, ref_lat, ref_alt = CoordinateTransform.convert_ecef_to_wgs(*ref_ecef)
#     # ref_lon, ref_lat, ref_alt = CoordinateTransform.convert_ecef_to_wgs(ref_ecef[0], ref_ecef[1], ref_ecef[2])
#
#
#     building_meshes = []
#     for building in buildings:
#         polygon_geo = building["polygon"]   #wgs84坐标下的多边形
#         height = building["height"]
#         #center_point = building["center"]
#         #center_point=[CoordinateTransform().convert_ecef_to_enu(center_point['X'], center_point['Y'], center_point['Z'], ref_lat, ref_lon, ref_alt)[:2] ]
#
#         # 将建筑底面转换为 ECEF 坐标
#         ecef_points = [CoordinateTransform().convert_wgs_to_ecef(lat, lon, 12) for lat, lon in polygon_geo.exterior.coords]
#
#         # 转换为 ENU 坐标（相对于 ground 点）
#         enu_2d = [CoordinateTransform().convert_ecef_to_enu(x, y, z, ref_lat, ref_lon, ref_alt)[:2] for x, y, z in ecef_points]
#
#         # 创建建筑 3D 网格
#         building_mesh = create_building_mesh(np.array(enu_2d), height)
#         building_mesh = create_building_mesh(np.array(ecef_points), height)
#         # building_meshes.append(building_mesh)
#
#         # building_info = {
#         #     "building_mesh": building_mesh,
#         #     "center_point": center_point
#         # }
#         building_meshes.append(building_mesh)
#
#     return building_meshes
#
#
# # ------------------  遮挡检测逻辑 ------------------
#
# def should_check_building(sat_ecef, ground_ecef, building_ecef):
#     """判断是否需要检查建筑遮挡"""
#     az_s = compute_azimuth(ground_ecef, sat_ecef)  # 计算卫星方位角
#     az_b = compute_azimuth(ground_ecef, building_ecef)  # 计算建筑中心点方位角
#
#     delta_az = abs(az_s - az_b) % 360  # 计算方位角夹角
#     if abs(delta_az - 180) < 15:  # 若夹角接近 180°（阈值可调整）
#         return False  # 说明卫星和地面点在建筑的同侧，无需检测
#     return True  # 需要进行遮挡检测
#
#
# def is_occluded(building_meshes, satellite_ecef, ground_ecef):
#     """检测卫星到地面的线段是否被任意建筑遮挡"""
#     ref_lon, ref_lat, ref_alt = CoordinateTransform().convert_ecef_to_wgs(*ground_ecef)
#
#     sat_e, sat_n, sat_u = CoordinateTransform().convert_ecef_to_enu(*satellite_ecef, ref_lat, ref_lon, ref_alt)
#     grd_e, grd_n, grd_u = CoordinateTransform().convert_ecef_to_enu(*ground_ecef, ref_lat, ref_lon, ref_alt)
#
#     start = np.array([sat_e, sat_n, sat_u])
#     end = np.array([grd_e, grd_n, grd_u])
#     direction = end - start
#     length = np.linalg.norm(direction)
#     if length < 1e-6:
#         return False  # 忽略重合点
#     direction /= length
#
#     for mesh in building_meshes:
#         locations, _, _ = mesh.ray.intersects_location(ray_origins=[start], ray_directions=[direction])
#         if len(locations) > 0:
#             t = np.dot(locations - start, direction) / length
#             if any((t >= 0) & (t <= 1)):
#                 return True  # 存在遮挡
#     return False

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

    def is_occluded(building_meshes, satellite_ecef, ground_ecef):
        """检测卫星到地面的线段是否被任意建筑遮挡"""
        ref_lon, ref_lat, ref_alt = CoordinateTransform().convert_ecef_to_wgs(*ground_ecef)

        sat_e, sat_n, sat_u = CoordinateTransform().convert_ecef_to_enu(*satellite_ecef, ref_lat, ref_lon, ref_alt)
        grd_e, grd_n, grd_u = CoordinateTransform().convert_ecef_to_enu(*ground_ecef, ref_lat, ref_lon, ref_alt)

        start = np.array([sat_e, sat_n, sat_u])
        end = np.array([grd_e, grd_n, grd_u])
        direction = end - start
        length = np.linalg.norm(direction)
        if length < 1e-6:
            return False  # 忽略重合点
        direction /= length

        for mesh in building_meshes:
            locations, _, _ = mesh.ray.intersects_location(ray_origins=[start], ray_directions=[direction])
            if len(locations) > 0:
                t = np.dot(locations - start, direction) / length
                if any((t >= 0) & (t <= 1)):
                    return True  # 存在遮挡
        return False

# def is_occluded_concatenate(buildings_meshes_ecef, sat_ecef, grid_ecef):
#     """
#     判断卫星到地面点的视线是否被建筑遮挡（ECEF坐标系）
#     :param sat_ecef: 卫星ECEF坐标 (x, y, z)
#     :param grid_ecef: 地面点ECEF坐标 (x, y, z)
#     :param buildings_meshes_ecef: 建筑的三维网格列表 [trimesh.Trimesh, ...]
#     :return: True（被遮挡） / False（未被遮挡）
#     """
#     ray_origin = np.array(sat_ecef)
#     ray_direction = np.array(grid_ecef) - ray_origin
#     ray_length = np.linalg.norm(ray_direction)
#     ray_direction_normalized = ray_direction / ray_length
#
#     # 合并所有建筑网格并构建加速结构
#     all_buildings = trimesh.util.concatenate(buildings_meshes_ecef)
#     intersector = trimesh.ray.ray_pyembree.RayMeshIntersector(all_buildings)
#
#     # 检测相交
#     locations, _, _ = intersector.intersects_location(
#         ray_origins=[ray_origin],
#         ray_directions=[ray_direction_normalized]
#     )
#     return any(np.linalg.norm(loc - ray_origin) < ray_length for loc in locations)


# ------------------  主程序 ------------------
#
# # 示例建筑数据
# buildings = [
#     {
#         "polygon": [(40.7128, -74.0060), (40.7128, -74.0055), (40.7123, -74.0055), (40.7123, -74.0060)],
#         "height": 50.0,
#         "center": geodetic_to_ecef(40.7126, -74.0058, 0)
#     }
# ]
#
# satellite_positions = [(x_sat, y_sat, z_sat) for _ in range(30)]  # 30 颗卫星
# ground_points = [(x_ground, y_ground, z_ground) for _ in range(3000)]  # 3000 个地面点
#
# occlusion_results = {}
#
# for ground_ecef in ground_points:
#     if ground_ecef not in occlusion_results:
#         occlusion_results[ground_ecef] = {}
#
#     building_meshes = preprocess_buildings(buildings, ground_ecef)
#
#     for sat_ecef in satellite_positions:
#         for building in buildings:
#             if not should_check_building(sat_ecef, ground_ecef, building["center"]):
#                 continue
#
#             occluded = is_occluded(building_meshes, sat_ecef, ground_ecef)
#             occlusion_results[ground_ecef][sat_ecef] = occluded
#
# print("遮挡计算完成！")

