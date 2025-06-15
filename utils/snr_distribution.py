#--------------------------------------------手机采集的数据SNR分布-------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt

# 读取CSV件
csv_file = 'F:\\GNSSdata\\Android GNSS data\\2025-04-08\\all_snr_output.csv'
df = pd.read_csv(csv_file)

# 排除SNR为0的数据
df = df[df['SNR'] > 0]
df['SNR'] = df['SNR']/1000
# # 折线图
# plt.figure(figsize=(10, 4))
# plt.plot(df['Index'], df['SNR'], color='blue', linewidth=1)
# plt.title('SNR Trend (SNR > 0)')
# plt.xlabel('Index')
# plt.ylabel('SNR (dB-Hz)')
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# 直方图，观察SNR分布情况
plt.figure(figsize=(6, 4))
plt.hist(df['SNR'], bins=30, color='skyblue', edgecolor='black')
plt.title('SNR Distribution ')
plt.xlabel('SNR (dB-Hz)')
plt.ylabel('Count')
plt.axvline(df['SNR'].mean(), color='red', linestyle='--', label=f'Mean = {df["SNR"].mean():.2f}')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
