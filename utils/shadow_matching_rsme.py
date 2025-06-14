# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from pyproj import Transformer, CRS
# import matplotlib.ticker as ticker
#
# # ======= 1. 参数 =======
# input_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\shadow_matching\\shadow_matching(P1).csv"
# output_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\shadow_matching\\smbasic(P1)_errors.csv"
#
# true_lat =31.496194
# true_lon =120.269652
#
# # P1
# # 31.496194  120.269652
# #
# # P2
# # 31.496033  120.269650
# #
# # P3
# # 31.495794  120.269597
# #
# # P4
# # 31.496433  120.269643
# #
# # P6
# # 31.496365  120.269643
#
# # ======= 2. 读取数据 =======
# df = pd.read_csv(input_csv)
# ecef_coords = df[['X', 'Y', 'Z']].values
#
# # ======= 3. 坐标转换器 =======
# ecef_to_wgs84 = Transformer.from_crs("epsg:4978", "epsg:4326", always_xy=True)
# utm_zone = int((true_lon + 180) / 6) + 1
# utm_crs = CRS.from_proj4(f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs")
# wgs84_to_utm = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
#
# # ======= 4. 转换坐标 =======
# lons, lats, alts = zip(*[ecef_to_wgs84.transform(x, y, z) for x, y, z in ecef_coords])
# df['lat'] = lats
# df['lon'] = lons
#
# eastings, northings = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(lons, lats)])
# df['easting'] = eastings
# df['northing'] = northings
#
# true_easting, true_northing = wgs84_to_utm.transform(true_lon, true_lat)
#
# # ======= 5. 误差计算 =======
# df['east_error'] = df['easting'] - true_easting
# df['north_error'] = df['northing'] - true_northing
# df['horizontal_error'] = np.sqrt(df['east_error']**2 + df['north_error']**2)
#
# # ======= 6. 误差统计（基于绝对值）=======
# def rms(x): return np.sqrt(np.mean(np.square(x)))
#
# def get_stats(series):
#     abs_series = series.abs()  # ← 只考虑绝对误差
#     return {
#         "Min": abs_series.min(),
#         "Max": abs_series.max(),
#         "Mean": abs_series.mean(),
#         "RMSE": rms(abs_series)
#     }
#
# east_stats = get_stats(df['east_error'])
# north_stats = get_stats(df['north_error'])
# horiz_stats = get_stats(df['horizontal_error'])
#
# # ======= 7. 构造输出行并保存 =======
# summary_row = {
#     "Timestamp": df['Epoch'].iloc[0],
#     "East Min": east_stats["Min"],
#     "East Max": east_stats["Max"],
#     "East Mean": east_stats["Mean"],
#     "East RMSE": east_stats["RMSE"],
#     "North Min": north_stats["Min"],
#     "North Max": north_stats["Max"],
#     "North Mean": north_stats["Mean"],
#     "North RMSE": north_stats["RMSE"],
#     "2D Min": horiz_stats["Min"],
#     "2D Max": horiz_stats["Max"],
#     "2D Mean": horiz_stats["Mean"],
#     "2D RMSE": horiz_stats["RMSE"]
# }
#
# summary_df = pd.DataFrame([summary_row])
# summary_df.to_csv(output_csv, index=False)
# print(f"✅ 绝对误差统计结果已保存到：{output_csv}")
#
# # ======= 8. 绘图 =======
# plt.figure(figsize=(12, 6))
#
# # 假设 Epoch 列名是 'Epoch'，格式是类似 "2025/4/15  8:29:19"
# df['Time'] = pd.to_datetime(df['Epoch'], format='%Y/%m/%d %H:%M:%S.%f')
# # 提取时分秒字符串，只显示 "HH:MM:SS"
# df['TimeStr'] = df['Time'].dt.strftime('%H:%M:%S')
#
# # 绘图
# plt.plot(df['TimeStr'], df['east_error'].abs(), label='|East Error|')
# plt.plot(df['TimeStr'], df['north_error'].abs(), label='|North Error|')
# plt.plot(df['TimeStr'], df['horizontal_error'], label='2D Error')
#
# # 设置 X 轴显示的刻度数量（例如只显示10个）
# plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
# #plt.xticks(rotation=45)  # 旋转刻度标签
#
# plt.xlabel('Time',fontsize=20)
# plt.ylabel('Error (m)',fontsize=20)
# plt.title('Position Errors(P1)',fontsize=20)
#
# plt.tick_params(axis='x', labelsize=18)  # 设置 X 轴刻度字体大小为 12
# plt.tick_params(axis='y', labelsize=18)  # 设置 Y 轴刻度字体大小为 12
#
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer, CRS
import matplotlib.ticker as ticker
import matplotlib.dates as mdates


# 读取 POS 文件
def read_pos_file(filename):
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
                    lat = float(data[2])
                    lon = float(data[3])
                    height = float(data[4])
                    timestamps.append(timestamp)
                    latitudes.append(lat)
                    longitudes.append(lon)
                    heights.append(height)
                except (ValueError, IndexError):
                    continue

    return pd.DataFrame({
        'Timestamp': pd.to_datetime(timestamps),
        'Latitude': latitudes,
        'Longitude': longitudes,
        'Height': heights
    })

