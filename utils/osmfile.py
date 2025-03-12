#
# import osmium
# import shapely.geometry as geometry
# from random import uniform
#
# # 用于存储建筑物的多边形
# buildings = []
#
#
# class BuildingHandler(osmium.SimpleHandler):
#     def way(self, w):
#         if 'building' in w.tags:
#             # 提取建筑物的节点坐标
#             nodes = [(n.lon, n.lat) for n in w.nodes]
#             # 创建一个 Shapely 多边形
#             polygon = geometry.Polygon(nodes)
#             buildings.append(polygon)
#
#
# def read_osm_file(file_path):
#     handler = BuildingHandler()
#     handler.apply_file(file_path)
#
#
# def is_point_in_buildings(point, buildings):
#     for building in buildings:
#         if building.contains(point):
#             return True
#     return False
#
#
# def generate_point(min_lon, max_lon, min_lat, max_lat, buildings):
#     while True:
#         lon = uniform(min_lon, max_lon)
#         lat = uniform(min_lat, max_lat)
#         point = geometry.Point(lon, lat)
#         if not is_point_in_buildings(point, buildings):
#             return point
#
#
# # 读取 .osm 文件
# read_osm_file('path_to_your_osm_file.osm')
#
# # 定义生成点的范围
# min_lon, max_lon = 116.35, 116.38  # 示例经度范围
# min_lat, max_lat = 39.90, 39.92  # 示例纬度范围
#
# # 生成一个不在建筑物内的点
# point = generate_point(min_lon, max_lon, min_lat, max_lat, buildings)
# print(f"Generated Point: {point.x}, {point.y}")
#
