# scatter_demo.py —— s= / c= / cmap= 三件套
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

x_values = [1, 2, 3, 4, 5]
y_values = [1, 4, 9, 16, 25]

# ===== 1. 基础散点图：位置 = 两个列表 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=100)                 # s=100：点大小
fig.savefig("scatter_1_基础.png", dpi=100, bbox_inches="tight")

# ===== 2. 三件套同时上场 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values,
           s=[v * 30 for v in x_values],                # 点大小随 x 变化
           c=y_values,                                  # 颜色由 y 值决定
           cmap=plt.cm.Blues,                           # Blues 这套渐变色
           edgecolors="gray")                           # 灰边让点更清楚
fig.savefig("scatter_2_三件套.png", dpi=100, bbox_inches="tight")

# ===== 3. 绘制一系列点：传颜色名字 = 分类上色 =====
years = list(range(2010, 2021))
program_a = [10, 18, 26, 35, 47, 58, 70, 82, 95, 105, 118]   # 增长快
program_b = [10, 12, 15, 18, 21, 23, 26, 28, 30, 33, 35]    # 增长慢

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(years, program_a, s=60, c="red", label="方案 A", alpha=0.7)
ax.scatter(years, program_b, s=60, c="blue", label="方案 B", alpha=0.7)
ax.set_title("两个方案的用户增长对比")
ax.set_xlabel("年份")
ax.set_ylabel("用户数（万）")
ax.legend()                                            # 图例靠 label 自动生成
fig.savefig("scatter_3_两个系列.png", dpi=100, bbox_inches="tight")
print("三张散点图都已保存")
