import pandas as pd
import pandas as pd

def calculate_classification_metrics(csv_path, snr_col, los_col, threshold=29):
    """计算LOS/NLOS分类性能指标（F1分数、宏平均和加权平均）"""
    # 读取数据
    df = pd.read_csv(csv_path)
    print(f"[DEBUG] 当前使用阈值: {threshold}")

    # 生成预测结果
    df['Predicted_LOS'] = (df[snr_col] > threshold).astype(int)

    # 混淆矩阵四要素
    TP = ((df[los_col] == 1) & (df['Predicted_LOS'] == 1)).sum()
    FP = ((df[los_col] == 0) & (df['Predicted_LOS'] == 1)).sum()
    FN = ((df[los_col] == 1) & (df['Predicted_LOS'] == 0)).sum()
    TN = ((df[los_col] == 0) & (df['Predicted_LOS'] == 0)).sum()

    total = len(df)
    support_LOS = (df[los_col] == 1).sum()
    support_NLOS = (df[los_col] == 0).sum()

    # LOS 指标
    LOS_precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    LOS_recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    LOS_f1 = 2 * LOS_precision * LOS_recall / (LOS_precision + LOS_recall) if (LOS_precision + LOS_recall) > 0 else 0

    # NLOS 指标
    NLOS_precision = TN / (TN + FN) if (TN + FN) > 0 else 0
    NLOS_recall = TN / (TN + FP) if (TN + FP) > 0 else 0
    NLOS_f1 = 2 * NLOS_precision * NLOS_recall / (NLOS_precision + NLOS_recall) if (NLOS_precision + NLOS_recall) > 0 else 0

    accuracy = (TP + TN) / total

    # 宏平均
    macro_precision = (LOS_precision + NLOS_precision) / 2
    macro_recall = (LOS_recall + NLOS_recall) / 2
    macro_f1 = (LOS_f1 + NLOS_f1) / 2

    # 加权平均
    weighted_precision = (LOS_precision * support_LOS + NLOS_precision * support_NLOS) / total
    weighted_recall = (LOS_recall * support_LOS + NLOS_recall * support_NLOS) / total
    weighted_f1 = (LOS_f1 * support_LOS + NLOS_f1 * support_NLOS) / total

    # 打印分类报告
    print(f"\n阈值 {threshold} 分类性能评估:")
    print(f"| {'指标':<10} | {'LOS':<8} | {'NLOS':<8} |")
    print("|------------|----------|----------|")
    print(f"| 精确率     | {LOS_precision:.2%} | {NLOS_precision:.2%} |")
    print(f"| 召回率     | {LOS_recall:.2%} | {NLOS_recall:.2%} |")
    print(f"| F1 分数    | {LOS_f1:.2%} | {NLOS_f1:.2%} |")
    print("|------------|-----------------------------|")
    print(f"| 宏平均     | 精确率: {macro_precision:.2%}，召回率: {macro_recall:.2%}，F1: {macro_f1:.2%}")
    print(f"| 加权平均   | 精确率: {weighted_precision:.2%}，召回率: {weighted_recall:.2%}，F1: {weighted_f1:.2%}")
    print(f"| 准确率     | {accuracy:.2%}")

    return {
        'LOS': {
            'precision': LOS_precision,
            'recall': LOS_recall,
            'f1_score': LOS_f1,
            'support': support_LOS
        },
        'NLOS': {
            'precision': NLOS_precision,
            'recall': NLOS_recall,
            'f1_score': NLOS_f1,
            'support': support_NLOS
        },
        'accuracy': accuracy,
        'macro_avg': {
            'precision': macro_precision,
            'recall': macro_recall,
            'f1_score': macro_f1
        },
        'weighted_avg': {
            'precision': weighted_precision,
            'recall': weighted_recall,
            'f1_score': weighted_f1
        }
    }


# 使用示例
if __name__ == "__main__":
    metrics = calculate_classification_metrics(
        csv_path='F:\\GNSSdata\\rf_train\\new\\gps_bds_with_los_filtered.csv',
        snr_col='snr',
        los_col='LOS',
        threshold=30
    )