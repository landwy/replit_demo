import shapely.geometry as geometry
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon, Point, LineString
#from scipy.spatial.transform import Rotation as R
from .coordinate_transform import CoordinateTransform


class GridGenerator:
    def __init__(self, search_radius, grid_spacing):
        self.search_radius = search_radius
        self.grid_spacing = grid_spacing


    def generate_search_grid(self, center_x, center_y, center_z, buildings):
        """
        生成搜索网格，排除建筑物内部的点。
        center_x, center_y, center_z 是 ECEF 坐标，需要转换。
        """


        # 计算网格维度
        num_points = int(2 * self.search_radius / self.grid_spacing) + 1

        # 生成网格坐标
        x_coords = np.linspace(center_x - self.search_radius, center_x + self.search_radius, num_points)
        y_coords = np.linspace(center_y - self.search_radius, center_y + self.search_radius, num_points)

        # 创建网格点
        grid_points = []
        for x in x_coords:
            for y in y_coords:
                # 只包含搜索半径内的点
                if np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) <= self.search_radius:
                    #point = geometry.Point(x, y)
                    # 检查点是否在建筑物内
                    # if not any(building["polygon"].contains(Point(x, y)) for building in buildings):
                    if not any(Point(x, y).buffer(1e-2).within(building["polygon"]) for building in buildings):
                        grid_points.append((x, y, center_z ))
        return grid_points


    @staticmethod
    def generate_search_grid_ecef(initial_position, radius, grid_spacing, buildings):
        """
            生成以中心点为原点、排除建筑区域的圆形网格点
            :param initial_position: 初始点，字典类型
            :param radius: 搜索半径（米）
            :param grid_spacing: 网格间距（米）
            :param buildings: 建筑列表，每个元素包含ENU坐标系下的多边形顶点
                             示例结构：[{"polygon": [[e1,n1], [e2,n2], ...]}, ...]
            :return: 安全点坐标数组，形状为(N, 2)的numpy数组
            """
        # ----------------------------------
        # 步骤1：生成候选网格点
        # ----------------------------------
        # 生成东西和南北方向的坐标序列（ENU坐标系）
        e_coords = np.arange(-radius, radius + grid_spacing / 2, grid_spacing)
        n_coords = np.arange(-radius, radius + grid_spacing / 2, grid_spacing)

        # 创建网格点矩阵并展平
        e_grid, n_grid = np.meshgrid(e_coords, n_coords)
        points = np.column_stack([e_grid.ravel(), n_grid.ravel()])

        # 筛选圆形范围内的点
        distances = np.linalg.norm(points, axis=1)
        candidate_points = points[distances <= radius]

        # ----------------------------------
        # 步骤3：过滤建筑区域内的点
        # ----------------------------------
        safe_points = []
        for pt in candidate_points:
            # in_building = False
            # point=Point(pt)
            # # 遍历所有建筑
            # for building in buildings:
            #     polygon = np.array(building["polygon"])
            #     # 检查点是否在当前建筑内
            #     if is_inside_polygon(pt, polygon):
            #         in_building = True
            #         break
            # # 仅保留不在任何建筑内的点
            # if not in_building:
            #     safe_points.append(pt)
            if not any(Point(pt[0], pt[1]).buffer(1e-2).within(building) for building in buildings):
                safe_points.append((pt[0], pt[1], 0))

        grid_points_ecef = np.array([CoordinateTransform().convert_enu_to_ecef(pt[0], pt[1], pt[2],
                                                                                initial_position['lat'],
                                                                                initial_position['lon'],
                                                                                initial_position['alt']) for pt in safe_points])
        # return np.array(safe_points)
        return grid_points_ecef

    @staticmethod
    def generate_search_grid_enu(radius, grid_spacing, buildings):
        """
            生成以中心点为原点、排除建筑区域的圆形网格点
            :param radius: 搜索半径（米）
            :param grid_spacing: 网格间距（米）
            :param buildings: 建筑列表，每个元素包含ENU坐标系下的多边形顶点
                             示例结构：[{"polygon": [[e1,n1], [e2,n2], ...]}, ...]
            :return: 安全点坐标数组，形状为(N, 2)的numpy数组
            """
        # ----------------------------------
        # 步骤1：生成候选网格点
        # ----------------------------------
        # 生成东西和南北方向的坐标序列（ENU坐标系）
        e_coords = np.arange(-radius, radius + grid_spacing / 2, grid_spacing)
        n_coords = np.arange(-radius, radius + grid_spacing / 2, grid_spacing)

        # 创建网格点矩阵并展平
        e_grid, n_grid = np.meshgrid(e_coords, n_coords)
        points = np.column_stack([e_grid.ravel(), n_grid.ravel()])

        # 筛选圆形范围内的点
        distances = np.linalg.norm(points, axis=1)
        candidate_points = points[distances <= radius]

        # ----------------------------------
        # 步骤2：射线法判断点是否在多边形内
        # ----------------------------------
        def is_inside_polygon(point, polygon):
            """射线法判断点是否在二维多边形内部"""
            x, y = point
            inside = False
            n = len(polygon)

            for i in range(n):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % n]

                # 检查y坐标是否在边的范围内
                y_min = min(p1[1], p2[1])
                y_max = max(p1[1], p2[1])
                if y < y_min or y > y_max:
                    continue

                # 计算交点x坐标（处理垂直边）
                if p2[1] != p1[1]:
                    x_intersect = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                else:
                    x_intersect = p1[0]  # 垂直边特殊处理

                # 判断射线穿越次数
                if x <= x_intersect:
                    inside = not inside

            return inside

        # ----------------------------------
        # 步骤3：过滤建筑区域内的点
        # ----------------------------------
        safe_points = []
        for pt in candidate_points:
            # in_building = False
            # point=Point(pt)
            # # 遍历所有建筑
            # for building in buildings:
            #     polygon = np.array(building["polygon"])
            #     # 检查点是否在当前建筑内
            #     if is_inside_polygon(pt, polygon):
            #         in_building = True
            #         break
            # # 仅保留不在任何建筑内的点
            # if not in_building:
            #     safe_points.append(pt)
            if not any(Point(pt[0], pt[1]).buffer(1e-2).within(building) for building in buildings):
                safe_points.append((pt[0], pt[1], 0))

        return np.array(safe_points)


