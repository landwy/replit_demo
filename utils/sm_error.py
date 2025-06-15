# #---------------------------------sm和spp误差对比（柱状图）---------------------------------
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
#
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文显示
# plt.rcParams['axes.unicode_minus'] = False
#
# # 读取误差文件
# #error_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\shadow_matching\\smbasic_all_errors.csv'
# error_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm\\smbasic_all_errors.csv'
# df = pd.read_csv(error_file)
#
# if 'Timestamp' in df.columns:
#     df = df.drop(columns=['Timestamp'])
# # 拿第一组数据作为代表
# spm = df.iloc[0]
# spp = df.iloc[1]
#
# # 选择要对比的误差项
# error_items = ['East Mean', 'East RMSE', 'North Mean', 'North RMSE', '2D Mean', '2D RMSE']
#
# spm_vals = [spm[item] for item in error_items]
# spp_vals = [spp[item] for item in error_items]
#
# x = np.arange(len(error_items))  # 横轴位置
# width = 0.25  # 柱宽设为窄一点
#
# fig, ax = plt.subplots(figsize=(12, 6))
#
# ax.bar(x - width/2, spp_vals, width, label='SPP', color='orange')
# ax.bar(x + width/2, spm_vals, width, label='Shadow Matching', color='royalblue')
#
# # 设置图形属性
# ax.set_ylabel('误差值 (m)',fontsize=20)
# ax.set_xlabel('误差项',fontsize=20)
# #ax.set_title('SPP 与 阴影匹配各项误差对比')
# ax.set_xticks(x)
# ax.set_xticklabels(error_items, rotation=0, fontsize=16)
# ax.tick_params(axis='y', labelsize=16)
# ax.legend(fontsize=16)
# ax.grid(True, linestyle='--', alpha=0.3)
#
# plt.tight_layout()
# plt.show()

#----------------------------------------sm与spp误差对比-----------------------------------

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


input_csv_0 = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm\\shadow_matching(P1).csv"       # sm_basic
input_pos = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(p1).pos"
output_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm_yanshou_test\\sm(P1)_error.csv"
figure_title = 'P1'

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


#-------------------------------------读取input_csv_0即shadow matching 的 CSV 数据-----------------------
# 读取 shadow matching 的 CSV 数据
csv_df0 = pd.read_csv(input_csv_0)  # 修改路径
csv_coords2 = csv_df0[['X', 'Y', 'Z']].values
csv_df0['Timestamp'] = pd.to_datetime(csv_df0['Epoch'])

# ECEF → WGS84 → UTM
ecef_to_wgs84 = Transformer.from_crs("epsg:4978", "epsg:4326", always_xy=True)
utm_zone = int((true_lon + 180) / 6) + 1
utm_crs = CRS.from_proj4(f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs")
wgs84_to_utm = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)

# 处理 CSV 坐标 → 经纬度
csv_lons, csv_lats, _ = zip(*[ecef_to_wgs84.transform(x, y, z) for x, y, z in csv_coords2])
csv_df0['Latitude'] = csv_lats
csv_df0['Longitude'] = csv_lons
csv_df0['easting'], csv_df0['northing'] = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(csv_df0['Longitude'], csv_df0['Latitude'])])

true_easting, true_northing = wgs84_to_utm.transform(true_lon, true_lat)
csv_df0['east_error'] = (csv_df0['easting'] - true_easting).abs()
csv_df0['north_error'] = (csv_df0['northing'] - true_northing).abs()
csv_df0['horizontal_error'] = np.sqrt(csv_df0['east_error']**2 + csv_df0['north_error']**2)


#-------------------------------------读取SPP.pos数据-----------------------
#读取初始定位文件
pos_df = read_pos_file(input_pos)  # 修改路径
pos_df['easting'], pos_df['northing'] = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(pos_df['Longitude'], pos_df['Latitude'])])
pos_df['east_error'] = (pos_df['easting'] - true_easting).abs()
pos_df['north_error'] = (pos_df['northing'] - true_northing).abs()
pos_df['horizontal_error'] = np.sqrt(pos_df['east_error']**2 + pos_df['north_error']**2)
#--------------------------------------------------------------------------
# 合并两个 DataFrame，增加来源标签
csv_df0['Source'] = 'ShadowMatching'
pos_df['Source'] = 'SPP'
combined_df = pd.concat([csv_df0[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']],
                         pos_df[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']]])

#保存误差统计数据
csv_stats0 = compute_error_stats(csv_df0)
pos_stats = compute_error_stats(pos_df)

# out_df = pd.DataFrame([{
#     'Timestamp': 'sm_smoothed',
#     **csv_stats1
# }, {
#     'Timestamp': 'sm',
#     **csv_stats2
# },{
#     'Timestamp': 'SPP',
#     **pos_stats
# }])

out_df = pd.DataFrame([{
    'Timestamp': 'SM',
    **csv_stats0
},{
    'Timestamp': 'SPP',
    **pos_stats
}])

out_df.to_csv(output_csv, index=False)  # 修改保存路径

#绘图对比误差（带来源标签）
#-----------------北向误差----------------------
plt.figure(figsize=(14, 4))
# 定义颜色列表
colors = ['steelblue' , 'orange']
labels = ['ShadowMatching','SPP']

for i, label in enumerate(labels):
    df_part = combined_df[combined_df['Source'] == label]
    # 指定曲线颜色
    # plt.plot(df_part['Timestamp'], df_part['east_error'], label=label, color=colors[i])
    plt.plot(df_part['Timestamp'], df_part['north_error'], label=label, color=colors[i])
    # plt.plot(df_part['Timestamp'], df_part['horizontal_error'], label=label, color=colors[i])


plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
# #plt.xticks(rotation=45)  # 旋转刻度标签
plt.xlabel('Time', fontsize=20)
# plt.ylabel('East Error(m)', fontsize=20)
plt.ylabel('North Error(m)', fontsize=20)
# plt.ylabel('Horizontal Error(m)', fontsize=20)
plt.title(figure_title, fontsize=20)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=16, loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.show()
