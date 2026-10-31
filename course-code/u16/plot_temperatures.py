# plot_temperatures.py —— plot + fill_between 画温度区间带

import csv
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

random.seed(42)        # 固定随机种子，每次运行生成的数据一样

# ===== 1. 准备数据：生成 30 天气温样本（2021 年 7 月）=====
path = Path("weather_data/sample_july.csv")
path.parent.mkdir(exist_ok=True)

with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["STATION", "NAME", "DATE", "TAVG", "TMAX", "TMIN"])
    for day in range(1, 31):
        # 模拟气温：最高 15~22 之间波动，最低 = 最高 - 5~9
        high = random.randint(15, 22)
        low = high - random.randint(5, 9)
        writer.writerow(
            ["USW00025333", "SITKA AIRPORT, AK US", f"2021-07-{day:02d}", "", high, low]
        )
print(f"已生成 {path}")

# ===== 2. 读数据：日期字符串用 strptime 转成日期对象 =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
next(reader)           # 跳过表头

dates, highs, lows = [], [], []
for row in reader:
    dates.append(datetime.strptime(row[2], "%Y-%m-%d"))
    highs.append(int(row[4]))
    lows.append(int(row[5]))

# ===== 3. 画图 =====
plt.style.use("seaborn-v0_8")         # 皮肤；这行删掉也能跑
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(dates, highs, c="red", alpha=0.5, label="High")
ax.plot(dates, lows, c="blue", alpha=0.5, label="Low")
ax.fill_between(dates, highs, lows, facecolor="blue", alpha=0.1)

ax.set_title("Daily High and Low Temperatures - July 2021", fontsize=20)
ax.set_ylabel("Temperature (C)", fontsize=14)
ax.legend()                            # 显示图例
fig.autofmt_xdate()                    # 日期标签倾斜，防止重叠

plt.savefig("温度区间图.png", dpi=150, bbox_inches="tight")
print("图片已保存为 温度区间图.png")

# 教材里这一步是 plt.show()，会弹出窗口；
# savefig 存成文件，画出来的图完全一样，无图形界面的环境也能跑
