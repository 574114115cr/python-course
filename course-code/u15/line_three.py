# line_three.py —— 折线图三种样式
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

x = list(range(1, 21))
y = [i * i for i in x]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y, linewidth=3, marker="o", color="royalblue")
ax.set_title("20 以内的平方数", fontsize=16)
ax.set_xlabel("数字", fontsize=12)
ax.set_ylabel("平方", fontsize=12)

# ===== 定制刻度：x 轴只标奇数位，y 轴每 50 一格 =====
ax.set_xticks(x[::2])                              # 1, 3, 5, ... 隔一个取一个
ax.set_yticks(list(range(0, 401, 50)))
ax.grid(True, linestyle=":", alpha=0.6)             # 点状网格，不抢主体
fig.savefig("square_默认样式.png", dpi=100, bbox_inches="tight")

# ===== 换三种内置样式各存一张 =====
styles = [s for s in plt.style.available
          if s in ("seaborn-v0_8", "ggplot", "bmh", "dark_background")]
for style in styles[:3]:
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, linewidth=3, marker="o")
    ax.set_title(f"平方数（{style}）")
    ax.set_xticks(x[::2])
    ax.set_yticks(list(range(0, 401, 50)))
    fig.savefig(f"square_{style}.png", dpi=100, bbox_inches="tight")
    print("已生成", f"square_{style}.png")

plt.style.use("default")        # 换回默认，免得影响后面画的东西
