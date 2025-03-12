# from pyproj import Transformer
# import numpy as np
# import trimesh
#
# # 坐标转换工具初始化
# transformer_to_ecef = Transformer.from_crs(4326, 4978)  # WGS84经纬度转ECEF
# transformer_to_lla = Transformer.from_crs(4978, 4326)  # ECEF转WGS84经纬度
#
# def geodetic_to_ecef(lat, lon, alt):
#     """经纬度转ECEF坐标"""
#     return transformer_to_ecef.transform(lon, lat, alt)
#
# def ecef_to_enu(x, y, z, lat0, lon0, alt0):
#     """ECEF坐标转ENU坐标（局部坐标系）"""
#     # 将参考点转换为ECEF
#     x0, y0, z0 = transformer_to_ecef.transform(lon0, lat0, alt0)
#     dx, dy, dz = x - x0, y - y0, z - z0
#     # 转换为弧度
#     lat0_rad = np.radians(lat0)
#     lon0_rad = np.radians(lon0)
#     # 旋转矩阵元素
#     slon = np.sin(lon0_rad)
#     clon = np.cos(lon0_rad)
#     slat = np.sin(lat0_rad)
#     clat = np.cos(lat0_rad)
#     # 计算ENU坐标
#     e = -slon * dx + clon * dy
#     n = -slat * clon * dx - slat * slon * dy + clat * dz
#     u = clat * clon * dx + clat * slon * dy + slat * dz
#     return e, n, u
#
# def create_building_mesh(polygon, height):
#     """生成建筑三维网格（ENU坐标系下）"""
#     vertices_2d = np.array(polygon)     #将 polygon 转换为 numpy 数组
#     vertices_bottom = np.hstack([vertices_2d, np.zeros((len(vertices_2d), 1))])  # 水平方向拼接数组
#     vertices_top = np.hstack([vertices_2d, np.full((len(vertices_2d), 1), height)])
#     vertices = np.vstack([vertices_bottom, vertices_top])  # 垂直方向拼接数组
#
#     faces = []
#     n = len(vertices_2d)
#
#     # 底面三角剖分（假设凸多边形）
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
#         i_top = i + n
#         i_next_top = i_next + n
#         faces.append([i, i_next, i_next_top])
#         faces.append([i, i_next_top, i_top])
#
#     return trimesh.Trimesh(vertices=vertices, faces=faces)
#
# def does_intersect_trimesh(polygon, height, satellite_enu, ground_point_enu):
#     """检测线段是否与建筑网格相交"""
#     building_mesh = create_building_mesh(polygon, height)
#     start = np.array(satellite_enu)
#     end = np.array(ground_point_enu)
#     direction = end - start
#     length = np.linalg.norm(direction)
#     if length == 0:
#         return False
#     direction_normalized = direction / length
#
#     # 检测射线相交
#     locations, _, _ = building_mesh.ray.intersects_location(
#         ray_origins=[start],
#         ray_directions=[direction_normalized]
#     )
#
#     if len(locations) > 0:
#         t_values = np.dot(locations - start, direction) / (length**2)
#         return any((t >= 0) & (t <= 1) for t in t_values)
#     return False
#
# # 示例使用流程
# # 输入数据：建筑角点经纬度，建筑高度，卫星和地面点ECEF坐标
# building_lat_lon = [(40.7128, -74.0060), (40.7128, -74.0050), ...]  # 建筑角点经纬度列表
# building_height = 50  # 建筑高度（米）
# satellite_ecef = (x_sat, y_sat, z_sat)  # 卫星ECEF坐标
# ground_point_ecef = (x_ground, y_ground, z_ground)  # 地面点ECEF坐标
#
# # 转换建筑角点到ECEF
# ecef_coords = [geodetic_to_ecef(lat, lon, 0) for lat, lon in building_lat_lon]
#
# # 计算ENU原点（建筑底面中心）
# x0 = np.mean([c[0] for c in ecef_coords])
# y0 = np.mean([c[1] for c in ecef_coords])
# z0 = np.mean([c[2] for c in ecef_coords])
# lat0, lon0, alt0 = transformer_to_lla.transform(x0, y0, z0)
#
# # 转换到ENU坐标系
# building_enu = [ecef_to_enu(x, y, z, lat0, lon0, alt0)[:2] for x, y, z in ecef_coords]  # 仅取E,N
# satellite_enu = ecef_to_enu(*satellite_ecef, lat0, lon0, alt0)
# ground_enu = ecef_to_enu(*ground_point_ecef, lat0, lon0, alt0)
#
# # 检测遮挡
# intersects = does_intersect_trimesh(building_enu, building_height, satellite_enu, ground_enu)
# print(f"信号被遮挡: {intersects}")