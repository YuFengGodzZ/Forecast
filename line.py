import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

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

# 尝试不同次数的多项式拟合，并选择最佳模型
best_degree = 0
best_mse = float('inf')
best_ridge = None

for degree in range(1, 11):
    # 生成多项式特征
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    # 使用岭回归防止过拟合
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train_poly, y_train)

    # 计算预测值和评估指标
    y_pred = ridge.predict(X_test_poly)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Degree {degree} - MSE: {mse:.4f}, R²: {r2:.4f}")

    # 保存最佳模型
    if mse < best_mse:
        best_mse = mse
        best_r2 = r2
        best_degree = degree
        best_ridge = ridge
        best_X_train_poly = X_train_poly

print(f"\n最佳多项式次数: {best_degree}, 最佳MSE: {best_mse:.4f}, 最佳R²: {best_r2:.4f}")

# 使用最佳模型绘制拟合曲线
poly = PolynomialFeatures(degree=best_degree)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

y_pred = best_ridge.predict(X_test_poly)

# 绘制训练结果
plt.figure(figsize=(10, 6))
#plt.scatter(X_train, y_train, color='blue', label='Training Data')
plt.scatter(X_test, y_test, color='green', label='Test Data')
plt.scatter(X_test, y_pred, color='red', label='Predictions', alpha=0.5)
plt.xlabel('Standardized Peak Feature Charge')
plt.ylabel('Total Capacity')
plt.title('Polynomial Regression Results')
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
            user_input_poly = poly.transform(user_input_scaled)
            predicted_capacity = best_ridge.predict(user_input_poly)
            print(f"预测的Total Capacity值为：{predicted_capacity[0]:.2f}")

        else:
            print("无效选项，请输入1或2。")

    except ValueError:
        print("输入无效，请输入有效的选项或数字。")