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
# input_csv_smsmoothed = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm+snrweight(1)\\sm+snrweight(P1).csv"
# input_csv_smbasic = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\GNSS_SM\\gnss_sm(P1)_snrweighted.csv"
# input_pos = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(p3).pos"
# output_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\GNSS_SM\\gnss_sm_errors(P1)_snrweighted.csv"
# figure_title = 'P3'

input_csv_1 = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm+xgboost_snrweight\\sm+xgboost_snrweight(P3).csv"
input_csv_0 = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\sm\\shadow_matching(P3).csv"       # sm_basic

input_pos = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\spp(p3).pos"
output_csv = "F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\xgb-sm_yanshou_test\\gnss_sm_preproc(P3)_error_yanshou.csv"
figure_title = 'P3'

# P1
# true_lat =31.496194
# true_lon =120.269652

# P2
# true_lat =31.496033
# true_lon =120.269650

# P3
true_lat =31.495794
true_lon =120.269597

# P4
# 31.496433  120.269643
# P6
# 31.496365  120.269643
#-----------------------------------读取 input_csv_1的 CSV 数据---------------------------------------
# 读取 shadow matching 的 CSV 数据
csv_df1 = pd.read_csv(input_csv_1)  # 修改路径
csv_coords = csv_df1[['X', 'Y', 'Z']].values
csv_df1['Timestamp'] = pd.to_datetime(csv_df1['Epoch'])

# ECEF → WGS84 → UTM
ecef_to_wgs84 = Transformer.from_crs("epsg:4978", "epsg:4326", always_xy=True)
utm_zone = int((true_lon + 180) / 6) + 1
utm_crs = CRS.from_proj4(f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs")
wgs84_to_utm = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)

# 处理 CSV 坐标 → 经纬度
csv_lons, csv_lats, _ = zip(*[ecef_to_wgs84.transform(x, y, z) for x, y, z in csv_coords])
csv_df1['Latitude'] = csv_lats
csv_df1['Longitude'] = csv_lons
csv_df1['easting'], csv_df1['northing'] = zip(*[wgs84_to_utm.transform(lon, lat) for lon, lat in zip(csv_df1['Longitude'], csv_df1['Latitude'])])

true_easting, true_northing = wgs84_to_utm.transform(true_lon, true_lat)
csv_df1['east_error'] = (csv_df1['easting'] - true_easting).abs()
csv_df1['north_error'] = (csv_df1['northing'] - true_northing).abs()
csv_df1['horizontal_error'] = np.sqrt(csv_df1['east_error']**2 + csv_df1['north_error']**2)

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


#--------------------------------------------------------------------------
# 合并两个 DataFrame，增加来源标签
csv_df1['Source'] = 'XGB-SM'
csv_df0['Source'] = 'SM'
combined_df = pd.concat([csv_df0[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']],
                         csv_df1[['Timestamp', 'east_error', 'north_error', 'horizontal_error', 'Source']],
                       ])

#保存误差统计数据
csv_stats0 = compute_error_stats(csv_df0)
csv_stats1 = compute_error_stats(csv_df1)


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
    'Timestamp': 'XGB-SM',
    **csv_stats1
}, {
    'Timestamp': 'SM',
    **csv_stats0
},])

out_df.to_csv(output_csv, index=False)  # 修改保存路径

#绘图对比误差（带来源标签）
#-----------------北向误差----------------------
plt.figure(figsize=(14, 4))
# 定义颜色列表
colors = ['cyan','orange']
labels = ['XGB-SM','SM']

for i, label in enumerate(labels):
    df_part = combined_df[combined_df['Source'] == label]
    # 指定曲线颜色
    plt.plot(df_part['Timestamp'], df_part['horizontal_error'], label=label, color=colors[i])

plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
# #plt.xticks(rotation=45)  # 旋转刻度标签
plt.xlabel('Time', fontsize=20)
plt.ylabel('Horizontal Error(m)', fontsize=20)
plt.title(figure_title, fontsize=20)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.legend(fontsize=16, loc='upper right')
plt.grid(True)
plt.tight_layout()
plt.show()
