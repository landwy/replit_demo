import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.strtree import STRtree
from .coordinate_transform import CoordinateTransform


class GridGenerator:
    def __init__(self, search_radius, grid_spacing):
        self.search_radius = search_radius
        self.grid_spacing = grid_spacing

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
        # 步骤1：生成候选网格点（ENU）
        # ----------------------------------
        e_coords, n_coords = np.meshgrid(
            np.linspace(-radius, radius, int(2 * radius / grid_spacing) + 1),
            np.linspace(-radius, radius, int(2 * radius / grid_spacing) + 1)
        )
        points = np.c_[e_coords.ravel(), n_coords.ravel()]

        # 筛选圆形范围内的点
        distances = np.linalg.norm(points, axis=1)
        candidate_points = points[distances <= radius]

        # ----------------------------------
        # 步骤3：过滤建筑区域内的点
        # ----------------------------------
        tree = STRtree(buildings)  # 构建空间索引

        safe_points = candidate_points[
            ~np.array([any(tree.query(Point(pt))) for pt in candidate_points])
        ]  # 只保留不在建筑内的点

        # lat, lon, alt = initial_position["lat"], initial_position["lon"], initial_position["alt"]
        safe_points_3d = np.column_stack((safe_points, np.zeros(len(safe_points))))  # 添加高度维度

        transformer = CoordinateTransform()
        grid_points_ecef = np.array([transformer.convert_enu_to_ecef(pt[0], pt[1], pt[2],
                                                                                initial_position['lon'],
                                                                                initial_position['lat'],
                                                                                initial_position['alt']) for pt in safe_points_3d])
        # return np.array(safe_points)
        return grid_points_ecef



    @staticmethod
    def generate_search_grid_enu( radius, grid_spacing, buildings):

        # ----------------------------------
        # 步骤1：生成候选网格点（ENU）
        # ----------------------------------
        e_coords, n_coords = np.meshgrid(
            np.linspace(-radius, radius, int(2 * radius / grid_spacing) + 1),
            np.linspace(-radius, radius, int(2 * radius / grid_spacing) + 1)
        )
        points = np.c_[e_coords.ravel(), n_coords.ravel()]

        # 筛选圆形范围内的点
        distances = np.linalg.norm(points, axis=1)
        candidate_points = points[distances <= radius]

        # ----------------------------------
        # 步骤3：过滤建筑区域内的点
        # ----------------------------------
        tree = STRtree(buildings)  # 构建空间索引

        safe_points = candidate_points[
            ~np.array([any(tree.query(Point(pt))) for pt in candidate_points])
        ]  # 只保留不在建筑内的点

        safe_points_3d = np.column_stack((safe_points, np.zeros(len(safe_points))))  # 添加高度维度


        return safe_points_3d





