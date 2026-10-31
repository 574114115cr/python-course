# walk_reproducible.py —— random.seed() 让随机程序可复现
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    def __init__(self, num_points=2000):
        self.num_points = num_points
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step = random.choice([-1, 0, 1])
            y_step = random.choice([-1, 0, 1])
            if x_step == 0 and y_step == 0:
                continue                     # ★ and 不是 or
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)


plt.style.use("seaborn-v0_8")

# ===== 1. 不设种子：结果随机 =====
walk_a = RandomWalk(2000)
walk_a.fill_walk()
print("第一次运行终点:", (walk_a.x_values[-1], walk_a.y_values[-1]))

# ===== 2. 设种子：结果被固定 =====
random.seed(42)
walk_b = RandomWalk(2000)
walk_b.fill_walk()
print("第二次运行终点(seed 42):", (walk_b.x_values[-1], walk_b.y_values[-1]))

# ===== 3. 同一个种子跑两次，终点必须完全一样 =====
random.seed(42)
w1 = RandomWalk(2000)
w1.fill_walk()
random.seed(42)
w2 = RandomWalk(2000)
w2.fill_walk()
assert w1.x_values == w2.x_values, "同种子却给出了不同路径，seed 用法错了"
print("自检通过：random.seed(42) 之后随机序列完全可复现")

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(w1.x_values, w1.y_values, linewidth=1, color="royalblue")
ax.set_title("random.seed(42) 的随机游走")
ax.axis([0, 2000 * 1.05, 0, 2000 * 1.05])
fig.savefig("walk_reproducible.png", dpi=120, bbox_inches="tight")
