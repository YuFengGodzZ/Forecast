import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler

# 获取当前工作目录
current_dir = os.getcwd()

# 构建 CSV 文件路径（假设 CSV 文件在同一目录下）
csv_filename = "IC-V_curves/q.csv"
csv_path = os.path.join(current_dir, csv_filename)

# 从 CSV 文件中读取数据
data = pd.read_csv(csv_path)

# 初始化变量
Peak_Feature_Charge = data["Peak Feature Charge"].values
Total_Capacity = data["Total Capacity"].values

# 数据标准化
scaler = StandardScaler()
Peak_Feature_Charge_scaled = scaler.fit_transform(Peak_Feature_Charge.reshape(-1, 1))

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    Peak_Feature_Charge_scaled, Total_Capacity, test_size=0.2, random_state=42)

# 使用GridSearchCV优化KNN参数
param_grid = {
    'n_neighbors': list(range(1, 21)),
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean', 'manhattan']
}

knn = KNeighborsRegressor()
grid_search = GridSearchCV(knn, param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search.fit(X_train, y_train)

best_knn = grid_search.best_estimator_
print(f"最佳KNN参数: {grid_search.best_params_}")

# 使用最佳模型进行预测
y_pred = best_knn.predict(X_test)

# 计算评估指标
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"测试集均方误差 (MSE): {mse:.4f}")
print(f"测试集决定系数 (R²): {r2:.4f}")

# 绘制结果
plt.figure(figsize=(10, 6))
plt.scatter(X_test, y_test, color='blue', label='Actual Data')
plt.scatter(X_test, y_pred, color='red', label='Predicted Data', alpha=0.5)
plt.xlabel('Standardized Peak Feature Charge')
plt.ylabel('Total Capacity')
plt.title('KNN Regression Results')
plt.legend()
plt.show()

# 绘制平滑曲线
x_range = np.linspace(X_train.min(), X_train.max(), 500).reshape(-1, 1)
y_range = best_knn.predict(x_range)

plt.figure(figsize=(10, 6))
plt.scatter(X_train, y_train, color='blue', label='Training Data')
plt.plot(x_range, y_range, color='red', linewidth=2, label='KNN Regression Curve')
plt.xlabel('Standardized Peak Feature Charge')
plt.ylabel('Total Capacity')
plt.title('KNN Regression Curve')
plt.legend()
plt.show()

# 添加用户交互功能
while True:
    try:
        choice = input("请输入选项（1: 预测，2: 退出）：")
        if choice.lower() == '2':
            break

        if choice == '1':
            user_input = input("请输入一个Peak Feature Charge值进行预测：")
            user_input = float(user_input)
            user_input_scaled = scaler.transform(np.array([[user_input]]))
            predicted_capacity = best_knn.predict(user_input_scaled)
            print(f"预测的Total Capacity值为：{predicted_capacity[0]:.2f}")

        else:
            print("无效选项，请输入1或2。")

    except ValueError:
        print("输入无效，请输入有效的选项或数字。")