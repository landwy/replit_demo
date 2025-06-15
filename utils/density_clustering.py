import numpy as np
from sklearn.cluster import DBSCAN


def shadow_matching_density_clustering(scores, eps=3.0, min_samples=2, score_threshold_ratio=0.5):
    """
    基于密度聚类(DBSCAN)的阴影匹配定位结果聚合函数

    参数：
    scores : np.ndarray
        候选点数组，形状为 (N,4)，每行格式为 [score, x_ecef, y_ecef, z_ecef]
    eps : float
        DBSCAN邻域半径（单位：米），建议设置为网格分辨率的1.5-2倍
    min_samples : int
        DBSCAN最小簇点数
    score_threshold_ratio : float
        候选点分数过滤阈值（保留分数 > 最高分*该比例的点）

    返回：
    np.ndarray - 最终定位结果 (ECEF坐标) 或 None（无有效结果）
    """
    # 参数校验
    if scores.size == 0:
        return None

    # 分离分数和坐标
    point_scores = scores[:, 0]
    points_ecef = scores[:, 1:]

    # 1. 过滤低分候选点
    max_score = np.max(point_scores)
    threshold = max_score * score_threshold_ratio
    mask = point_scores >= threshold
    filtered_scores = point_scores[mask]
    filtered_points = points_ecef[mask]

    if len(filtered_scores) == 0:
        return None

    # 2. DBSCAN聚类
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(filtered_points)
    labels = db.labels_

    # 3. 统计各簇总分
    clusters = {}
    for label, score in zip(labels, filtered_scores):
        if label == -1:  # 忽略噪声点
            continue
        if label not in clusters:
            clusters[label] = {"total_score": 0.0, "points": []}
        clusters[label]["total_score"] += score
        clusters[label]["points"].append(filtered_points[labels == label])

    # 4. 结果处理
    if not clusters:
        # 无有效簇时返回最高分点
        best_idx = np.argmax(filtered_scores)
        return filtered_points[best_idx]
    else:
        # 选择总分最高的簇
        main_label = max(clusters.keys(), key=lambda k: clusters[k]["total_score"])
        main_cluster = clusters[main_label]

        # 提取簇内点和对应分数
        cluster_mask = (labels == main_label)
        cluster_points = filtered_points[cluster_mask]
        cluster_scores = filtered_scores[cluster_mask]

        # 5. 计算加权质心
        try:
            weighted_centroid = np.average(cluster_points, axis=0, weights=cluster_scores)
            return weighted_centroid
        except ZeroDivisionError:
            return np.mean(cluster_points, axis=0)