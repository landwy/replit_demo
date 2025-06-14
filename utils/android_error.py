#---------------------------------------------------------------------------分析手机定位误差并保存文件----------------------------------------------
import numpy as np
import csv
import os
from datetime import datetime
from pyproj import Transformer


def calculate_android_errors(pos_file, true_lon, true_lat, output_csv="results.csv"):
    """
    解析.pos文件并计算结果，将统计量追加到CSV文件

    参数：
        pos_file (str): .pos文件路径
        true_lon (float): 真实经度
        true_lat (float): 真实纬度
        output_csv (str): 输出CSV文件路径
    """

    # 自动确定UTM分区
    def get_utm_epsg(lon, lat):
        zone = int((lon + 180) // 6 + 1)
        return 32600 + zone if lat >= 0 else 32700 + zone

    utm_epsg = get_utm_epsg(true_lon, true_lat)
    transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{utm_epsg}")

    # 转换真实坐标到UTM
    true_easting, true_northing = transformer.transform(true_lat, true_lon)

    # 读取数据
    east_errors, north_errors, plane_errors = [], [], []

    with open(pos_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            try:
                lat = float(parts[2])
                lon = float(parts[3])
            except (IndexError, ValueError):
                continue

            # 坐标转换
            current_easting, current_northing = transformer.transform(lat, lon)

            # 计算误差
            e_error = current_easting - true_easting
            n_error = current_northing - true_northing
            p_error = np.sqrt(e_error ** 2 + n_error ** 2)

            east_errors.append(abs(e_error))
            north_errors.append(abs(n_error))
            plane_errors.append(abs(p_error))

    # 计算统计指标
    stats = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "East Min": np.min(east_errors) if east_errors else np.nan,
        "East Max": np.max(east_errors) if east_errors else np.nan,
        "East Mean": np.mean(east_errors) if east_errors else np.nan,
        "East RMSE": np.sqrt(np.mean(np.square(east_errors))) if east_errors else np.nan,
        "North Min": np.min(north_errors) if north_errors else np.nan,
        "North Max": np.max(north_errors) if north_errors else np.nan,
        "North Mean": np.mean(north_errors) if north_errors else np.nan,
        "North RMSE": np.sqrt(np.mean(np.square(north_errors))) if north_errors else np.nan,
        "2D Min": np.min(plane_errors) if plane_errors else np.nan,
        "2D Max": np.max(plane_errors) if plane_errors else np.nan,
        "2D Mean": np.mean(plane_errors) if plane_errors else np.nan,
        "2D RMSE": np.sqrt(np.mean(np.square(plane_errors))) if plane_errors else np.nan
    }

    # 定义CSV列顺序
    fieldnames = [
        "Timestamp",
        "East Min", "East Max", "East Mean", "East RMSE",
        "North Min", "North Max", "North Mean", "North RMSE",
        "2D Min", "2D Max", "2D Mean", "2D RMSE"
    ]

    # 写入/追加到CSV文件
    file_exists = os.path.isfile(output_csv)

    with open(output_csv, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(stats)

    return stats

#调用
if __name__ == "__main__":
    results = calculate_android_errors(
        pos_file="F:\\GNSSdata\\Android GNSS data\\Android_pos\\0104_P1.pos",
        # G1
        true_lat=31.47293789,
        true_lon = 120.2538854,
        #
        # # G2
        # true_lat=31.47200456,
        # true_lon = 120.2537109,
        #
        # # G3
        # true_lat=31.47192006,
        # true_lon=120.2544413,
        #
        # # G4
        # true_lat=31.47286452,
        # true_lon=120.2546225,
        #
        # # G5
        # true_lat=31.47192112,
        # true_lon=120.2541585,

        output_csv="F:\\GNSSdata\\Android GNSS data\\android_pos_error.csv"
    )
    print("Results saved to CSV:")
    print(results)
