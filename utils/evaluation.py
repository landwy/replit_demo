import pandas as pd
def calculate_classification_metrics(csv_path, snr_col, los_col, threshold=29):
    """计算基于SNR阈值的LOS/NLOS分类性能指标

    参数：
        csv_path (str): CSV文件路径
        snr_col (str): SNR数值列名
        los_col (str): 实际LOS标签列名（1=LOS，0=NLOS）
        threshold (int): SNR判断阈值

    返回：
        dict: 包含LOS/NLOS各项指标的字典
    """
    # 读取数据
    df = pd.read_csv(csv_path)
    print(f"[DEBUG] 当前使用阈值: {threshold}")

    # 生成预测结果
    df['Predicted_LOS'] = (df[snr_col] > threshold).astype(int)

    # 计算混淆矩阵要素
    # LOS类别（正类）
    TP = ((df[los_col] == 1) & (df['Predicted_LOS'] == 1)).sum()  # 真阳性
    FP = ((df[los_col] == 0) & (df['Predicted_LOS'] == 1)).sum()  # 假阳性
    FN = ((df[los_col] == 1) & (df['Predicted_LOS'] == 0)).sum()  # 假阴性

    # NLOS类别（负类）
    TN = ((df[los_col] == 0) & (df['Predicted_LOS'] == 0)).sum()  # 真阴性
    FP_NLOS = FP  # 对NLOS来说FP就是预测错误的LOS
    FN_NLOS = FN  # 对NLOS来说FN就是预测错误的NLOS

    # 计算LOS指标
    LOS_accuracy = (TP + TN) / len(df)  # 整体准确率
    LOS_precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    LOS_recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    # 计算NLOS指标
    NLOS_accuracy = (TP + TN) / len(df)  # 整体准确率相同
    NLOS_precision = TN / (TN + FN_NLOS) if (TN + FN_NLOS) > 0 else 0
    NLOS_recall = TN / (TN + FP_NLOS) if (TN + FP_NLOS) > 0 else 0

    # 格式化输出
    print(f"\n阈值 {threshold} 分类性能评估:")
    print(f"| {'指标':<10} | {'LOS':<8} | {'NLOS':<8} |")
    print("|------------|----------|----------|")
    print(f"| 准确率     | {LOS_accuracy:.2%} | {NLOS_accuracy:.2%} |")
    print(f"| 精确率     | {LOS_precision:.2%} | {NLOS_precision:.2%} |")
    print(f"| 召回率     | {LOS_recall:.2%} | {NLOS_recall:.2%} |")

    return {
        'LOS': {
            'accuracy': LOS_accuracy,
            'precision': LOS_precision,
            'recall': LOS_recall
        },
        'NLOS': {
            'accuracy': NLOS_accuracy,
            'precision': NLOS_precision,
            'recall': NLOS_recall
        }
    }

# 使用示例
if __name__ == "__main__":
    metrics = calculate_classification_metrics(
        csv_path='F:\\GNSSdata\\rf_train\\merged_snr.csv',
        snr_col='SNR',
        los_col='LOS',
        threshold=33000
    )