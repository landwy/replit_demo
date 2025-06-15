#--------------------------------------------------------android定位误差可视化------------------------------------------------
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import matplotlib.ticker as ticker
# # 数据加载
# df = pd.read_csv("F:\\GNSSdata\\Android GNSS data\\2025-04-08\\Android_position_errors.csv")
#
# # 箱线图
# plt.figure(figsize=(10, 8))
# ax = sns.boxplot(data=df[["East RMSE", "North RMSE", "2D RMSE"]])
#
# # 提取三列数据的Q1、Q2、Q3
# for i, col in enumerate(["East RMSE", "North RMSE", "2D RMSE"]):
#     q1 = df[col].quantile(0.25)
#     q2 = df[col].quantile(0.5)
#     q3 = df[col].quantile(0.75)
#
#     # 在箱体旁边添加文本标注
#     ax.text(i, q1, f"Q1={q1:.2f}", ha='center', va='bottom', fontsize=12, color='black')
#     ax.text(i, q2, f"Q2={q2:.2f}", ha='center', va='bottom', fontsize=12, color='blue')
#     ax.text(i, q3, f"Q3={q3:.2f}", ha='center', va='bottom', fontsize=12, color='red')
#
# plt.ylabel("Error (m)", fontsize=20)
# plt.xticks(fontsize=20)
# ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
# ax.tick_params(axis='both', which='major', labelsize=20)
# plt.tight_layout()
# plt.show()
#
# # 散点图与误差椭圆
# plt.figure(figsize=(8, 7))
# sns.scatterplot(x="East Mean", y="North Mean", data=df, s=100, alpha=0.7)
# plt.xlabel("East Error (m)", fontsize=20)
# plt.ylabel("North Error (m)", fontsize=20)
# #plt.title("East vs North Positioning Errors")
# plt.grid(True)
# ax = plt.gca()
# ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
# ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
# ax.tick_params(axis='both', which='major', labelsize=20)
# plt.show()
#
# # CDF曲线
# plt.figure(figsize=(8,7))
# df_sorted = df.sort_values("2D RMSE").reset_index(drop=True)
# df_sorted["CDF"] = (df_sorted.index + 1) / len(df_sorted)
# plt.plot(df_sorted["2D RMSE"], df_sorted["CDF"], marker=".", linestyle="-")
#
# # 添加每个点的上下错开标注
# for i in range(len(df_sorted)):
#     x = df_sorted.loc[i, "2D RMSE"]
#     y = df_sorted.loc[i, "CDF"]
#
#     # 标注位置错开：奇数向上，偶数向下
#     y_offset = -0.01 if i % 2 == 1 else 0.01
#
#     plt.text(x, y + y_offset, f"({x:.2f}, {y:.2f})",
#              fontsize=10, ha="center", rotation=0)
#
# plt.xlabel("2D RMSE (m)", fontsize=20)
# plt.ylabel("Cumulative Probability", fontsize=20)
# #plt.title("Cumulative Distribution of 2D RMSE")
# plt.grid(True)
# ax = plt.gca()
# ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
# ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
# ax.tick_params(axis='both', which='major', labelsize=20)
# plt.show()


#--------------------------------------------异常值剔除效果----------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_rel

# === Step 1: 读取数据 ===
excel_path = 'F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\error\\error_summary.xlsx'  # TODO: 改成你的路径
df = pd.read_excel(excel_path)

# 检查列名
required_columns = ["number", "East RMSE", "North RMSE", "2D RMSE"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"缺少必要列: {col}")

# === Step 2: 分离原始与滤波数据 ===
raw_df = df.iloc[::2].reset_index(drop=True)      # 原始数据（奇数行）
filt_df = df.iloc[1::2].reset_index(drop=True)    # 滤波数据（偶数行）

# === Step 3: 计算每项指标的改进百分比 ===
def compute_improvement(raw, filt):
    return ((raw - filt) / raw * 100).round(2)

