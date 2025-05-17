import os
import pandas as pd


def delete_files_without_keyword(folder_path, keyword="恒压充电"):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xlsx"):
                file_path = os.path.join(root, file)
                keyword_found = False

                try:
                    # 读取Excel文件
                    df = pd.read_excel(file_path)
                    # 检查第二列是否存在
                    if len(df.columns) >= 2:
                        second_column = df.iloc[:, 1]
                        # 检查第二列是否包含关键字
                        if keyword in second_column.astype(str).values:
                            keyword_found = True
                except Exception as e:
                    print(f"处理文件 {file} 失败，错误信息: {e}")
                    continue

                if not keyword_found:
                    try:
                        os.remove(file_path)
                        print(f"已删除不包含关键字的文件: {file}")
                    except Exception as e:
                        print(f"删除文件 {file} 失败，错误信息: {e}")


if __name__ == "__main__":
    target_folder = input("请输入目标文件夹路径: ")
    delete_files_without_keyword(target_folder)
    print("操作完成。")