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
import random

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse



class SatelliteShadowMatching:
    def __init__(self, grid_spacing=2.0, search_radius=20.0, snr_threshold=33):
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



    # def plot_pca_analysis(self,scores, confidence_level=0.95):
    #     """
    #     绘制阴影匹配候选点的主成分分析可视化图
    #     参数：
    #     scores - 候选点列表，格式为 [(score, (E, N)), ...]
    #     confidence_level - 置信椭圆概率（默认95%）
    #     """
    #
    #     # 全局设置中文字体和负号
    #     plt.rcParams['font.sans-serif'] = ['SimHei']
    #     plt.rcParams['axes.unicode_minus'] = False
    #
    #     # 1. 数据提取与预处理
    #     points = np.array([[point[0], point[1]] for (score, point) in scores])
    #     scores_array = np.array([score for (score, point) in scores])
    #     weights = scores_array / np.sum(scores_array)  # 归一化权重
    #
    #     # 2. 计算加权均值和协方差
    #     mean = np.average(points, axis=0, weights=weights)
    #     cov = np.cov(points.T, aweights=weights)
    #
    #     # 3. 主成分分析（PCA）
    #     eig_vals, eig_vecs = np.linalg.eigh(cov)
    #     order = eig_vals.argsort()[::-1]  # 降序排列
    #     eig_vals, eig_vecs = eig_vals[order], eig_vecs[:, order]
    #
    #     # 4. 置信椭圆参数计算
    #     angle = np.degrees(np.arctan2(*eig_vecs[:, 0][::-1]))  # 主方向角度
    #     chi2_val = np.sqrt(-2 * np.log(1 - confidence_level))  # 卡方分布临界值
    #     width, height = 2 * chi2_val * np.sqrt(eig_vals)  # 椭圆轴长
    #
    #     # 5. 创建画布
    #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    #
    #     # ========== 原始坐标系图 ==========
    #     # 绘制候选点（颜色表示得分）
    #     sc = ax1.scatter(points[:, 0], points[:, 1],
    #                      c=scores_array, cmap='viridis', alpha=0.6,
    #                      label='候选点 (颜色=得分)')
    #
    #     # 绘制均值点
    #     ax1.scatter(mean[0], mean[1], s=100, c='red',
    #                 marker='x', label='加权均值')
    #
    #     # 绘制主成分方向箭头
    #     for i in range(len(eig_vals)):
    #         vec = eig_vecs[:, i] * np.sqrt(eig_vals[i]) * 3  # 缩放向量
    #         ax1.quiver(mean[0], mean[1], vec[0], vec[1],
    #                    color=['r', 'b'][i], width=0.01, scale=1,
    #                    label=f'PC{i + 1}方向 (λ={eig_vals[i]:.1f})')
    #
    #     # 绘制置信椭圆
    #     ellipse = Ellipse(xy=mean, width=width, height=height,
    #                       angle=angle, edgecolor='r',
    #                       fc='None', lw=2, label=f'{confidence_level * 100:.0f}% 置信椭圆')
    #     ax1.add_patch(ellipse)
    #
    #     ax1.set_title('原始坐标系下的主成分分析')
    #     ax1.set_xlabel('东向 (米)')
    #     ax1.set_ylabel('北向 (米)')
    #     ax1.grid(True)
    #     ax1.legend()
    #     plt.colorbar(sc, ax=ax1, label='候选点得分')
    #
    #     # ========== 主成分坐标系图 ==========
    #     # 坐标转换
    #     points_pc = (points - mean) @ eig_vecs
    #
    #     # 绘制转换后的点
    #     ax2.scatter(points_pc[:, 0], points_pc[:, 1],
    #                 c=scores_array, cmap='viridis', alpha=0.6)
    #
    #     # 绘制坐标轴
    #     ax2.axhline(0, color='black', lw=0.5)
    #     ax2.axvline(0, color='black', lw=0.5)
    #
    #     ax2.set_title('主成分坐标系下的分布')
    #     ax2.set_xlabel('PC1 (方差=%.1f $m^2$)' % eig_vals[0])
    #     ax2.set_ylabel('PC2 (方差=%.1f $m^2$)' % eig_vals[1])
    #     ax2.grid(True)
    #
    #     plt.tight_layout()
    #     plt.show()
    #     return fig, (ax1, ax2)


    def normalize_scores(self, scores):
        min_score = min(s for s, _ in scores)
        max_score = max(s for s, _ in scores)
        range_score = max_score - min_score if max_score != min_score else 1

        # 线性归一化后再平方增强视觉对比
        return [(((s - min_score) / range_score) ** 2, pt) for s, pt in scores]

    # def score_to_color(self, norm_score):
    #     # 红（高分） -> 蓝（低分）
    #     r = int(255 * norm_score)
    #     g = 0
    #     b = int(255 * (1 - norm_score))
    #     return simplekml.Color.rgb(r, g, b)

    def score_to_color(self, norm_score):
        # 只用蓝色通道，分高 -> 亮蓝，分低 -> 深蓝
        r = 0
        g = int(min(255, max(0, 255 * norm_score * 0.8)))  # 控制在 0~255
        b = int(min(255, max(0, 100 + norm_score * 155)))  # 蓝色主通道
        print(f"norm_score={norm_score:.2f}, RGB=({r},{g},{b})")

        return simplekml.Color.rgb(r, g, b)

    # def export_epochs_to_kml(self, all_epoch_scores, output_file="candidate_points.kml", selected_epochs=None):
    #     """
    #     导出若干历元中的候选点得分分布为 KML 文件，支持自动或指定选择历元。
    #     """
    #     if selected_epochs is None:
    #         selected_epochs = random.sample(range(len(all_epoch_scores)), 4)
    #
    #     kml = simplekml.Kml()
    #
    #     for epoch_idx in selected_epochs:
    #         epoch_scores = all_epoch_scores[epoch_idx]  # [(score, (x, y, z)), ...]
    #         norm_scores = self.normalize_scores(epoch_scores)  # [(normalized_score, (x, y, z)), ...]
    #
    #         folder = kml.newfolder(name=f"Epoch {epoch_idx}")
    #
    #         for (norm_score, (x, y, z)), (score, _) in zip(norm_scores, epoch_scores):
    #             color = self.score_to_color(norm_score)
    #             lon, lat, alt = self.transformer.convert_ecef_to_wgs(x, y, z)
    #
    #             pnt = folder.newpoint(coords=[(lon, lat, alt)])
    #             pnt.style.iconstyle.color = color
    #             pnt.description = f"Score: {score}"
    #
    #     kml.save(output_file)

    def export_epochs_to_kml(self, all_epoch_scores, output_file="candidate_points.kml", selected_epochs=None):
        import random
        if selected_epochs is None:
            selected_epochs = random.sample(range(len(all_epoch_scores)), 4)

        kml = simplekml.Kml()

        for epoch_idx in selected_epochs:
            if epoch_idx >= len(all_epoch_scores):
                print(f"Warning: Epoch index {epoch_idx} is out of range.")
                continue

            epoch_scores = all_epoch_scores[epoch_idx]
            norm_scores = self.normalize_scores(epoch_scores)

            folder = kml.newfolder(name=f"Epoch {epoch_idx}")

            for norm_score, (score, (x, y, z)) in zip(norm_scores, epoch_scores):
                #color = self.score_to_color(norm_score)
                color = self.score_to_color(norm_score[0])

                # 坐标转换 ECEF -> WGS84
                lon, lat, alt = self.transformer.convert_ecef_to_wgs(x, y, z)

                pnt = folder.newpoint(coords=[(lon, lat, alt)])
                pnt.style.iconstyle.color = color
                pnt.style.iconstyle.scale = 1.2  # 放大图标
                pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
                pnt.description = f"Score: {score}"

        kml.save(output_file)
        print(f"KML file saved to: {output_file}")

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
        #grid_points = self.grid_generator.generate_search_grid_enu(30, 2, buildings_polygon_enu)  #enu坐标系下
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

                # 对网格点进行匹配打分
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
                'score_all': [],
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
            'score_all':scores,
            'num_best_points': len(best_points)
        }

    def run(self, satellite_file, position_file, building_file, output_file):
        """
        Run shadow matching for all epochs
        """
        # Parse input data
        self.logger.info("Parsing input data...")
        self.all_epoch_scores = []  # 在初始化中准备一个空列表
        satellite_data = self.data_parser.parse_satellite_data(satellite_file)
        position_data = self.data_parser.parse_position_data(position_file)
        #position_data = self.data_parser.parse_position_csv(position_file)
        buildings = self.data_parser.parse_building_data_new(building_file)

        model = joblib.load('..\\los_classifier_rf.pkl')

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
                self.all_epoch_scores.append(results[epoch]['score_all'])
                if results[epoch]['num_best_points'] != len(results[epoch]['score_all']):
                    print(epoch)

            else:
                self.logger.warning(f"No position data for epoch {epoch}")
            # if i>10:
            #     break

        self.export_epochs_to_kml(self.all_epoch_scores,output_file="F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\sm+snrweight\\scores_epochs(snrweight)_yanshou.kml", selected_epochs=[57])
        # self.plot_pca_analysis(self.all_epoch_scores[57])

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

        #kml.save("F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\sm+snrweight\\shadow_matching(P1)(for_scores_distribution).kml")
        self.logger.info("Processing complete")
        return results


if __name__ == "__main__":
    # Example usage
    matcher = SatelliteShadowMatching()
    sm_results = matcher.run(
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\satpos_new(P1).txt",
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\spp(P1).pos",
        # "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\spp(P3)_smoothed.csv",
        "..\\files\\buildings.txt",
        "F:\\GNSSdata\Android GNSS data\\2025-04-15\\ALL\\sm+snrweight\\shadow_matching(P1)(for_scores_distribution).csv"
    )