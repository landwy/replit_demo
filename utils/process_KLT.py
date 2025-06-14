#
# #-------------------------------------------第一次处理的代码-----------------------------------------------------
# # import pickle
# # import csv
# import pyrtklib as prl
# from datetime import datetime, timezone, timedelta
# # import logging
# import pandas as pd
# import pickle
#
# # ------合并标签文件和卫星信息文件------
# def satindex2name(sats):
#     name = prl.Arr1Dchar(4)
#     if not isinstance(sats,list):
#         prl.satno2id(sats+1,name)
#         return name.ptr
#     names = []
#     for i in sats:
#         prl.satno2id(i+1,name)
#         names.append(name.ptr)
#     return names
#
#
# # 解析txt文件
# def parse_txt(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
#
#     data = []
#     current_time = None
#
#     for line in lines:
#         parts = line.strip().split()
#         if not parts:
#             continue
#
#         if parts[0] == 'time':
#             # 去掉毫秒，只保留秒
#             current_time = parts[1] + " " + parts[2].split('.')[0]
#         else:
#             if current_time:
#                 x, y, z = map(float, parts[0:3])
#                 snr0 = float(parts[3])
#                 snr1 = float(parts[4])
#                 satellite_name = parts[5]
#                 azimuth = float(parts[6])
#                 elevation = float(parts[7])
#
#                 data.append([current_time, satellite_name, x, y, z, snr0, snr1, azimuth, elevation])
#
#     return pd.DataFrame(data, columns=["time", "satellite", "X", "Y", "Z", "SNR0","SNR1", "azimuth", "elevation"])
#
#
# # 读取.pkl标签文件
# def load_pkl(file_path):
#     with open(file_path, 'rb') as f:
#         labels = pickle.load(f)
#
#     pkl_data = {}
#     for label in labels:
#         # 转换 UNIX 时间戳，并去掉毫秒
#         timestamp = datetime.fromtimestamp(label[0], tz=timezone.utc) + timedelta(seconds=18)
#         timestamp_str = timestamp.strftime("%Y/%m/%d %H:%M:%S")  # 保留到秒
#
#         los_satellites = label[2]  # LOS卫星索引
#         los_satellite_names = set(satindex2name(los_satellites))
#         pkl_data[timestamp_str] = los_satellite_names
#
#     return pkl_data  # {GPS时间字符串: {LOS卫星名称}}
#
#
# # 合并数据
# def merge_data(txt_df, pkl_data):
#     txt_df["LOS"] = txt_df.apply(lambda row: 1 if row["satellite"] in pkl_data.get(row["time"], set()) else 0, axis=1)
#     return txt_df
#
#
# # 运行脚本
# def run_merge_data(txt_file, pkl_file, output_csv):
#     txt_df = parse_txt(txt_file)
#     pkl_data = load_pkl(pkl_file)
#     merged_df = merge_data(txt_df, pkl_data)
#     merged_df.to_csv(output_csv, index=False)
#     print(f"Merged data saved to {output_csv}")
#
# #示例调用
# txt_file_path = "F:\\GNSSdata\KLTDataset\\label\\1109_KLT1_421\\satpos421.txt"
# pkl_file_path = "F:\\GNSSdata\KLTDataset\\label\\1109_KLT1_421\\nlos.pkl"
# csv_file_path = "F:\\GNSSdata\KLTDataset\\label\\1109_KLT1_421\\merged_data421.csv"
#
# run_merge_data(txt_file_path, pkl_file_path, csv_file_path)

#------------------------------------第二次重新处理的代码----------------------------------------------

