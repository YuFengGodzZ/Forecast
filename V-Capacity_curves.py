import pandas as pd
import os
import matplotlib.pyplot as plt
import random

processed_excel_path = 'processed_data'  # 保留电流电压信息的excel文件的文件夹
output_base_folder_iv = 'V-Capacity_curves'      # 输出图像的文件夹
pngnumber = 10                           # 你想输出的I-V曲线图的数量

def generate_iv_curves():
    # 确保输出文件夹存在
    if not os.path.exists(output_base_folder_iv):
        os.makedirs(output_base_folder_iv)

    # 遍历主文件夹下的每个子文件夹
    for root, dirs, files in os.walk(processed_excel_path):
        # 筛选出xlsx文件
        xlsx_files = [f for f in files if f.endswith('.xlsx')]

        # 随机选择10个文件，如果文件数量少于10，则选择所有文件
        selected_files = random.sample(xlsx_files, min(pngnumber, len(xlsx_files)))

        # 处理每个选中的文件
        for selected_file in selected_files:
            file_path = os.path.join(root, selected_file)
            # 读取Excel文件
            df = pd.read_excel(file_path)

            # 只保留恒流充电阶段的数据
            df_cc = df[df['状态'] == '恒流充电']

            # 绘制电压-容量图
            plt.figure(figsize=(10, 5))
            plt.plot(df_cc['容量(mAh)'], df_cc['电压(V)'], label='Voltage and Capacity ')

            plt.title(f'Voltage and Capacity for {selected_file}')
            plt.xlabel('Capacity (mAh)')
            plt.ylabel('Voltage (V)')
            plt.legend()

            # 保存图形
            output_filename = f"{os.path.splitext(selected_file)[0]}_cc.png"
            output_path = os.path.join(output_base_folder_iv, output_filename)
            plt.savefig(output_path)
            plt.close()

# 调用函数
generate_iv_curves()