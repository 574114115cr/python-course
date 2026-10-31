# extract_with_missing.py —— try/except 处理缺失值

import csv
from datetime import datetime
from pathlib import Path

# ===== 1. 造一份"有缺失"的死亡谷风格 CSV =====
# 表头：STATION, NAME, DATE, TMAX, TMIN, TOBS
# 故意让 2021-03-05 这天的 TMAX/TMIN 缺失
rows = [
    ["STATION", "NAME", "DATE", "TMAX", "TMIN", "TOBS"],
    ["USC00042319", "DEATH VALLEY, CA US", "2021-01-01", "71", "51", "56"],
    ["USC00042319", "DEATH VALLEY, CA US", "2021-01-02", "69", "48", "52"],
    ["USC00042319", "DEATH VALLEY, CA US", "2021-03-05", "", "", ""],
    ["USC00042319", "DEATH VALLEY, CA US", "2021-01-03", "74", "53", "58"],
]

path = Path("death_valley_2021_simple.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)

# ===== 2. 教材同款：提取 + 缺失值处理 =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
header_row = next(reader)

print("表头:", header_row)       # 先打印表头找列号（好习惯）

dates, highs, lows = [], [], []
missing_days = 0
for row in reader:
    current_date = datetime.strptime(row[2], "%Y-%m-%d")
    try:
        high = int(row[3])
        low = int(row[4])
    except ValueError:
        # 空字符串转 int 会抛 ValueError：这一天没测到数据
        print(f"Missing data for {current_date}")
        missing_days += 1
    else:
        # 只有两个值都转换成功，才一起收进三个列表
        # 保证 dates/highs/lows 永远等长、一一对应
        dates.append(current_date)
        highs.append(high)
        lows.append(low)

print(f"\n共 {len(dates)} 天有效数据，跳过 {missing_days} 天缺失数据")
print(f"三个列表等长吗？dates={len(dates)}, highs={len(highs)}, lows={len(lows)}")

# ===== 3. 为什么 else 不能省？ =====
# 如果把 append 写进 try：遇到 TMAX 缺失的这天，
# high = int("") 先抛异常，而 dates 已经在异常前 append 过了
# 结果 dates 比 highs 长 -> 画图时报错或整列错位

path.unlink()        # 清理
