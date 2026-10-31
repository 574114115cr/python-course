# axis_fix_demo.py —— ax.axis([xmin, xmax, ymin, ymax]) 留边距
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

# ===== 1. 造数据：100 个点，最大值正好是 1100 / 1_100_000 =====
x_values = list(range(1, 101))
y_values = [x * 11000 for x in x_values]        # 100 * 11000 = 1_100_000

# ===== 2. 不校正：最左最右的点会被边框削掉 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.set_title("没有校正：边上的点被切了")
fig.savefig("axis_1_没校正.png", dpi=100, bbox_inches="tight")

# ===== 3. 校正：手工指定四个边界，多留 5% 余量 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.set_title("校正之后：四周有留白，点是完整的")
ax.axis([0, 1100, 0, 1_100_000])   # 顺序是 [xmin, xmax, ymin, ymax]
fig.savefig("axis_2_校正.png", dpi=100, bbox_inches="tight")

# ===== 4. 让代码自己算余量，并定制刻度 =====
x_max, y_max = max(x_values), max(y_values)
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.axis([0, x_max * 1.05, 0, y_max * 1.05])
ax.set_xticks(list(range(0, 101, 10)))           # 刻度位置
ax.set_xticklabels([str(v) for v in range(0, 101, 10)])   # 刻度文字
ax.set_yticks(list(range(0, 1_100_001, 200_000)))
ax.set_yticklabels([f"{v:,}" for v in range(0, 1_100_001, 200_000)])
ax.set_title("自动边距 + 定制刻度", fontsize=16)
fig.savefig("axis_3_自动边距.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