# import csv
# import pickle
# import pyrtklib as prl
#
# # 时间常量
# GPS_START_UNIX = 315964800  # GPS起始时间的Unix时间戳
# LEAP_SECONDS = 18           # GPS与UTC的时间差
#
# # def gps2unix(week, tow):
# #     """将GPS时间（week + tow）转换为Unix时间戳"""
# #     return round(GPS_START_UNIX + week * 7 * 86400 + tow - LEAP_SECONDS, 3)
#
# def gps2gpstime(week, tow):
#     """将GPS周和周内秒转换为总的GPS秒数"""
#     return round(GPS_START_UNIX + week * 7 * 86400 + tow)
#
#
# def satindex2name(sats):
#     """将卫星索引转换为名称（如G01，C02）"""
#     name = prl.Arr1Dchar(4)
#     if not isinstance(sats, list):
#         prl.satno2id(sats + 1, name)
#         return name.ptr
#     names = []
#     for i in sats:
#         prl.satno2id(i + 1, name)
#         names.append(name.ptr)
#     return names
#
#
# def load_los_labels(label_file_paths):
#     los_dict = {}
#     for label_path in label_file_paths:
#         print(f"Loading labels from {label_path}...")
#         with open(label_path, 'rb') as f:
#             labels = pickle.load(f)
#         for label in labels:
#             timestamp = int(label[0])  #gps秒
#             print(timestamp)
#             los_sats = set(satindex2name(label[2]))
#             los_dict[timestamp] = los_sats
#             print(f"Loaded {len(labels)} labels from {label_path}.")
#     return los_dict
#
# def normalize(values):
#     """归一化伪距残差"""
#     min_v = min(values)
#     max_v = max(values)
#     if max_v - min_v == 0:
#         return [0 for _ in values]
#     return [(v - min_v) / (max_v - min_v) for v in values]
#
# def process_status_file(status_file_path, label_file_paths, output_csv_path):
#     los_dict = load_los_labels(label_file_paths)
#
#     output_rows = []
#     current_epoch_data = []
#
#     with open(status_file_path, 'r') as f:
#         for line in f:
#             if line.startswith("$POS"):
#                 if current_epoch_data:
#                     # 上一个历元结束，处理数据
#                     resps = [item[-1] for item in current_epoch_data]
#                     norm_resps = normalize(resps)
#                     week, tow = current_epoch_data[0][0], current_epoch_data[0][1]  #以第一颗卫星的时间作为历元时间
#                     gps_time = gps2gpstime(week, tow)
#                     los_sats = los_dict.get(gps_time, None)
#
#                     for i, item in enumerate(current_epoch_data):
#                         week, tow, sat, az, el, snr, _ = item
#                         if los_sats is None:
#                             los_flag = 2
#                         else:
#                             los_flag = 1 if sat in los_sats else 0
#                         output_rows.append([week, tow, sat, az, el, snr, norm_resps[i], los_flag])
#                         #output_rows.append([week, tow, sat, az, el, snr, resps[i], los_flag])
#                     current_epoch_data = []
#
#             elif line.startswith("$SAT"):
#                 parts = line.strip().split(',')
#                 week = int(parts[1])
#                 tow = int(float(parts[2]))
#                 sat = parts[3]
#
#                 # 只保留GPS (G) 和 北斗 (C)
#                 if not (sat.startswith('G') or sat.startswith('C')):
#                     continue
#
#                 az = float(parts[5])
#                 el = float(parts[6])
#                 resp = float(parts[7])
#                 snr = float(parts[10])
#                 current_epoch_data.append([week, tow, sat, az, el, snr, resp])
#
#         # 文件末尾也要处理最后一个历元
#         if current_epoch_data:
#             resps = [item[-1] for item in current_epoch_data]
#             norm_resps = normalize(resps)
#             week, tow = current_epoch_data[0][0], current_epoch_data[0][1]
#             gps_time = gps2gpstime(week, tow)
#             los_sats = los_dict.get(gps_time, None)
#
#             for i, item in enumerate(current_epoch_data):
#                 week, tow, sat, az, el, snr, _ = item
#                 if los_sats is None:
#                     los_flag = 2
#                 else:
#                     los_flag = 1 if sat in los_sats else 0
#                 output_rows.append([week, tow, sat, az, el, snr, norm_resps[i], los_flag])
#
#     # 写入CSV
#     with open(output_csv_path, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(['week', 'tow', 'sat', 'az', 'el', 'snr', 'norm_resp', 'LOS'])
#         writer.writerows(output_rows)
#
# # 示例调用
#
# if __name__ == '__main__':
#     label_paths = [
#         'F:\\GNSSdata\\KLTDataset\\label\\1109_KLT1_421\\nlos.pkl',
#         'F:\\GNSSdata\\KLTDataset\\label\\1109_KLT2_294\\nlos.pkl',
#         'F:\\GNSSdata\\KLTDataset\\label\\1109_KLT2_301\\nlos.pkl',
#         'F:\\GNSSdata\\KLTDataset\\label\\1109_KLT3_666\\nlos.pkl',
#     ]
#
#     process_status_file(
#         'F:\\GNSSdata\\rf_train\\new\\spp.pos.stat',
#         label_paths,
#         'F:\\GNSSdata\\rf_train\\new\\gps_bds_with_los(no_normalization).csv'
#     )



#-----------------------------------------------剔除没有匹配的历元数据----------------------------------------------------
import csv

def filter_los_data(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r') as infile, open(output_csv_path, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(header)  # 写入表头

        for row in reader:
            try:
                los_value = int(row[-1])  # LOS 列在最后一列
                if los_value != 2:
                    writer.writerow(row)
            except ValueError:
                # 处理非整数（比如空值）情况
                continue

# 使用方式
filter_los_data(
    'F:\\GNSSdata\\rf_train\\new\\gps_bds_with_los(no_normalization).csv',
    'F:\\GNSSdata\\rf_train\\new\\gps_bds_with_los_filtered(no_normalization).csv'
)
