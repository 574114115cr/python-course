# random_walk_demo.py —— 教材 RandomWalk 类：单次轨迹 + 500 次叠加
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    """模拟一只小虫的随机游走：每一步往四个方向之一移动一格。"""

    def __init__(self, num_points=5000):
        self.num_points = num_points       # 走多少步
        self.x_values = [0]                # 属性：位置列表，从原点出发
        self.y_values = [0]

    def step(self):
        """走一步，然后在列表末尾追加新位置。"""
        x_step = random.choice([-1, 0, 1])
        y_step = random.choice([-1, 0, 1])
        # ★ and 不是 or：只有"横竖都不动"才重来
        if x_step == 0 and y_step == 0:
            return False
        self.x_values.append(self.x_values[-1] + x_step)
        self.y_values.append(self.y_values[-1] + y_step)
        return True

    def fill_walk(self):
        """反复调用 step，直到攒够 num_points 个点。"""
        while len(self.x_values) < self.num_points:
            self.step()


plt.style.use("seaborn-v0_8")
random.seed(42)        # 固定种子：每次运行结果一样，bug 可复现

# ===== 1. 画一次游走：连线 + 标出终点 =====
walk = RandomWalk(1000)
walk.fill_walk()
print("点数:", len(walk.x_values), " 终点:", walk.x_values[-1], walk.y_values[-1])

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(walk.x_values, walk.y_values, linewidth=1, color="royalblue")   # 连线看轨迹
ax.scatter(walk.x_values[-1], walk.y_values[-1], s=120, c="red", label="终点")
ax.set_title("一次随机游走（1000 步）")
ax.legend()
ax.axis([0, 1000 * 1.05, 0, 1000 * 1.05])       # 校正绘图：留边距
fig.savefig("random_walk_一次.png", dpi=120, bbox_inches="tight")

# ===== 自检：拒绝原地不动之后，实际步数必须刚好等于 num_points =====
assert len(walk.x_values) == 1000, f"点数不对：{len(walk.x_values)}"
print("自检通过：没有原地踏步的浪费")

# ===== 2. 模拟 500 次游走并设置样式 =====
num_walks, num_points = 500, 5000
fig, ax = plt.subplots(figsize=(12, 8))
for i in range(num_walks):
    w = RandomWalk(num_points)
    w.fill_walk()
    # 用「第几次游走」当颜色值：先画的淡、后画的深，形成历史层次
    # 注意 c 必须和点一样长，所以写成 [i] * len(...) 这样的列表
    ax.scatter(w.x_values, w.y_values, s=1,
               c=[i] * len(w.x_values), cmap=plt.cm.Blues,
               alpha=0.1, edgecolors="none")

ax.set_title(f"{num_walks} 次随机游走（每次 {num_points} 步）", fontsize=16)
ax.axis([0, num_points * 1.05, 0, num_points * 1.05])
fig.savefig("random_walk_500.png", dpi=150, bbox_inches="tight")
print("两张图都已保存")
