# from pyproj import Proj, transform
# import simplekml
#
# # 定义 ECEF 和 WGS84 投影
# proj_ecef = Proj(proj="geocent", datum="WGS84")
# proj_geodetic = Proj(proj="latlong", datum="WGS84")
#
# # 示例建筑物数据（ECEF 坐标）
# buildings = [
#     {
#         'corner1_X': 1332556.57, 'corner1_Y': -4656581.77, 'corner1_Z': 4133285.89,
#         'corner2_X': 1332600.00, 'corner2_Y': -4656581.77, 'corner2_Z': 4133285.89,
#         'corner3_X': 1332600.00, 'corner3_Y': -4656620.00, 'corner3_Z': 4133285.89,
#         'corner4_X': 1332556.57, 'corner4_Y': -4656620.00, 'corner4_Z': 4133285.89,
#         'height': 50  # 建筑高度（米）
#     }
# ]
#
# # 创建 KML
# kml = simplekml.Kml()
#
# for building in buildings:
#     # 转换四个角点的 ECEF 坐标为 WGS84
#     lon1, lat1, alt1 = transform(proj_ecef, proj_geodetic,
#                                  building['corner1_X'], building['corner1_Y'], building['corner1_Z'], radians=False)
#     lon2, lat2, alt2 = transform(proj_ecef, proj_geodetic,
#                                  building['corner2_X'], building['corner2_Y'], building['corner2_Z'], radians=False)
#     lon3, lat3, alt3 = transform(proj_ecef, proj_geodetic,
#                                  building['corner3_X'], building['corner3_Y'], building['corner3_Z'], radians=False)
#     lon4, lat4, alt4 = transform(proj_ecef, proj_geodetic,
#                                  building['corner4_X'], building['corner4_Y'], building['corner4_Z'], radians=False)
#
#     # **地面四个角点**
#     ground_coords = [(lon1, lat1, 0), (lon2, lat2, 0), (lon3, lat3, 0), (lon4, lat4, 0), (lon1, lat1, 0)]
#
#     # **建筑顶部四个角点**
#     top_coords = [(lon1, lat1, building['height']), (lon2, lat2, building['height']),
#                   (lon3, lat3, building['height']), (lon4, lat4, building['height']), (lon1, lat1, building['height'])]
#
#     # **创建地面多边形**
#     ground_poly = kml.newpolygon(name="Building Base")
#     ground_poly.outerboundaryis = ground_coords
#     ground_poly.altitudemode = simplekml.AltitudeMode.relativetoground
#     ground_poly.style.polystyle.color = simplekml.Color.changealpha("80", simplekml.Color.blue)
#
#     # **创建顶部多边形**
#     top_poly = kml.newpolygon(name="Building Top")
#     top_poly.outerboundaryis = top_coords
#     top_poly.altitudemode = simplekml.AltitudeMode.relativetoground
#     top_poly.style.polystyle.color = simplekml.Color.changealpha("80", simplekml.Color.red)
#
#     # **创建墙体**
#     for i in range(4):
#         wall = kml.newpolygon(name=f"Building Wall {i+1}")
#         wall.outerboundaryis = [ground_coords[i], ground_coords[i+1],
#                                 top_coords[i+1], top_coords[i], ground_coords[i]]
#         wall.altitudemode = simplekml.AltitudeMode.relativetoground
#         wall.style.polystyle.color = simplekml.Color.changealpha("80", simplekml.Color.green)
#
# # 保存 KML 文件
# kml.save("complex_buildings.kml")
#
# print("KML 文件已生成：complex_buildings.kml")
