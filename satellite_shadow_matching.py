import numpy as np
import logging
from utils.data_parser import DataParser
from utils.grid_generator import GridGenerator
#from utils.visibility_calculator import VisibilityCalculator
import utils.visibility_calculator as visibility_calculator
import simplekml
from pyproj import Proj, transform
from shapely.geometry import Polygon
from utils.coordinate_transform import CoordinateTransform


class SatelliteShadowMatching:
    def __init__(self, grid_spacing=2.0, search_radius=20.0, snr_threshold=35):
        """
        Initialize shadow matching system
        """
        self.data_parser = DataParser()
        self.grid_generator = GridGenerator(search_radius, grid_spacing)
        self.visibility_calculator = visibility_calculator.VisibilityCalculator(snr_threshold)
        self.transformer = CoordinateTransform()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_epoch(self, satellite_data, initial_position, buildings):
        """
        Process single epoch of data
        """
        self.logger.info(f"Processing epoch with {len(satellite_data)} satellites")

        ref_lat, ref_lon, ref_alt = initial_position['lat'], initial_position['lon'],initial_position['alt']
        ground_ecef = self.transformer.convert_wgs_to_ecef(ref_lat, ref_lon, ref_alt)

        # Generate search grid
        # grid_points = self.grid_generator.generate_search_grid(
        #     initial_position['X'],
        #     initial_position['Y'],
        #     initial_position['Z'],
        #     buildings
        # )

        # 初始点为参考点的enu坐标系下的建筑底面多边形
        buildings_polygon_enu = []
        for building in buildings:
            polygon = building["polygon"]
            ecef_points = [self.transformer.convert_wgs_to_ecef(lat, lon, 12) for lat, lon in polygon.exterior.coords]
            # 转换为 ENU 坐标（相对于 ground 点）
            enu_2d = [self.transformer.convert_ecef_to_enu(x, y, z, ref_lat, ref_lon, ref_alt)[:2] for x, y, z
                      in ecef_points]

            enu_2d = [(round(p[0], 6), round(p[1], 6)) for p in enu_2d]
            # print(f"首点: {enu_2d[0]}, 尾点: {enu_2d[-1]}")
            if enu_2d[0] != enu_2d[-1]:
                enu_2d.append(enu_2d[0])

            #polygon_enu = Polygon([(p[0], p[1]) for p in enu_2d])  # 确保是 (x, y) 坐标
            polygon_enu = Polygon(enu_2d)
            buildings_polygon_enu.append(polygon_enu)

        # 生成建筑三维网格，用于判断卫星遮挡
        #building_meshes = visibility_calculator.preprocess_buildings(buildings,ref_lat, ref_lon, ref_alt)  #enu坐标系下
        building_meshes = visibility_calculator.preprocess_buildings(buildings)     #ecef坐标系下

        #生成地面网格点
        #grid_points = self.grid_generator.generate_search_grid_enu(30, 2, buildings_polygon_enu)  #enu坐标系下
        grid_points = self.grid_generator.generate_search_grid_ecef(initial_position,30, 2, buildings_polygon_enu)    #ecef坐标系下
        self.logger.info(f"Generated {len(grid_points)} candidate points")

        # 计算每个网格点得分
        scores = []
        for point in grid_points:
            point_score = 0
            #候选点坐标
            # receiver_pos = {
            #     'X': point[0],
            #     'Y': point[1],
            #     'Z': point[2]  # Keep original height
            # }

            # Check each satellite
            for sat in satellite_data:
                # Predict visibility
                sat_ecef = sat['X'], sat['Y'], sat['Z']
                # predicted_visible = False
                # for building in buildings:
                #     center_point = np.array([building["center"].x, building["center"].y, building["center"].z])
                #     if not visibility_calculator.should_check_building(sat_ecef, ground_ecef, center_point):
                #         continue
                #
                #     if visibility_calculator.is_occluded(building_meshes, sat_ecef, ground_ecef):
                #         predicted_visible = True
                #         break

                predicted_visible=visibility_calculator.is_occluded_ecef(sat_ecef, point, building_meshes)

                # predicted_visible = self.visibility_calculator.predict_satellite_visibility(
                #     sat, receiver_pos, buildings
                # )

                # Check observed visibility
                observed_visible = self.visibility_calculator.check_observed_visibility( sat['SNR']  )

                # Score matching
                if predicted_visible == observed_visible:
                    point_score += 1

            scores.append((point_score, point))

        # Find best position
        if not scores:  # 如果 scores 为空
            self.logger.warning("No valid scores found for this epoch. Returning initial position.")
            x, y, z = self.transformer.convert_wgs_to_ecef(initial_position['lon'], initial_position['lat'], initial_position['alt'])
            return {
                # 'X': initial_position['X'],
                # 'Y': initial_position['Y'],
                # 'Z': initial_position['Z'],
                # 'score': 0,
                # 'num_best_points': 0
                # 'lat': initial_position['lat'],
                # 'lon': initial_position['lon'],
                # 'alt': initial_position['alt'],
                # 'score': 0,
                # 'num_best_points': 0
                'X': x,
                'Y': y,
                'Z': z,
                'score': 0,
                'num_best_points': 0
            }

        max_score = max(score for score, _ in scores)
        best_points = [point for score, point in scores if score == max_score]

        # Calculate final position (average of best points)
        final_x = np.mean([p[0] for p in best_points])
        final_y = np.mean([p[1] for p in best_points])
        final_z = np.mean([p[2] for p in best_points])

        return {
            'X': final_x,
            'Y': final_y,
            'Z': final_z,
            'score': max_score,
            'num_best_points': len(best_points)
        }

    def run(self, satellite_file, position_file, building_file, output_file):
        """
        Run shadow matching for all epochs
        """
        # Parse input data
        self.logger.info("Parsing input data...")
        satellite_data = self.data_parser.parse_satellite_data(satellite_file)
        position_data = self.data_parser.parse_position_data(position_file)
        buildings = self.data_parser.parse_building_data(building_file)

        # Process each epoch
        results = {}
        for epoch in satellite_data.keys():
            if epoch in position_data:
                self.logger.info(f"Processing epoch {epoch}")
                results[epoch] = self.process_epoch(
                    satellite_data[epoch],
                    position_data[epoch],
                    buildings
                )

            else:
                self.logger.warning(f"No position data for epoch {epoch}")
            # if i>10:
            #     break

        # Write results
        self.logger.info("Writing results...")
        with open(output_file, 'w') as f:
            f.write("Epoch,X,Y,Z,Score,NumBestPoints\n")
            for epoch, result in results.items():
                f.write(f"{epoch},{result['X']},{result['Y']},{result['Z']},"
                        f"{result['score']},{result['num_best_points']}\n")

        # 导出 kml 文件
        kml = simplekml.Kml()
        # proj_ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
        # proj_lla = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
        for epoch, result in results.items():
            lon, lat, alt = self.transformer.convert_ecef_to_wgs(result['X'], result['Y'], result['Z'])
            lon, lat, alt = self.transformer.convert_wgs_to_egm96(lon, lat, alt)
            # lon, lat, alt = transformer(result['X'], result['Y'], result['Z'], radians=False)
            #pnt = kml.newpoint(name=f"Epoch {epoch}")
            pnt = kml.newpoint()
            pnt.coords = [(lon, lat, alt)]  # KML 需要 (经度, 纬度, 高度)
            #pnt.altitudemode = simplekml.AltitudeMode.clamptoground  # 绝对高度
            # pnt.description = f"Score: {data['score']}\nBest Points: {data['num_best_points']}"
            pnt.style.labelstyle.scale = 1  # 文字大小
            pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"

        kml.save("output\\sm_pos.kml")

        self.logger.info("Processing complete")
        return results


if __name__ == "__main__":
    # Example usage
    matcher = SatelliteShadowMatching()
    sm_results = matcher.run(
        "files\\satpos1.txt",
        "files\\spp-kf1.pos",
        "files\\buildings.txt",
        "output\\shadow_matching_results.csv"
    )