def compute_error_stats(df):
    def rms(x): return np.sqrt(np.mean(np.square(x)))
    return {
        'East Min': df['east_error'].min(),
        'East Max': df['east_error'].max(),
        'East Mean': df['east_error'].mean(),
        'East RMSE': rms(df['east_error']),
        'North Min': df['north_error'].min(),
        'North Max': df['north_error'].max(),
        'North Mean': df['north_error'].mean(),
        'North RMSE': rms(df['north_error']),
        '2D Min': df['horizontal_error'].min(),
        '2D Max': df['horizontal_error'].max(),
        '2D Mean': df['horizontal_error'].mean(),
        '2D RMSE': rms(df['horizontal_error']),
    }

# 替换为你的真实坐标
input_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm+smoothed\\shadow_matching(P1).csv"
input_pos = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(p1).pos"
#input_csv_smbasic = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm\\shadow_matching(P1).csv"
output_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm+smoothed\\\sm_smoothed_errors(P1).csv"

# P1
true_lat =31.496194
true_lon =120.269652

# P2
# true_lat =31.496033
# true_lon =120.269650

# P3
# true_lat =31.495794
# true_lon =120.269597

# P4
# 31.496433  120.269643
# P6
# 31.496365  120.269643

# 读取 shadow matching 的 CSV 数据
csv_df = pd.read_csv(input_csv)  # 修改路径
csv_coords = csv_df[['X', 'Y', 'Z']].values
csv_df['Timestamp'] = pd.to_datetime(csv_df['Epoch'])

# ECEF → WGS84 → UTM
ecef_to_wgs84 = Transformer.from_crs("epsg:4978", "epsg:4326", always_xy=True)
utm_zone = int((true_lon + 180) / 6) + 1
utm_crs = CRS.from_proj4(f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs")
wgs84_to_utm = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)

# 处理 CSV 坐标 → 经纬度
csv_lons, csv_lats, _ = zip(*[ecef_to_wgs84.transform(x, y, z) for x, y, z in csv_coords])
csv_df['Latitude'] = csv_lats
csv_df['Longitude'] = csv_lons
csv_df['easting'], csv_df['northing'] = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(csv_df['Longitude'], csv_df['Latitude'])])

true_easting, true_northing = wgs84_to_utm.transform(true_lon, true_lat)
csv_df['east_error'] = (csv_df['easting'] - true_easting).abs()
csv_df['north_error'] = (csv_df['northing'] - true_northing).abs()
csv_df['horizontal_error'] = np.sqrt(csv_df['east_error']**2 + csv_df['north_error']**2)

#读取初始定位文件
pos_df = read_pos_file(input_pos)  # 修改路径
pos_df['easting'], pos_df['northing'] = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(pos_df['Longitude'], pos_df['Latitude'])])
pos_df['east_error'] = (pos_df['easting'] - true_easting).abs()
pos_df['north_error'] = (pos_df['northing'] - true_northing).abs()
pos_df['horizontal_error'] = np.sqrt(pos_df['east_error']**2 + pos_df['north_error']**2)

# 合并两个 DataFrame，增加来源标签
csv_df['Source'] = 'ShadowMatching'
pos_df['Source'] = 'SPP'
combined_df = pd.concat([csv_df[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']],
                         pos_df[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']]])

#保存误差统计数据
csv_stats = compute_error_stats(csv_df)
pos_stats = compute_error_stats(pos_df)

out_df = pd.DataFrame([{
    'Timestamp': 'CSV',
    **csv_stats
}, {
    'Timestamp': 'SPP',
    **pos_stats
}])

out_df.to_csv(output_csv, index=False)  # 修改保存路径

#绘图对比误差（带来源标签）
#-----------------北向误差----------------------
plt.figure(figsize=(14, 6))
for label in ['ShadowMatching', 'SPP']:
    df_part = combined_df[combined_df['Source'] == label]
    plt.plot(df_part['Timestamp'], df_part['east_error'], label=label)

plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
# #plt.xticks(rotation=45)  # 旋转刻度标签
plt.xlabel('Time', fontsize=20)
plt.ylabel('North Error (m)', fontsize=20)
plt.title('P1', fontsize=20)
plt.xticks( fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=16)
plt.grid(True)
plt.tight_layout()
plt.show()



# 创建图和子图（共3行1列）
# fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
# error_types = ['east_error', 'north_error', 'horizontal_error']
# titles = ['East Error (m)', 'North Error (m)', 'Horizontal Error (m)']
# colors = {'ShadowMatching': 'tab:blue', 'SPP': 'tab:orange'}
#
# for i, (err, title) in enumerate(zip(error_types, titles)):
#     for label in ['ShadowMatching', 'SPP']:
#         df_part = combined_df[combined_df['Source'] == label]
#         axs[i].plot(
#             df_part['Timestamp'].dt.strftime('%H:%M:%S'),
#             df_part[err],
#             label=label,
#             color=colors[label] if i == 0 else None,  # 只为第一个子图指定颜色
#             linewidth=1.5
#         )
#
#     axs[i].set_ylabel(title, fontsize=18)
#     axs[i].grid(True)
#     axs[i].tick_params(axis='y', labelsize=18)
#     axs[i].tick_params(axis='x', labelsize=18)
# plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
# axs[2].set_xlabel('Time', fontsize=20)
# axs[0].legend(fontsize=16)
# plt.suptitle('Position Errors of P5', fontsize=20)
# plt.tight_layout(rect=[0, 0, 1, 0.96])
# plt.show()
