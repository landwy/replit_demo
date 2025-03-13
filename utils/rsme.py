import pandas as pd
import numpy as np

# 读取CSV文件
def read_csv_file(file_path):
    data = pd.read_csv(file_path)
    return data

# 计算误差
def calculate_errors(data, Xr, Yr, Zr):
    # 提取计算出的X, Y, Z坐标
    X = data.iloc[:, 2].values
    Y = data.iloc[:, 3].values
    Z = data.iloc[:, 4].values

    # 计算三维误差
    errors_3d = np.sqrt((X - Xr)**2 + (Y - Yr)**2 + (Z - Zr)**2)

    # 计算平面误差（仅考虑XY平面）
    errors_2d = np.sqrt((X - Xr)**2 + (Y - Yr)**2)

    # 计算均方根误差（RMSE）
    rmse_3d = np.sqrt(np.mean(errors_3d**2))
    rmse_2d = np.sqrt(np.mean(errors_2d**2))

    # 计算最小误差和最大误差
    min_error_3d = np.min(errors_3d)
    max_error_3d = np.max(errors_3d)
    min_error_2d = np.min(errors_2d)
    max_error_2d = np.max(errors_2d)

    return rmse_3d, rmse_2d, min_error_3d, max_error_3d, min_error_2d, max_error_2d

# 主函数
def main():
    file_path = 'F:\SatelliteShadowTracker\SatelliteShadowTracker\shadow_matching_results1.csv'  # 替换为你的CSV文件路径
    Xr = -2743908.236550865  # 替换为真实的X坐标
    Yr = 4701333.74960222  # 替换为真实的Y坐标
    Zr = 3312892.1832351903  # 替换为真实的Z坐标

    # 读取CSV文件
    data = read_csv_file(file_path)

    # 计算误差
    rmse_3d, rmse_2d, min_error_3d, max_error_3d, min_error_2d, max_error_2d = calculate_errors(data, Xr, Yr, Zr)

    # 输出结果
    print(f"三维均方根误差 (RMSE): {rmse_3d}")
    print(f"平面均方根误差 (RMSE): {rmse_2d}")
    print(f"三维最小误差: {min_error_3d}")
    print(f"三维最大误差: {max_error_3d}")
    print(f"平面最小误差: {min_error_2d}")
    print(f"平面最大误差: {max_error_2d}")

if __name__ == "__main__":
    main()