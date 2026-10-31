# scatter_trio.py —— s / c / cmap 三件套 + 两个系列
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt

random.seed(42)

x = list(range(30))
y = [i * i + random.randint(-20, 20) for i in x]

plt.style.use("seaborn-v0_8")

# ===== 1. 三件套同时上场 =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x, y,
           s=[i * 8 + 20 for i in x],     # 点大小随 x 递增
           c=y, cmap=plt.cm.Blues,        # 颜色由 y 决定 + Blues 渐变
           edgecolors="gray")             # 灰边让密集的点分得开
ax.set_title("散点图三件套：s / c / cmap")
fig.savefig("trio_三件套.png", dpi=100, bbox_inches="tight")

# ===== 2. 两个系列：偶数下标红色、奇数下标蓝色 =====
even = [(xi, yi) for i, (xi, yi) in enumerate(zip(x, y)) if i % 2 == 0]
odd = [(xi, yi) for i, (xi, yi) in enumerate(zip(x, y)) if i % 2 == 1]

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter([p[0] for p in even], [p[1] for p in even],
           s=70, c="red", label="偶数下标", alpha=0.7)
ax.scatter([p[0] for p in odd], [p[1] for p in odd],
           s=70, c="blue", label="奇数下标", alpha=0.7)
ax.set_title("两个系列一起画：靠 label + legend() 出图例")
ax.set_facecolor("#f0f0f0")            # 坐标区底色调浅灰，散点更跳
ax.legend()
fig.savefig("trio_两个系列.png", dpi=100, bbox_inches="tight")
print("两张图都已保存")
