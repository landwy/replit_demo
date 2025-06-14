


#-------------------------------------------------模型训练-----------------------------------------------------------\
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import make_pipeline

# 1. 数据加载与预处理------------------------------------------------------------------------------------------------------
def load_data(file_path):
    df = pd.read_csv(file_path)

    # 处理卫星系统类别（例如G=GPS，C=北斗）
    #df['constellation'] = df['satellite'].str[0].map({'G': 0, 'C': 1, 'R': 2, 'E': 3, 'J': 4})

    # 添加 SNR/仰角比值特征
    df['snr_ratio'] = df['snr'] / (df['el'] + 1e-5)  # 避免除0
    #df['sr_ratio'] = df['snr'] / (df['normalized_resp'] + 1e-5)

    # 选择特征
    X = df[['el', 'snr', 'norm_resp']]
    y = df['LOS']

    return X, y


# 2. 数据分割------------------------------------------------------------------------------------------------------------
def split_data(X, y, test_size=0.3, random_state=42):
    return train_test_split(X, y,
                            test_size=test_size,
                            stratify=y,  # 保持类别比例
                            random_state=random_state)


# 3. 模型训练------------------------------------------------------------------------------------------------------------
#----------------超参数优化---------------------
# def train_model(X_train, y_train):
#     param_grid = {
#         'n_estimators': [100, 200, 300],
#         'max_depth': [6, 8, 10],
#         'min_samples_split': [2, 5, 10],
#         'min_samples_leaf': [1, 2, 4]
#     }
#
#     rf = RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1)
#
#     grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='f1_weighted', verbose=2)
#     grid_search.fit(X_train, y_train)
#
#     print("最佳参数:", grid_search.best_params_)
#     return grid_search.best_estimator_


#----------------使用 XGBoost 替换随机森林--------------
def train_model(X_train, y_train):
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.2,
        scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])*1.7,  # 处理类别不均衡
        random_state=42,

    )
    model.fit(X_train, y_train)
    return model

# def train_model(X_train, y_train):
#     param_grid = {
#         'n_estimators': [100, 200, 300],     # 树的数量
#         'max_depth': [4, 6, 8],              # 树的最大深度
#         'learning_rate': [0.01, 0.05, 0.1],  # 学习率
#         'min_child_weight': [1, 3, 5],       # 控制叶子节点的最小样本权重
#         'subsample': [0.7, 0.8, 1.0],        # 训练样本采样比例
#         'colsample_bytree': [0.7, 0.8, 1.0]  # 每棵树使用的特征比例
#     }
#
#     xgb = XGBClassifier(
#         objective='binary:logistic',
#         scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1]),  # 处理类别不平衡
#         random_state=42
#     )
#
#     grid_search = GridSearchCV(xgb, param_grid, cv=3, scoring='f1_weighted', verbose=2, n_jobs=-1)
#     grid_search.fit(X_train, y_train)
#
#     print("最佳参数:", grid_search.best_params_)
#     return grid_search.best_estimator_




# def train_model(X_train, y_train):
#     model = RandomForestClassifier(
#         n_estimators=200,
#         max_depth=8,
#         class_weight='balanced',  # 处理类别不平衡
#         random_state=42,
#         n_jobs=-1  # 使用所有CPU核心
#     )
#     model.fit(X_train, y_train)
#     return model


