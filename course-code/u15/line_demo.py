# line_demo.py —— 折线图三连
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

input_values = [1, 2, 3, 4]
output_values = [1, 4, 9, 16]

# ===== 1. 最朴素的一张折线图（对照老写法 plt.plot）=====
fig, ax = plt.subplots()
ax.plot(input_values, output_values)
ax.set_title("朴素版")
fig.savefig("line_1_朴素版.png", dpi=100, bbox_inches="tight")
print("可用样式：", plt.style.available[:8], "...")

# ===== 2. 改线宽、改标签文字 =====
plt.style.use("seaborn-v0_8")                    # 先换皮肤
fig, ax = plt.subplots()
ax.plot(input_values, output_values, linewidth=3)   # lw=3 让线明显变粗
ax.set_title("折线图：平方增长", fontsize=16)
ax.set_xlabel("输入值", fontsize=12)
ax.set_ylabel("输出值", fontsize=12)
ax.set_xticks(input_values)
ax.set_yticks(output_values)
ax.grid(True)                                   # 网格线，方便读数
fig.savefig("line_2_加粗版.png", dpi=100, bbox_inches="tight")

# ===== 3. 换皮肤再画一张（matplotlib 自带的 bmh 样式）=====
plt.style.use("bmh")
fig, ax = plt.subplots()
ax.plot(input_values, output_values, marker="o", linewidth=2, color="tomato")
ax.set_title("折线图：换个皮肤")
fig.savefig("line_3_换皮肤版.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
