import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import logging
import os
from pyproj import Proj, Transformer



def calculate_errors(df, true_lat, true_lon):
    """通过UTM坐标计算东向误差、北向误差和平面误差"""
    # 创建UTM投影转换器，基于参考点所在的经纬度自动选择合适的 UTM 区
    transformer = Transformer.from_crs("epsg:4326", "epsg:32651" , always_xy=True)

    # 参考点 UTM 坐标
    true_east, true_north = transformer.transform(true_lon, true_lat)

    # 数据点 UTM 坐标
    east_list, north_list = transformer.transform(df['Longitude'].values, df['Latitude'].values)

    # 误差计算
    east_error = np.array(east_list) - true_east
    north_error = np.array(north_list) - true_north
    plane_error = np.sqrt(east_error**2 + north_error**2)

    return east_error, north_error, plane_error

def read_pos_file(filename):
    """读取POS文件"""
    timestamps = []
    latitudes = []
    longitudes = []
    heights = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('%'):
                continue

            data = line.split()
            if len(data) >= 15:
                try:
                    timestamp = f"{data[0]} {data[1]}"
                    lat = float(data[2])  # 纬度(度)
                    lon = float(data[3])  # 经度(度)
                    height = float(data[4])  # 高度(米)

                    timestamps.append(timestamp)
                    latitudes.append(lat)
                    longitudes.append(lon)
                    heights.append(height)
                except (ValueError, IndexError) as e:
                    continue

    return pd.DataFrame({
        'Timestamp': pd.to_datetime(timestamps),
        'Latitude': latitudes,
        'Longitude': longitudes,
        'Height': heights
    })


def plot_subplots_plane_errors(file_groups, save_path=None):
    """绘制5个子图，每个子图显示一组数据的平面误差"""
    fig, axes = plt.subplots(3, 1, figsize=(22, 20))
    date_format = DateFormatter("%H:%M:%S")

    # 设置中文字体为黑体（SimHei），确保支持中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决负号显示问题（若有负号相关绘图需求）
    plt.rcParams['axes.unicode_minus'] = False

    # 调整子图布局，去掉最后一个多余的子图
    # axes[-1, -1].axis('off')

    # 将二维的axes数组展平
    axes = axes.flatten()[:3]

    for i, (ax, (pos_file, csv_file, true_lat, true_lon)) in enumerate(zip(axes, file_groups)):
        try:
            # 读取数据
            csv_df = pd.read_csv(csv_file)
            csv_df['Timestamp'] = pd.to_datetime(csv_df['Timestamp'])
            pos_df = read_pos_file(pos_file)

            # 计算误差
            csv_east,csv_north, csv_plane = calculate_errors(csv_df, true_lat, true_lon)
            _, _, pos_plane = calculate_errors(pos_df, true_lat, true_lon)

            csv_east_min = np.min(csv_east)
            csv_east_max = np.max(csv_east)
            csv_east_mean = np.mean(csv_east)
            csv_east_rmse =np.sqrt(np.mean(np.square(csv_east)))

            csv_north_min = np.min(csv_north)
            csv_north_max = np.max(csv_north)
            csv_north_mean = np.mean(csv_north)
            csv_east_rmse = np.sqrt(np.mean(np.square(csv_north)))

            csv_plane_min = np.min(csv_plane)
            csv_plane_max = np.max(csv_plane)
            csv_plane_mean = np.mean(csv_plane)
            csv_plane_rmse = np.sqrt(np.mean(np.square(csv_plane)))


            print(csv_east_min, csv_east_max, csv_east_mean,csv_east_rmse,csv_north_min, csv_north_max,csv_north_mean,csv_east_rmse,csv_plane_min, csv_plane_max,csv_plane_mean,csv_plane_rmse)


            # # 获取数据集名称
            # base_name = os.path.splitext(os.path.basename(pos_file))[0].replace('.pos', '')

            # 绘制曲线
            ax.plot(csv_df['Timestamp'], csv_plane,
                    label='Z-score', color='blue', linestyle='-', linewidth=2)
            ax.plot(pos_df['Timestamp'], pos_plane,
                    label='未处理', color='red', linestyle='--', linewidth=2)

            # 设置子图属性
            ax.xaxis.set_major_formatter(date_format)
            ax.set_ylabel('Horizont Error (m)', fontsize=24)
            # ax.set_title(base_name,fontsize=24)
            ax.set_title(f'P{i+1}', fontsize=24)
            for tick in ax.get_xticklabels():
                tick.set_fontsize(24)  # 可
            for tick in ax.get_yticklabels():
                tick.set_fontsize(24)  # 可
            ax.legend(fontsize=22)
            ax.grid(True, linestyle='--', alpha=0.6)

        except Exception as e:
            print(f"Error processing files {pos_file} and {csv_file}: {e}")
            ax.set_title(f'Error loading dataset {i + 1}')
            continue

    plt.xlabel('Time', fontsize=12)
    plt.tight_layout(pad=3.0)  # 增加子图间距

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.show()

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 文件组列表 (POS文件, CSV文件, 真实纬度, 真实经度)
    file_groups = [
        ('F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P1).pos',
         'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\Zscore\\spp(P1)_zscore.csv', 31.496194 , 120.269652),  # 第1组数据和真实值
        ('F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P2).pos',
         'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\Zscore\\spp(P2)_zscore.csv', 31.496033 , 120.269650),  # 第2组数据和真实值
        ('F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(P3).pos',
         'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\Zscore\\spp(P3)_zscore.csv', 31.495794 , 120.269597),  # 第3组数据和真实值
    ]

    plot_subplots_plane_errors(file_groups, save_path='plane_errors_subplots.png')
