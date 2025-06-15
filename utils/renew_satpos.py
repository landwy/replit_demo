# import math
#
# # 打开原始文件和输出文件
# input_file = 'F:\\GNSSdata\Android GNSS data\\2025-04-15\\GNSS_SM\\satpos_cov(P1).txt'      # 原始文件名
# output_file = 'F:\\GNSSdata\Android GNSS data\\2025-04-15\\GNSS_SM\\satpos_cov_new(P1).txt'    # 修改后的文件保存名
#
#
# def is_last_number_zero(line):
#     try:
#         parts = line.strip().split()
#         if not parts:
#             return False
#         return float(parts[-1]) == 0.0
#     except ValueError:
#         return False
#
# def process_line(line):
#     parts = line.strip().split()
#     if len(parts) < 10:
#         return None  # 非法行，跳过
#
#     try:
#         # 第 4、5、6 个数据为整型（可能为频率或标识类数据）
#         max456 = max(int(parts[3]), int(parts[4]), int(parts[5]))/1000
#
#         # 第 7 是卫星号，8、9 是弧度转角度
#         sat_id = parts[6]
#         rad1 = float(parts[7])
#         rad2 = float(parts[8])
#         deg1 = rad1 * 180.0 / math.pi
#         deg2 = rad2 * 180.0 / math.pi
#
#         # 保留原始前三列 + 最大值 + sat_id + 弧度转角度 + 第10个数据（一般为载噪比）
#         new_parts = parts[0:3] + [str(max456), sat_id,
#                                   f"{deg1:.6f}", f"{deg2:.6f}", parts[9]]
#         return ' '.join(new_parts) + '\n'
#     except Exception:
#         return None  # 遇到错误，跳过
#
# with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
#     buffer = []
#     in_block = False
#
#     for line in fin:
#         stripped = line.strip()
#         if stripped.startswith('time'):
#             # 写入之前 buffer 中有效的行
#             for data_line in buffer:
#                 if not is_last_number_zero(data_line):
#                     processed = process_line(data_line)
#                     if processed:
#                         fout.write(processed)
#             buffer = []
#
#             time_parts = stripped.split()
#             if len(time_parts) > 1:
#                 time_parts.pop()
#             fout.write(' '.join(time_parts) + '\n')
#
#             in_block = True
#         else:
#             if in_block:
#                 buffer.append(line)
#
#     # 写入最后一块
#     for data_line in buffer:
#         if not is_last_number_zero(data_line):
#             processed = process_line(data_line)
#             if processed:
#                 fout.write(processed)


#--------------------------------------处理有协方差矩阵的satpos文件----------------------------------------

import math

# 打开原始文件和输出文件
input_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\GNSS_SM\\satpos_cov(P1).txt'      # 原始文件名
output_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\GNSS_SM\\satpos_cov_new(P1).txt'    # 修改后的文件保存名


def is_tenth_number_zero(line):
    try:
        parts = line.strip().split()
        if len(parts) < 10:
            return False  # 列数不足，不视为有效行
        return float(parts[9]) == 0.0  # 检查第10个数据（索引9，从0开始计数）
    except ValueError:
        return False

def process_line(line):
    parts = line.strip().split()
    if len(parts) < 19:  # 新增9列后，至少需要19列数据
        return None  # 非法行，跳过

    try:
        # 第4、5、6个数据为整型（可能为频率或标识类数据）
        max456 = max(int(parts[3]), int(parts[4]), int(parts[5])) / 1000

        # 第7个是卫星号，8、9是弧度转角度（注意：新增列后索引可能变化，假设卫星号仍在第6列，弧度数据仍在7、8列）
        sat_id = parts[6]
        rad1 = float(parts[7])
        rad2 = float(parts[8])
        deg1 = rad1 * 180.0 / math.pi
        deg2 = rad2 * 180.0 / math.pi

        # 保留原始前三列 + 最大值 + sat_id + 弧度转角度 + 第10个数据（现在可能是原第10列，新增列在其后）
        new_parts = parts[0:3] + [str(max456), sat_id,
                                  f"{deg1:.6f}", f"{deg2:.6f}"] + parts[9:]  # 保留第10列及之后所有新增列
        return ' '.join(new_parts) + '\n'
    except Exception as e:
        print(f"处理行时出错: {e}")
        return None  # 遇到错误，跳过

with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
    buffer = []
    in_block = False

    for line in fin:
        stripped = line.strip()
        if stripped.startswith('time'):
            # 写入之前buffer中有效的行（过滤第10个数据为0的行）
            for data_line in buffer:
                if not is_tenth_number_zero(data_line):
                    processed = process_line(data_line)
                    if processed:
                        fout.write(processed)
            buffer = []

            time_parts = stripped.split()

            fout.write(' '.join(time_parts) + '\n')

            in_block = True
        else:
            if in_block:
                buffer.append(line)

    # 处理最后一个数据块
    for data_line in buffer:
        if not is_tenth_number_zero(data_line):
            processed = process_line(data_line)
            if processed:
                fout.write(processed)