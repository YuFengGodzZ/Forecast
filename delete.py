import pandas as pd

# 读取CSV文件
df = pd.read_csv("IC-V_curves/q.csv")  # 替换为你的CSV文件名

# 删除第一列大于0.002的行
filtered_df = df[df[df.columns[1]] <= 1200]

# 保存清理后的DataFrame到新的CSV文件
filtered_df.to_csv("q.csv", index=False)