# 4. 模型评估-------------------------------------------------------------------------------------------------------------
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    # 计算准确度
    accuracy = accuracy_score(y_test, y_pred)

    # 打印评估指标
    print(f"准确度: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['NLOS', 'LOS'], digits=4))

    # 混淆矩阵可视化
    cm = confusion_matrix(y_test, y_pred)
    print("混淆矩阵的具体值：")
    print(cm)

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix (Accuracy: {accuracy:.2%})', fontsize = 16)  # 在标题中显示准确度
    plt.colorbar()
    tick_marks = [0, 1]
    plt.xticks(tick_marks, ['NLOS', 'LOS'])
    plt.yticks(tick_marks, ['NLOS', 'LOS'])
    plt.ylabel('True label', fontsize=15)
    plt.xlabel('Predicted label',fontsize=15)
    plt.savefig("F:\\大论文\\图片\\论文图片\\Confusion Matrix.png", dpi=300, bbox_inches='tight')
    plt.show()

    # return accuracy  # 可选：返回准确度供后续使用

# 5. 特征重要性分析-------------------------------------------------------------------------------------------------------
# def plot_feature_importance(model, X):
#     import matplotlib as mpl
#
#     # 获取特征重要性数据
#     features = X.columns
#     importances = model.feature_importances_
#     result = permutation_importance(model, X, y, n_repeats=10, random_state=42)
#     sorted_idx = result.importances_mean.argsort()[::-1]
#
#     # 绘图
#     plt.figure(figsize=(10, 4))
#
#     # Gini重要性
#     plt.subplot(1, 2, 1)
#     plt.barh(range(len(features)), importances[sorted_idx], align='center')
#     plt.yticks(range(len(features)), features[sorted_idx])
#     plt.title("Feature Importance (Gini)")
#
#     # 排列重要性
#     plt.subplot(1, 2, 2)
#
#     # Matplotlib版本兼容处理
#     mpl_version = int(mpl.__version__.split('.')[0])
#     boxplot_args = {
#         'x': result.importances[sorted_idx].T,
#         'vert': False,
#         'tick_labels' if mpl_version >= 3 else 'labels': features[sorted_idx]
#     }
#     plt.boxplot(**boxplot_args)
#     plt.title("Permutation Importance")
#
#     plt.tight_layout()
#     plt.show()


def plot_feature_importance(model, X):
    import matplotlib as mpl
    import xgboost as xgb

    features = X.columns

    # 使用 XGBoost 提供的 get_booster().get_score() 方法，获取 gain / weight / cover
    booster = model.get_booster()
    importance_types = ['weight', 'gain', 'cover']

    # plt.figure(figsize=(16, 4))
    #
    # for i, importance_type in enumerate(importance_types):
    #     importance_dict = booster.get_score(importance_type=importance_type)
    #     # 将 dict 转为与列顺序一致的 list
    #     importances = [importance_dict.get(f, 0) for f in features]
    #
    #     plt.subplot(1, 3, i + 1)
    #     plt.barh(features, importances)
    #     plt.title(f"Importance ({importance_type})", fontsize=18)
    #     plt.ylabel("Score", fontsize=18)
    #     plt.xticks(fontsize=16)
    #     plt.yticks(fontsize=16)
    #     plt.tight_layout()

    plt.figure(figsize=(15, 12))  # 竖排时宽度小、高度大

    for i, importance_type in enumerate(importance_types):
        importance_dict = booster.get_score(importance_type=importance_type)
        importances = [importance_dict.get(f, 0) for f in features]

        plt.subplot(3, 1, i + 1)  # 改为3行1列的子图排布
        plt.barh(features, importances)
        plt.title(f"Importance ({importance_type})", fontsize=32)
        plt.ylabel("Score", fontsize=28)
        plt.xticks(fontsize=28)
        plt.yticks(fontsize=28)
        plt.tight_layout()
    plt.subplots_adjust(hspace=0.5)  # 可调大，如 0.6、0.8
    plt.savefig("F:\\大论文\\图片\\论文图片\\importance.png", dpi=300, bbox_inches='tight')

    # 排列重要性（Permutation Importance）
    result = permutation_importance(model, X, y, n_repeats=10, random_state=42)
    sorted_idx = result.importances_mean.argsort()[::-1]

    plt.figure(figsize=(6, 5))
    plt.boxplot(
        result.importances[sorted_idx].T,
        vert=False,
        tick_labels=features[sorted_idx]
    )
    plt.title("Permutation Importance", fontsize=16)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.tight_layout()
    plt.savefig("F:\\大论文\\图片\\论文图片\\Permutation_Importance.png", dpi=300, bbox_inches='tight')
    plt.show()



# 主程序流程
if __name__ == "__main__":
    # 数据路径
    csv_path = "F:\\GNSSdata\\rf_train\\new\\gps_bds_with_los_filtered.csv"

    # 加载数据
    X, y = load_data(csv_path)

    # 数据分割
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 训练模型
    model = train_model(X_train, y_train)

    # 评估模型
    evaluate_model(model, X_test, y_test)

    # 特征分析
    plot_feature_importance(model, X)

    # 保存模型
    joblib.dump(model, '..//los_classifier_rf.pkl')

    # 示例预测
    sample_data = pd.DataFrame(
        [[50, 38.5, 0.3],  # elevation(rad), SNR, constellation
         [24, 24.3, 0.7]],
        columns=['el', 'snr',  'norm_resp']
    )
    print("Sample predictions:", model.predict(sample_data))
