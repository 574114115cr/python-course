# walk_compare.py —— 三种步长对照，一行三张图
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    def __init__(self, num_points=2000, step_size=1):
        self.num_points = num_points
        self.step_size = step_size          # 新属性：一步走几格
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step = random.choice([-1, 0, 1]) * self.step_size
            y_step = random.choice([-1, 0, 1]) * self.step_size
            if x_step == 0 and y_step == 0:
                continue
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)


plt.style.use("seaborn-v0_8")
random.seed(42)

step_sizes = [1, 2, 3]
num_walks = 100
num_points = 2000

# ★ plt.subplots(1, 3) 返回 1 个 figure + 3 个 ax，参数是行数、列数
fig, axes = plt.subplots(1, 3, figsize=(19, 5))

for index, step_size in enumerate(step_sizes):
    ax = axes[index]                       # 逐个取出坐标轴对象
    for i in range(num_walks):
        walk = RandomWalk(num_points, step_size)
        walk.fill_walk()
        # c 必须是和点等长的列表，所以写成 [i] * len(...) 这样的列表
        ax.scatter(walk.x_values, walk.y_values, s=1,
                   c=[i] * len(walk.x_values), cmap=plt.cm.Blues,
                   alpha=0.1, edgecolors="none")
    ax.set_title(f"步长 = {step_size}", fontsize=14)
    ax.axis([0, num_points * step_size * 1.05, 0, num_points * step_size * 1.05])

fig.suptitle(f"三种步长对比：每张图 {num_walks} 次游走 × {num_points} 步", fontsize=16)
fig.tight_layout()                          # 自动排版，标题和图不重叠
fig.savefig("walk_三组对比.png", dpi=120, bbox_inches="tight")
print("已保存 walk_三组对比.png：步长越大，游走范围越大")
