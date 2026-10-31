# missing_stats.py —— 缺失值统计

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(7)

# ===== 1. 生成 20 天数据，随机挑 3 天缺 TMAX =====
start = datetime(2021, 7, 1)
missing_offsets = set(random.sample(range(20), 3))     # 随机 3 天缺数据

rows = [["STATION", "NAME", "DATE", "TMAX", "TMIN"]]
for offset in range(20):
    date_text = (start + timedelta(days=offset)).strftime("%Y-%m-%d")
    if offset in missing_offsets:
        rows.append(["USC00042319", "DEATH VALLEY, CA US", date_text, "", ""])
    else:
        high = random.randint(38, 46)
        low = high - random.randint(8, 12)
        rows.append(["USC00042319", "DEATH VALLEY, CA US", date_text, high, low])

path = Path("dv_sample.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)

# ===== 2. 读取 + 统计 =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
next(reader)

dates, highs, lows = [], [], []
missing_list = []
for row in reader:
    current_date = datetime.strptime(row[2], "%Y-%m-%d")
    try:
        high = int(row[3])
        low = int(row[4])
    except ValueError:
        missing_list.append(current_date)
    else:
        dates.append(current_date)
        highs.append(high)
        lows.append(low)

print(f"总行数: {len(dates) + len(missing_list)}")
print(f"有效天数: {len(dates)}")
print(f"缺失天数: {len(missing_list)}")
print(f"缺失的日期: {[d.strftime('%Y-%m-%d') for d in missing_list]}")

average_high = sum(highs) / len(highs)
print(f"有效数据平均最高温: {average_high:.1f}")
print(f"三个列表等长: {len(dates) == len(highs) == len(lows)}")

path.unlink()
