# walk_and_dice.py —— 不画图，只算数据：坐标是怎么一步步走出来的
import random
from collections import Counter


def get_step():
    """一步的方向：x、y 各自随机取 -1 / 0 / 1。"""
    return random.choice([-1, 0, 1]), random.choice([-1, 0, 1])


class RandomWalk:
    """随机游走：x_values / y_values 两个列表就是全部数据。"""

    def __init__(self, num_points=5000):
        self.num_points = num_points
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step, y_step = get_step()
            if x_step == 0 and y_step == 0:      # ★ and：两个都不动才重来
                continue
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)


random.seed(42)                               # 固定种子，输出才可复现
walk = RandomWalk(500)
walk.fill_walk()
print(f"点数：{len(walk.x_values)}（num_points = 500）")
print("前十步坐标：", list(zip(walk.x_values[:10], walk.y_values[:10])))
print(f"终点：({walk.x_values[-1]}, {walk.y_values[-1]})")
print(f"x 的范围：{min(walk.x_values)} ~ {max(walk.x_values)}"
      f"；y 的范围：{min(walk.y_values)} ~ {max(walk.y_values)}")
stayed = sum(1 for a, b in zip(walk.x_values, walk.y_values)
             if (a, b) == (0, 0))
print(f"经过原点 {stayed} 次（概率模型不同，这个数会变）")

print("\n=== 同一份坐标，换个画法就是不同的图 ===")
print("折线 --> ax.plot(walk.x_values, walk.y_values)")
print("散点 --> ax.scatter(walk.x_values, walk.y_values, s=1)")
print("上色 --> c=range(len(walk.x_values)), cmap=plt.cm.Blues  # 越走越深")

print("\n=== 掷骰子：一堆结果怎么变成频次表 ===")
random.seed(7)
results = [random.randint(1, 6) for _ in range(600)]
counts = Counter(results)                    # 一行数完，等价于 results.count(v)
print("前 20 次结果：", results[:20])
print("频次表：", dict(sorted(counts.items())))
frequencies = [counts[v] for v in range(1, 7)]   # 按面数顺序取，缺的面补 0
print("按面数排列：", frequencies)
assert sum(frequencies) == len(results)      # ★ 分布类程序必加：总数必须对上
print(f"总数校验通过：sum(frequencies) = {len(results)}")
print(f"出现最多：{counts.most_common(1)[0]}；最少：{counts.most_common()[-1]}")
print(f"平均点数：{sum(results) / len(results):.3f}（理论 3.5）")
