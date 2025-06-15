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
import joblib
import pandas as pd

#卫星坐标：ecef
#单点定位坐标：wgs84，中间会转换
#网格点：ecef
#建筑：wgs84

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

    def process_epoch(self, satellite_data, initial_position, buildings,building_triangles, model):
        """
        Process single epoch of data
        """
        self.logger.info(f"Processing epoch with {len(satellite_data)} satellites")

        ref_lat, ref_lon, ref_alt = initial_position['lat'], initial_position['lon'],initial_position['alt']
        ground_ecef = self.transformer.convert_wgs_to_ecef(ref_lat, ref_lon, ref_alt)

        # 初始点为参考点的enu坐标系下的建筑底面多边形（用于排除建筑内的点）
        buildings_polygon_enu = []
        for building in buildings:
            polygon = building["polygon"]
            #将建筑底面点的坐标转换为ECEF坐标
            ecef_points = [self.transformer.convert_wgs_to_ecef(lat, lon, 0) for lat, lon in polygon.exterior.coords]
            # 将建筑底面点的坐标转换为 ENU 坐标（相对于 ground 点）
            enu_2d = [self.transformer.convert_ecef_to_enu(x, y, z, ref_lon, ref_lat, ref_alt)[:2] for x, y, z
                      in ecef_points]
            # 舍去天向坐标，仅保留东向和北向坐标，便于构成平面多边形
            enu_2d = [(round(p[0], 6), round(p[1], 6)) for p in enu_2d]
            if enu_2d[0] != enu_2d[-1]:
                enu_2d.append(enu_2d[0])   #首尾点相同，确保点能形成闭合多边形

            polygon_enu = Polygon(enu_2d)   #构建ENU坐标系下建筑底面多边形
            buildings_polygon_enu.append(polygon_enu)


        #生成地面网格点
        grid_points = self.grid_generator.generate_search_grid_ecef(initial_position,20, 2, buildings_polygon_enu)    #ecef坐标系下
        self.logger.info(f"Generated {len(grid_points)} candidate points")

        # 计算每个网格点得分
        scores = []
        for point in grid_points:
            point_score = 0
            #
            # # 找到 SNR 最大的项
            max_snr_sat = max(satellite_data, key=lambda x: x['SNR'])
            max_snr = max_snr_sat['SNR']
            #
            # # 找到 SNR 最小的项
            min_snr_sat = min(satellite_data, key=lambda x: x['SNR'])
            min_snr = min_snr_sat['SNR']

            # Check each satellite
            for sat in satellite_data:
                # Predict visibility
                sat_ecef = sat['X'], sat['Y'], sat['Z']

                predicted_visible=visibility_calculator.is_line_blocked(sat_ecef, point, building_triangles)

                #observed_visible = self.visibility_calculator.check_observed_visibility( sat['SNR']  )

                X = pd.DataFrame([{
                    'el': sat['elevation'],
                    'snr': sat['SNR'],
                    'norm_resp': sat['resp']
                }])
                X = X.astype(float)
                observed_visible = model.predict(X)          #'elevation', 'snr',  'normalized_resp'


                # # 对网格点进行匹配打分
                # if predicted_visible == observed_visible:
                #     point_score += 1

                if predicted_visible == observed_visible:
                     if sat['SNR'] == max_snr or sat['SNR'] == min_snr:
                         point_score += 2
                     else:
                         point_score += 1

            scores.append((point_score, point))

        # Find best position
        if not scores:  # 如果 scores 为空
            self.logger.warning("No valid scores found for this epoch. Returning initial position.")
            x, y, z = self.transformer.convert_wgs_to_ecef(initial_position['lon'], initial_position['lat'], initial_position['alt'])
            return {
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

        # top_n = max(1, int(len(scores) * 0.8))
        # top_scores = scores[:top_n]
        #
        # total_weight = sum(score for score, _ in top_scores)
        # if total_weight == 0:
        #     avg_x = sum(point[0] for _, point in top_scores) / top_n
        #     avg_y = sum(point[1] for _, point in top_scores) / top_n
        #     avg_z = sum(point[2] for _, point in top_scores) / top_n
        # else:
        #     avg_x = sum(score * point[0] for score, point in top_scores) / total_weight
        #     avg_y = sum(score * point[1] for score, point in top_scores) / total_weight
        #     avg_z = sum(score * point[2] for score, point in top_scores) / total_weight
        #
        # return {
        #     'X': avg_x,
        #     'Y': avg_y,
        #     'Z': avg_z,
        #     'score': sum(score for score, _ in top_scores) / top_n,
        #     'num_best_points': top_n
        # }

    def run(self, satellite_file, position_file, building_file, output_file):
        """
        Run shadow matching for all epochs
        """
        # Parse input data
        self.logger.info("Parsing input data...")
        satellite_data = self.data_parser.parse_satellite_data(satellite_file)
        position_data = self.data_parser.parse_position_data(position_file)
        #position_data = self.data_parser.parse_position_csv(position_file)
        buildings = self.data_parser.parse_building_data_new(building_file)

        model = joblib.load('los_classifier_rf.pkl')

        building_triangles = visibility_calculator.preprocess_building_sides(buildings)  # ecef坐标系下

        # Process each epoch
        results = {}
        for epoch in satellite_data.keys():
            if epoch in position_data:
                self.logger.info(f"Processing epoch {epoch}")
                results[epoch] = self.process_epoch(
                    satellite_data[epoch],
                    position_data[epoch],
                    buildings,
                    building_triangles,
                    model
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
            #pnt = kml.newpoint(name=f"Epoch {epoch}")
            pnt = kml.newpoint()
            pnt.coords = [(lon, lat, alt)]  # KML 需要 (经度, 纬度, 高度)
            pnt.altitudemode = simplekml.AltitudeMode.clamptoground  # 高度模式
            # pnt.description = f"Score: {data['score']}\nBest Points: {data['num_best_points']}"
            pnt.style.labelstyle.scale = 1  # 文字大小
            pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
            #pnt.style.iconstyle.icon.href = "icons/green16.png"

        kml.save("F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\sm+xgboost_snrweight\\sm+snrweight(P1).kml")

        self.logger.info("Processing complete")
        return results


if __name__ == "__main__":
    # Example usage
    matcher = SatelliteShadowMatching()
    sm_results = matcher.run(
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\satpos_new(P1).txt",
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\spp(P1).pos",
        # "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\spp(P3)_smoothed.csv",
        "files\\buildings.txt",
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\sm+xgboost_snrweight\\sm+snrweight(P1).csv"
    )