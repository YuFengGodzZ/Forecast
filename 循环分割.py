import pandas as pd
import os

# 系统输入文件夹
original_path = '电池数据'
# 处理后的Excel文件存放的路径
processed_excel_path = 'processed_data'

def process_excel_detail_sheets():
    # 创建处理后的文件夹，如果不存在的话
    if not os.path.exists(processed_excel_path):
        os.makedirs(processed_excel_path)

    # 遍历原始文件夹中的文件
    for root, dirs, files in os.walk(original_path):
        for file in files:
            # 检查是否为Excel文件
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                xl = pd.ExcelFile(file_path)
                detail_sheets = [sheet_name for sheet_name in xl.sheet_names if sheet_name.startswith('Detail')]

                if detail_sheets:
                    for sheet_name in detail_sheets:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)

                        # 定义充电状态列表，包含恒流充电和恒压充电
                        charging_status = ['恒流充电', '恒压充电']

                        # 填充状态列的空值
                        df['状态'] = df['状态'].fillna('Unknown')

                        # 筛选充电相关的数据
                        charging_data = df[df['状态'].isin(charging_status)]

                        # 只保留需要的列
                        columns_to_keep = ['循环', '状态', '电压(V)', '电流(mA)', '容量(mAh)']
                        charging_data = charging_data[columns_to_keep]

                        # 按照循环进行分组
                        grouped_cycle = charging_data.groupby('循环')

                        for cycle, group in grouped_cycle:
                            # 对于每个循环，分别处理恒流充电和恒压充电的数据
                            charge_group = group[group['状态'] == '恒流充电'][columns_to_keep].reset_index(drop=True)
                            float_charge_group = group[group['状态'] == '恒压充电'][columns_to_keep].reset_index(drop=True)

                            # 计算总容量
                            max_charge_capacity = charge_group['容量(mAh)'].max() if not charge_group.empty else None
                            max_float_charge_capacity = float_charge_group['容量(mAh)'].max() if not float_charge_group.empty else None
                            total_capacity = pd.Series([max_charge_capacity, max_float_charge_capacity]).dropna().sum()
                            total_capacity = round(total_capacity, 2)  # 保留一位小数

                            # 计算恒流充电阶段电流的均值并取整
                            charge_current_mean = charge_group['电流(mA)'].mean() if not charge_group.empty else None
                            charge_current_mean_rounded = int(round(charge_current_mean)) if charge_current_mean is not None else None

                            combined_data = pd.concat([charge_group, float_charge_group], ignore_index=True)

                            # 创建新的Excel文件名，包含循环号和总容量
                            excel_filename = os.path.join(processed_excel_path, f'{total_capacity}.xlsx')

                            # 将合并后的数据写入同一个Excel文件的同一个工作表中
                            combined_data.to_excel(excel_filename, sheet_name='充电数据', index=False)

                            print(f'Data for cycle {cycle} with total capacity {total_capacity} saved to {excel_filename}')

# 调用函数
process_excel_detail_sheets()