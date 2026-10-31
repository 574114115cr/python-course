# death_valley_year.py —— 全年温度图：读数据 -> 洗数据 -> 画图

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt

random.seed(2021)

# ===== 1. 生成 365 天死亡谷风格数据 =====
# 用正弦曲线造"夏热冬暖"的基准温度，再加随机波动；约 5% 的天数缺数据
start = datetime(2021, 1, 1)
rows = [["STATION", "NAME", "DATE", "TMAX", "TMIN"]]

for day in range(365):
    date_text = (start + timedelta(days=day)).strftime("%Y-%m-%d")
    base = 30 + 10 * math.sin(2 * math.pi * (day - 200) / 365)   # 40（夏）~ 20（冬）
    high = int(base + random.uniform(-4, 4))
    low = high - random.randint(9, 14)
    if random.random() < 0.05:                                   # 5% 概率缺数据
        rows.append(["USC00042319", "DEATH VALLEY, CA US", date_text, "", ""])
    else:
        rows.append(["USC00042319", "DEATH VALLEY, CA US", date_text, high, low])

path = Path("weather_data/death_valley_2021_full.csv")
path.parent.mkdir(exist_ok=True)
with open(path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
print(f"已生成 {path}")

# ===== 2. 读取 + 缺失值处理 =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
next(reader)

dates, highs, lows = [], [], []
for row in reader:
    current_date = datetime.strptime(row[2], "%Y-%m-%d")
    try:
        high = int(row[3])
        low = int(row[4])
    except ValueError:
        print(f"Missing data for {current_date}")
    else:
        dates.append(current_date)
        highs.append(high)
        lows.append(low)

print(f"有效天数: {len(dates)}")
assert len(dates) == len(highs) == len(lows), "三个列表不等长，肯定有 bug"

# ===== 3. 画图 =====
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(dates, highs, c="red", alpha=0.5, label="High")
ax.plot(dates, lows, c="blue", alpha=0.5, label="Low")
ax.fill_between(dates, highs, lows, facecolor="blue", alpha=0.1)

ax.set_title(f"Death Valley 2021 ({len(dates)} valid days)", fontsize=20)
ax.set_ylabel("Temperature (F)", fontsize=14)
ax.legend()
fig.autofmt_xdate()

plt.savefig("死亡谷2021.png", dpi=150, bbox_inches="tight")
print("图片已保存为 死亡谷2021.png")

path.unlink()        # 清理
