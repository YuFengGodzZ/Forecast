import pandas as pd
import os
import math
import matplotlib.pyplot as plt
import csv
import numpy as np
import random

# 指定文件夹路径
folder_path = 'processed_data'  # 替换为你的Excel文件所在的文件夹路径
output_base_folder = 'IC-V_curves'

# 确保输出文件夹存在
if not os.path.exists(output_base_folder):
    os.makedirs(output_base_folder)

# 初始化所有文件的特征电量和总容量列表
all_peak_features = []
all_total_capacities = []

# 获取所有xlsx文件
all_xlsx_files = []
for root, dirs, files in os.walk(folder_path):
    xlsx_files = [f for f in files if f.endswith('.xlsx')]
    all_xlsx_files.extend([(os.path.join(root, f), f) for f in xlsx_files])

# 随机选择10个文件用于生成IC-V折线图
if len(all_xlsx_files) >= 10:
    selected_files = random.sample(all_xlsx_files, 10)
else:
    selected_files = all_xlsx_files

# 处理所有文件，只对选中的10个文件生成图表，其余文件只保存数据到CSV
for file_info in all_xlsx_files:
    file_path, selected_file = file_info
    # 读取Excel文件
    df = pd.read_excel(file_path)

    # 提取电压和电流列
    voltages = df['电压(V)'].dropna().to_numpy()
    currents = df['电流(mA)'].dropna().to_numpy()

    # 取电流列第一个值向上取整作为该文件的恒定电流
    IC = math.ceil(currents[0]) / 1000  # 将mA转换为A

    # 初始化区间数据字典
    interval_voltages = []
    interval_ic_values = []

    # 按每5mV为小区间统计数据点数量
    interval = 0.005  # 5mV
    current_voltage = voltages[0]
    count = 1

    for i in range(1, len(voltages)):
        if (voltages[i] - current_voltage) >= interval:
            # 如果当前电压值与区间起始电压的差值达到或超过5mV，则保存当前区间的数据
            interval_voltages.append(current_voltage)
            interval_ic_values.append(IC * count / 3600)
            current_voltage = voltages[i]
            count = 1
        else:
            count += 1

    # 将数据转换为numpy数组以便处理
    interval_voltages = np.array(interval_voltages)
    interval_ic_values = np.array(interval_ic_values)

    # 使用文件名作为总容量
    file_basename = os.path.splitext(selected_file)[0]
    total_capacity = file_basename  # 直接使用文件名（不包含扩展名）作为总容量

    # 寻找3.2V到3.4V之间的电压范围
    target_start = 3.2
    target_end = 3.4

    # 找到3.2V到3.4V之间的索引范围
    start_index = np.searchsorted(interval_voltages, target_start)
    end_index = np.searchsorted(interval_voltages, target_end)

    # 确保索引范围有效
    if start_index >= len(interval_voltages) or end_index < 0:
        print(f"Voltage range {target_start}-{target_end} not found in {selected_file}")
        continue

    # 提取目标电压范围内的电压和IC值
    target_voltages = interval_voltages[start_index:end_index]
    target_ic_values = interval_ic_values[start_index:end_index]

    # 计算特征电量（积分IC值）
    feature_charge = np.trapz(target_ic_values, target_voltages)

    # 将当前文件的特征电量和总容量添加到列表
    all_peak_features.append(feature_charge)
    all_total_capacities.append(total_capacity)

    # 只对选中的10个文件生成IC-V折线图
    if file_info in selected_files:
        # 创建基于文件名的子文件夹
        output_subfolder = os.path.join(output_base_folder, file_basename)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        # 绘制IC-V曲线
        plt.figure(figsize=(10, 5))
        plt.plot(interval_voltages, interval_ic_values, label=f'Constant current={IC:.3f}A')

        # 标注3.2V到3.4V之间的区域
        plt.axvspan(target_start, target_end, color='yellow', alpha=0.3, label=f'Target Region ({target_start}-{target_end}V)')

        plt.xlabel('Voltage (V)')
        plt.ylabel('IC (Ah/V)')
        plt.title(f'IC-V Curve for {selected_file}')
        plt.legend()
        plt.grid(True)

        # 保存图形
        output_filename = f"{file_basename}.png"
        output_path = os.path.join(output_subfolder, output_filename)
        plt.savefig(output_path)
        plt.close()

# 创建一个包含所有文件的特征电量和总容量的CSV文件
all_data_path = os.path.join(output_base_folder, 'peak_features_and_capacities.csv')
with open(all_data_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Peak Feature Charge', 'Total Capacity'])
    for peak_feature, total_capacity in zip(all_peak_features, all_total_capacities):
        writer.writerow([peak_feature, total_capacity])

print(f"所选10个IC-V曲线已生成并保存到 '{output_base_folder}' 文件夹及其子文件夹中。")
print(f"所有文件的特征电量和总容量数据已保存到 '{all_data_path}' 中。")