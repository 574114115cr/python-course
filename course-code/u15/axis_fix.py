# axis_fix.py —— 校正绘图前后对比
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt

random.seed(7)

# ===== 1. 造 200 个随机点 =====
x_values = [random.uniform(0, 100) for _ in range(200)]
y_values = [random.uniform(0, 1_000_000) for _ in range(200)]
print(f"数据最大值: x={max(x_values):.1f}, y={max(y_values):.0f}")
print("所以边界设成 x:0~110、y:0~1_100_000 —— 比最大值多留约 10% 余量")

plt.style.use("seaborn-v0_8")

# ===== 2. 不校正：贴着边框的点会被切掉 =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_title("before：没有校正，边上的点被切掉")
fig.savefig("axis_before.png", dpi=100, bbox_inches="tight")

# ===== 3. 校正：ax.axis([xmin, xmax, ymin, ymax]) =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_title("after：校正过，四周留白，点是完整的")
ax.axis([0, 110, 0, 1_100_000])
fig.savefig("axis_after.png", dpi=100, bbox_inches="tight")

# ===== 4. 等价写法：set_xlim / set_ylim，名字更直白 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_xlim(0, 110)
ax.set_ylim(0, 1_100_000)
fig.savefig("axis_after_setlim.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