improvements = pd.DataFrame({
    "number": raw_df["number"],
    "East RMSE %↓": compute_improvement(raw_df["East RMSE"], filt_df["East RMSE"]),
    "North RMSE %↓": compute_improvement(raw_df["North RMSE"], filt_df["North RMSE"]),
    "2D RMSE %↓": compute_improvement(raw_df["2D RMSE"], filt_df["2D RMSE"]),
})

print("\n📊 各测点误差下降百分比：")
print(improvements)

# 平均改进
avg_improve = improvements.mean(numeric_only=True).round(2)
print("\n✅ 平均误差改善（%）：")
print(avg_improve)

# === Step 4: 可视化（以 2D RMSE 为例） ===
plt.figure(figsize=(12, 6))
x = raw_df['number'].astype(str)

plt.plot(x, raw_df["2D RMSE"], label='原始 2D RMSE', marker='o')
plt.plot(x, filt_df["2D RMSE"], label='滤波后 2D RMSE', marker='o')
plt.title("各测点 2D RMSE 对比")
plt.xlabel("测点编号")
plt.ylabel("2D RMSE (米)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()

# === Step 5: t 检验 ===
t_stat, p_value = ttest_rel(raw_df["2D RMSE"], filt_df["2D RMSE"])
print(f"\n🧪 成对 t 检验结果：t = {t_stat:.3f}, p = {p_value:.4f}")
if p_value < 0.05:
    print("✅ 差异显著，滤波处理有效提升定位精度！")
else:
    print("⚠️ 差异不显著，可能还需优化滤波策略。")

#----------------------------------------------------------------------------------------------------
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy import stats
#
#
# def analyze_positioning_data(file_path):
#     # 读取数据
#     df = pd.read_excel(file_path)
#
#     # 预处理：确保数据按测点编号正确配对
#     df = df.sort_values(by='number').reset_index(drop=True)
#
#     # 分割原始组和处理组
#     raw_data = df.iloc[::2, :].reset_index(drop=True)  # 偶数行
#     processed_data = df.iloc[1::2, :].reset_index(drop=True)  # 奇数行
#
#     # 数据校验
#     assert len(raw_data) == len(processed_data), "数据配对不完整"
#
#     # 合并为配对数据集
#     paired_df = pd.concat([raw_data.add_prefix('raw_'), processed_data.add_prefix('proc_')], axis=1)
#
#     # 描述性统计
#     def calc_stats(metric_prefix):
#         return {
#             '原始均值': paired_df[f'raw_{metric_prefix} Mean'].mean(),
#             '处理后均值': paired_df[f'proc_{metric_prefix} Mean'].mean(),
#             '均值变化(%)': (paired_df[f'proc_{metric_prefix} Mean'].mean() - paired_df[
#                 f'raw_{metric_prefix} Mean'].mean())
#                            / paired_df[f'raw_{metric_prefix} Mean'].mean() * 100,
#             '原始RMSE': paired_df[f'raw_{metric_prefix} RMSE'].mean(),
#             '处理后RMSE': paired_df[f'proc_{metric_prefix} RMSE'].mean(),
#             'RMSE变化(%)': (paired_df[f'proc_{metric_prefix} RMSE'].mean() - paired_df[
#                 f'raw_{metric_prefix} RMSE'].mean())
#                            / paired_df[f'raw_{metric_prefix} RMSE'].mean() * 100
#         }
#
#     stats_results = {
#         '东向': calc_stats('East'),
#         '北向': calc_stats('North'),
#         '2D': calc_stats('2D')
#     }
#
#     # 统计检验
#     def perform_tests(raw_col, proc_col):
#         # 正态性检验
#         _, p_raw = stats.normaltest(paired_df[raw_col])
#         _, p_proc = stats.normaltest(paired_df[proc_col])
#
#         if (p_raw > 0.05) and (p_proc > 0.05):
#             # 配对t检验
#             t_stat, p_t = stats.ttest_rel(paired_df[raw_col], paired_df[proc_col])
#             test_type = 't检验'
#         else:
#             # Wilcoxon符号秩检验
#             stat, p_t = stats.wilcoxon(paired_df[raw_col], paired_df[proc_col])
#             test_type = 'Wilcoxon检验'
#         return p_t, test_type
#
#     metrics = [
#         ('raw_East RMSE', 'proc_East RMSE'),
#         ('raw_North RMSE', 'proc_North RMSE'),
#         ('raw_2D RMSE', 'proc_2D RMSE')
#     ]
#
#     test_results = {}
#     for raw, proc in metrics:
#         p_val, test_type = perform_tests(raw, proc)
#         test_results[raw.split('_')[1]] = {
#             'p值': p_val,
#             '检验方法': test_type,
#             '显著性': '显著' if p_val < 0.05 else '不显著'
#         }
#
#     # 可视化
#     plt.figure(figsize=(18, 12))
#     sns.set(style="whitegrid", palette="pastel")
#
#     # 箱线图对比
#     plt.subplot(2, 2, 1)
#     plot_data = pd.melt(paired_df[['raw_East RMSE', 'proc_East RMSE']].rename(
#         columns={'raw_East RMSE': '原始', 'proc_East RMSE': '处理后'}),
#         var_name='组别', value_name='RMSE')
#     sns.boxplot(x='组别', y='RMSE', data=plot_data)
#     plt.title('东向RMSE分布对比')
#
#     # 折线图展示变化趋势
#     plt.subplot(2, 2, 2)
#     sample_points = paired_df.sample(5, random_state=42)
#     for idx in sample_points.index:
#         plt.plot(['原始', '处理后'],
#                  [sample_points.loc[idx, 'raw_2D RMSE'],
#                   sample_points.loc[idx, 'proc_2D RMSE']],
#                  marker='o', label=f'测点 {paired_df.loc[idx, "raw_number"]}')
#     plt.title('随机测点2D RMSE处理前后对比')
#     plt.legend()
#
#     # 二维误差分布散点图
#     plt.subplot(2, 2, 3)
#     plt.scatter(paired_df['raw_East Mean'], paired_df['raw_North Mean'],
#                 alpha=0.5, label='原始')
#     plt.scatter(paired_df['proc_East Mean'], paired_df['proc_North Mean'],
#                 alpha=0.5, label='处理后')
#     plt.xlabel('东向误差均值')
#     plt.ylabel('北向误差均值')
#     plt.title('二维误差分布对比')
#     plt.legend()
#
#     # 异常值数量对比
#     plt.subplot(2, 2, 4)
#     threshold = 3  # 定义3倍标准差为异常值
#     raw_outliers = ((paired_df['raw_East Mean'] > threshold * paired_df['raw_East RMSE']) |
#                     (paired_df['raw_North Mean'] > threshold * paired_df['raw_North RMSE'])).sum()
#     proc_outliers = ((paired_df['proc_East Mean'] > threshold * paired_df['proc_East RMSE']) |
#                      (paired_df['proc_North Mean'] > threshold * paired_df['proc_North RMSE'])).sum()
#     plt.bar(['原始数据', '处理后'], [raw_outliers, proc_outliers], color=['red', 'green'])
#     plt.title(f'异常值数量对比（阈值={threshold}σ）')
#
#     plt.tight_layout()
#     plt.show()
#
#     # 输出结果
#     print("\n=== 描述性统计 ===")
#     print(pd.DataFrame(stats_results).T)
#
#     print("\n=== 统计检验结果 ===")
#     print(pd.DataFrame(test_results).T)
#
#
# # 使用示例
# analyze_positioning_data("F:\\GNSSdata\\Android GNSS data\\2025-04-15\\ALL\\error_new\\error_new_summary.xlsx")
#
