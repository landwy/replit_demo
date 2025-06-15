#---------------------------------------------计算谷歌地球影像精度并进行可视化-----------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

import matplotlib.pyplot as plt
# 设置中文字体为黑体（SimHei），确保支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题（若有负号相关绘图需求）
plt.rcParams['axes.unicode_minus'] = False

# 坐标数据（WGS84经纬度）
rtk_points = {
    'P1': (120.2538854, 31.47293789),
    'P2': (120.253710893816, 31.4720045609211),
    'P3': (120.254441340196, 31.4719200554348),
    'P4': (120.254622549473, 31.4728645177419),
    'P2-3': (120.254158472919, 31.4719211199189)
}

ge_points = {
    'P1': (120.253889, 31.472944),
    'P2': (120.253718, 31.472019),
    'P3': (120.254441, 31.471917),
    'P4': (120.254606, 31.472845),
    'P2-3': (120.254162, 31.471930)
}

# 转换经纬度到UTM坐标系（无锡校区UTM Zone 50N）
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32650")

# 存储误差数据
errors = {
    'names': [],
    'delta_e': [],
    'delta_n': [],
    'delta_d': []
}

for name in rtk_points:
    # RTK坐标转UTM
    rtk_easting, rtk_northing = transformer.transform(
        rtk_points[name][1], rtk_points[name][0]
    )
    # GE坐标转UTM
    ge_easting, ge_northing = transformer.transform(
        ge_points[name][1], ge_points[name][0]
    )
    # 计算各向误差
    delta_e = ge_easting - rtk_easting
    delta_n = ge_northing - rtk_northing
    delta_d = np.sqrt(delta_e ** 2 + delta_n ** 2)
    print(name,f"东向误差: {delta_e:.2f} m, 北向误差: {delta_n:.2f} m, 平面误差: {delta_d:.2f} m")

    # 存储结果
    errors['names'].append(name)
    errors['delta_e'].append(delta_e)
    errors['delta_n'].append(delta_n)
    errors['delta_d'].append(delta_d)

# 统计指标
rmse_d = np.sqrt(np.mean(np.array(errors['delta_d']) ** 2))
rmse_e = np.sqrt(np.mean(np.array(errors['delta_e']) ** 2))
rmse_n = np.sqrt(np.mean(np.array(errors['delta_n']) ** 2))

# 可视化
plt.figure(figsize=(12, 8))

# 子图1：东向误差（ΔE）
plt.subplot(3, 1, 1)
plt.bar(errors['names'], errors['delta_e'], color='skyblue', edgecolor='black', label='ΔE')
plt.axhline(0, color='gray', linestyle='--')
plt.ylabel('东向误差 (m)')
plt.title('东向误差（正值为GE偏东，负值为偏西）')

# 子图2：北向误差（ΔN）
plt.subplot(3, 1, 2)
plt.bar(errors['names'], errors['delta_n'], color='lightgreen', edgecolor='black', label='ΔN')
plt.axhline(0, color='gray', linestyle='--')
plt.ylabel('北向误差 (m)')
plt.title('北向误差（正值为GE偏北，负值为偏南）')

# 子图3：平面误差（ΔD）
plt.subplot(3, 1, 3)
plt.bar(errors['names'], errors['delta_d'], color='salmon', edgecolor='black', label='ΔD')
plt.axhline(rmse_d, color='blue', linestyle='--', label=f'RMSE = {rmse_d:.2f} m')
plt.ylabel('平面误差 (m)')
plt.xlabel('测点')
plt.title('平面误差与RMSE')
plt.legend()

plt.tight_layout()
plt.show()

# 输出统计结果
print(f"东向RMSE: {rmse_e:.2f} m, 北向RMSE: {rmse_n:.2f} m, 平面RMSE: {rmse_d:.2f} m")