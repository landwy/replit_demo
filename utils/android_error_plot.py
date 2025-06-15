#--------------------------------------------------------android定位误差可视化------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
# 数据加载
df = pd.read_csv("F:\\GNSSdata\\Android GNSS data\\2025-04-08\\Android_position_errors.csv")

# 箱线图
plt.figure(figsize=(10, 8))
ax = sns.boxplot(data=df[["East RMSE", "North RMSE", "2D RMSE"]])

# 提取三列数据的Q1、Q2、Q3
for i, col in enumerate(["East RMSE", "North RMSE", "2D RMSE"]):
    q1 = df[col].quantile(0.25)
    q2 = df[col].quantile(0.5)
    q3 = df[col].quantile(0.75)

    # 在箱体旁边添加文本标注
    ax.text(i, q1, f"Q1={q1:.2f}", ha='center', va='bottom', fontsize=12, color='black')
    ax.text(i, q2, f"Q2={q2:.2f}", ha='center', va='bottom', fontsize=12, color='blue')
    ax.text(i, q3, f"Q3={q3:.2f}", ha='center', va='bottom', fontsize=12, color='red')

plt.ylabel("Error (m)", fontsize=20)
plt.xticks(fontsize=20)
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.tick_params(axis='both', which='major', labelsize=20)
plt.tight_layout()
plt.show()

# CDF曲线
plt.figure(figsize=(8,7))
df_sorted = df.sort_values("2D RMSE").reset_index(drop=True)
df_sorted["CDF"] = (df_sorted.index + 1) / len(df_sorted)
plt.plot(df_sorted["2D RMSE"], df_sorted["CDF"], marker=".", linestyle="-")

# 添加每个点的上下错开标注
for i in range(len(df_sorted)):
    x = df_sorted.loc[i, "2D RMSE"]
    y = df_sorted.loc[i, "CDF"]

    # 标注位置错开：奇数向上，偶数向下
    y_offset = -0.01 if i % 2 == 1 else 0.01

    plt.text(x, y + y_offset, f"({x:.2f}, {y:.2f})",
             fontsize=10, ha="center", rotation=0)

plt.xlabel("2D RMSE (m)", fontsize=20)
plt.ylabel("Cumulative Probability", fontsize=20)
#plt.title("Cumulative Distribution of 2D RMSE")
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
ax.tick_params(axis='both', which='major', labelsize=20)
plt.show()