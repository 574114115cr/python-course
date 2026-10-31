# die_lab.py —— 骰子实验平台
# 跑完可以删掉生成的 html 文件

import random

import plotly.express as px


class Die:
    def __init__(self, num_sides=6):
        self.num_sides = num_sides
        self.results = []

    def roll(self):
        self.results.append(random.randint(1, self.num_sides))


random.seed(2024)

# ===== 1. 两个六面骰：点数和 =====
d1, d2 = Die(), Die()
for _ in range(1000):
    d1.roll()
    d2.roll()

sums_6 = [a + b for a, b in zip(d1.results, d2.results)]
freq_6 = [sums_6.count(v) for v in range(2, 13)]
assert sum(freq_6) == len(sums_6), "统计对不上"
mean_6 = sum(sums_6) / len(sums_6)
var_6 = sum((v - mean_6) ** 2 for v in sums_6) / len(sums_6)
print(f"两个六面骰：均值 {mean_6:.2f}（理论 7），方差 {var_6:.3f}（理论 5.83）")
print("频次:", dict(zip(range(2, 13), freq_6)))

fig = px.bar(x=list(range(2, 13)), y=freq_6, labels={"x": "点数和", "y": "出现次数"})
fig.update_layout(title="两个六面骰：点数和分布（钟形）")
fig.update_traces(marker_color="royalblue", marker_line_color="black")
fig.add_hline(y=len(sums_6) / 11, line_dash="dash", line_color="red",
              annotation_text="理论平均")
fig.write_html("lab_两个六面.html")

# ===== 2. 六面 + 二十面：面数越多，分布越平 =====
d6, d20 = Die(6), Die(20)
for _ in range(2000):
    d6.roll()
    d20.roll()

sums_mix = [a + b for a, b in zip(d6.results, d20.results)]
freq_mix = [sums_mix.count(v) for v in range(2, 27)]
assert sum(freq_mix) == len(sums_mix), "统计对不上"
mean_mix = sum(sums_mix) / len(sums_mix)
var_mix = sum((v - mean_mix) ** 2 for v in sums_mix) / len(sums_mix)
print(f"\n六面 + 二十面：均值 {mean_mix:.2f}（理论 13.5），方差 {var_mix:.3f}")
print(f"最高点 {2 + freq_mix.index(max(freq_mix))}，方差对比："
      f"两个六面 {var_6:.2f} vs 六面+二十面 {var_mix:.2f}")

fig2 = px.bar(x=list(range(2, 27)), y=freq_mix, labels={"x": "点数和", "y": "出现次数"})
fig2.update_layout(title="六面 + 二十面：点数和分布（更平、峰更矮）")
fig2.update_traces(marker_color="tomato", marker_line_color="black")
fig2.write_html("lab_六面加二十面.html")
