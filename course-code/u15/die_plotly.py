# die_plotly.py —— Plotly 模拟掷骰子（单骰 / 双六面 / 六面+二十面）
# 跑完可以删掉生成的 html 文件

import random

import plotly.express as px
import plotly.graph_objects as go


class Die:
    """一枚 n 面骰子，results 记住每一次的点数。"""

    def __init__(self, num_sides=6):
        self.num_sides = num_sides
        self.results = []

    def roll(self):
        result = random.randint(1, self.num_sides)   # 含 1 和 num_sides 两端
        self.results.append(result)


random.seed(42)

# ===== 1. 单个六面骰：results.count() 数频次 =====
die = Die()
for _ in range(1000):
    die.roll()

x_values = [str(v) for v in range(1, die.num_sides + 1)]
y_values = [die.results.count(v) for v in range(1, die.num_sides + 1)]
print("点数:", x_values, "次数:", y_values)

# ★ 自检：频次之和必须等于总投掷次数，否则说明漏统计了某个类别
assert sum(y_values) == len(die.results), "频次对不上，肯定漏了一个类别"

fig = px.bar(x=x_values, y=y_values, labels={"y": "出现次数"})
fig.update_layout(title="掷 1000 次六面骰子的点数分布", xaxis_title="骰子点数")
fig.update_traces(marker_color="royalblue", marker_line_color="black")
fig.add_hline(y=len(die.results) / die.num_sides, line_dash="dash", line_color="red",
              annotation_text="理论平均")
fig.write_html("die_六面.html")

# ===== 2. 两个六面骰：zip 把两条列表拉链配对，列表推导逐对相加 =====
d1, d2 = Die(), Die()
for _ in range(1000):
    d1.roll()
    d2.roll()

sums = [a + b for a, b in zip(d1.results, d2.results)]
freq = [sums.count(v) for v in range(2, 13)]          # 2~12 共 11 种
assert sum(freq) == len(sums), "点数和统计对不上"
print("点数和频次:", dict(zip(range(2, 13), freq)))

fig2 = px.bar(x=list(range(2, 13)), y=freq, labels={"x": "点数和", "y": "出现次数"})
fig2.update_layout(title="掷两个六面骰子 1000 次：点数和分布（钟形）")
fig2.update_traces(marker_color="royalblue", marker_line_color="black")
fig2.add_hline(y=len(sums) / 11, line_dash="dash", line_color="red",
               annotation_text="理论平均")
fig2.write_html("die_两个六面.html")

# ===== 3. 两个面数不同的骰子：六面 vs 二十面（graph_objects 画两组柱子）=====
d6, d20 = Die(6), Die(20)
for _ in range(2000):
    d6.roll()
    d20.roll()

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=list(range(1, 21)),
                      y=[d6.results.count(v) / len(d6.results) for v in range(1, 21)],
                      name="六面骰子", marker_color="royalblue", opacity=0.8))
fig3.add_trace(go.Bar(x=list(range(1, 21)),
                      y=[d20.results.count(v) / len(d20.results) for v in range(1, 21)],
                      name="二十面骰子", marker_color="tomato", opacity=0.8))
fig3.update_layout(barmode="group",
                   title="六面 vs 二十面：面数越多，分布越平（2000 次）",
                   xaxis_title="点数", yaxis_title="频率")
fig3.write_html("die_六面vs二十面.html")
print("已生成三张 html：单个骰子平坦，叠加后中间隆起，面数越多越平坦")
