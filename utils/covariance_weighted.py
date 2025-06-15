# import numpy as np
# from scipy.linalg import block_diag
#
# def covariance_fusion(lat, lon, alt,
#                       pseudo_cov_ecef,
#                       shadow_scores):
#     """
#     协方差加权融合定位函数
#     参数：
#     lat/lon/alt - 伪距单点定位的经纬高（度，米）
#     pseudo_cov_ecef - 伪距定位的ECEF协方差矩阵 (3x3)
#     pseudo_pos_ecef - 伪距定位的ECEF坐标 (x, y, z)
#     shadow_scores - 阴影匹配候选点列表 [(score, enu_point), ...]
#
#     返回：
#     fused_enu - 融合后的ENU坐标 (东, 北, 天)
#     """
#     # ========== 1. 转换伪距定位协方差到ENU系 ==========
#     # 构建ECEF到ENU的旋转矩阵
#     lat_rad = np.deg2rad(lat)
#     lon_rad = np.deg2rad(lon)
#
#     R = np.array([
#         [-np.sin(lon_rad), np.cos(lon_rad), 0],
#         [-np.sin(lat_rad) * np.cos(lon_rad), -np.sin(lat_rad) * np.sin(lon_rad), np.cos(lat_rad)],
#         [np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)]
#     ])
#
#     # 转换协方差矩阵
#     pseudo_cov_enu = R @ pseudo_cov_ecef @ R.T
#
#     # 提取协方差矩东-北分量 (忽略高程)
#     en_cov_gnss = pseudo_cov_enu[:2, :2]
#
#     # ========== 2. 计算阴影匹配的协方差 ==========
#     scores = np.array([s[0] for s in shadow_scores])
#     points = np.array([s[1] for s in shadow_scores])
#
#     # 归一化权重
#     weights = scores / np.sum(scores)
#
#     # 计算加权均值
#     mean_enu = np.average(points, axis=0, weights=weights)
#
#     # 计算加权协方差
#     diff = points - mean_enu
#     shadow_cov = np.zeros((2, 2))
#     for i in range(len(points)):
#         shadow_cov += weights[i] * np.outer(diff[i, :2], diff[i, :2])  # 仅用东-北分量
#
#     # ========== 3. 协方差加权融合 ==========
#     # 构造权重矩阵
#     W_gnss = np.linalg.inv(en_cov_gnss)
#     W_shadow = np.linalg.inv(shadow_cov)
#
#     # 构造扩展矩阵（处理三维坐标）
#     W_gnss_3d = block_diag(W_gnss, 0)  # 天顶方向不参与融合
#     W_shadow_3d = block_diag(W_shadow, 0)
#
#     # 伪距定位结果转换到ENU系（需要ECEF转ENU函数）
#     # 此处假设已有ecef_to_enu函数，实现ECEF到ENU坐标转换
#     enu_gnss = [0,0,0]
#
#     # 融合计算
#     W_total = W_gnss_3d + W_shadow_3d
#     fused_enu = np.linalg.inv(W_total) @ (
#             W_gnss_3d @ enu_gnss +
#             W_shadow_3d @ np.append(mean_enu[:2], 0)  # 阴影匹配无高程信息
#     )
#
#     return fused_enu
#


import numpy as np
from scipy.linalg import block_diag


def adjust_shadow_covariance(scores):
    # 提取候选点ENU坐标和得分
    points = np.array([s[1][:2] for s in scores])  # 东、北方向
    weights = np.array([s[0] for s in scores])
    weights /= np.sum(weights)

    # 计算加权均值和协方差
    mean = np.average(points, axis=0, weights=weights)
    cov = np.cov(points.T, aweights=weights)

    # 主成分分析
    eig_vals, eig_vecs = np.linalg.eigh(cov)
    order = eig_vals.argsort()[::-1]
    eig_vals = eig_vals[order]
    eig_vecs = eig_vecs[:, order]

    # 转换到主成分坐标系
    points_pc = (points - mean) @ eig_vecs

    # 计算各主成分方向的峰度
    excess_kurtosis = []
    for i in range(2):
        data = points_pc[:, i]
        mu = np.average(data, weights=weights)
        var = np.average((data - mu) ** 2, weights=weights)
        kurt = np.average((data - mu) ** 4, weights=weights) / var ** 2 - 3
        excess_kurtosis.append(kurt)

    # 调整主成分方差
    adjusted_eig_vals = []
    alpha = 2.0  # 调整系数
    threshold = -1.2
    for i in range(2):
        k = excess_kurtosis[i]
        if k < threshold:
            scale = 1 + alpha * (threshold - k)
            adjusted_eig_vals.append(eig_vals[i] * scale)
        else:
            adjusted_eig_vals.append(eig_vals[i])

    # 重建协方差矩阵
    adjusted_cov_pc = np.diag(adjusted_eig_vals)
    adjusted_cov_enu = eig_vecs @ adjusted_cov_pc @ eig_vecs.T

    return adjusted_cov_enu




def covariance_fusion(lat, lon, alt,
                      pseudo_cov_ecef,
                      shadow_scores,
                      epsilon=1e-6):
    """
    协方差加权融合定位函数（添加正则化项）
    """
    # ========== 1. 转换伪距定位协方差到ENU系 ==========
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)

    R = np.array([
        [-np.sin(lon_rad), np.cos(lon_rad), 0],
        [-np.sin(lat_rad) * np.cos(lon_rad), -np.sin(lat_rad) * np.sin(lon_rad), np.cos(lat_rad)],
        [np.cos(lat_rad) * np.cos(lon_rad), np.cos(lat_rad) * np.sin(lon_rad), np.sin(lat_rad)]
    ])

    pseudo_cov_enu = R @ pseudo_cov_ecef @ R.T
    en_cov_gnss = pseudo_cov_enu[:2, :2]

    # ========== 2. 计算阴影匹配协方差 ==========

    scores = np.array([s[0] for s in shadow_scores])
    points = np.array([s[1] for s in shadow_scores])
    weights = scores / np.sum(scores)
    mean_enu = np.average(points, axis=0, weights=weights)
    diff = points - mean_enu
    shadow_cov = np.sum(weights[:, None, None] * diff[:, :2, None] * diff[:, None, :2], axis=0)

    # ========== 3. 协方差矩阵正则化 ==========
    en_cov_gnss += epsilon * np.eye(2)  # GNSS协方差正则化
    shadow_cov += epsilon * np.eye(2)  # 阴影匹配协方差正则化

    # ========== 4. 权重矩阵计算与融合 ==========
    try:
        W_gnss = np.linalg.inv(en_cov_gnss)
        W_shadow = np.linalg.inv(shadow_cov)
    except np.linalg.LinAlgError:
        # 正则化后仍奇异，回退到GNSS
        return [0, 0, 0]

    W_gnss_3d = block_diag(W_gnss, 0)
    W_shadow_3d = block_diag(W_shadow, 0)
    W_total = W_gnss_3d + W_shadow_3d

    enu_gnss = [0, 0, 0]
    shadow_pos = np.append(mean_enu[:2], 0)  # 阴影匹配无高程

    try:
        fused_enu = np.linalg.inv(W_total) @ (W_gnss_3d @ enu_gnss + W_shadow_3d @ shadow_pos)
    except np.linalg.LinAlgError:
        # 最终融合矩阵奇异，回退到GNSS
        return enu_gnss

    return fused_enu

