# header_locator.py —— 按列名找列号，不硬编码

import csv
from pathlib import Path

HEADER = ["城市", "日期", "最高温", "最低温"]
ROWS = [
    ["北京", "2021-07-01", 35, 26],
    ["北京", "2021-07-02", 33, 25],
    ["北京", "2021-07-03", 37, 27],
    ["北京", "2021-07-04", 31, 24],
    ["北京", "2021-07-05", 34, 25],
]

path = Path("cities.csv")
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    writer.writerows(ROWS)

# ===== 读取 =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
header_row = next(reader)

print("--- 表头（列号: 列名）---")
for index, name in enumerate(header_row):
    print(f"{index}: {name}")

def find_column(header, name):
    """按列名找列号；找不到返回 -1。"""
    for index, column_name in enumerate(header):
        if column_name == name:
            return index
    return -1

city_i = find_column(header_row, "城市")
date_i = find_column(header_row, "日期")
high_i = find_column(header_row, "最高温")
low_i = find_column(header_row, "最低温")
print(f"\n找到的列号: 城市={city_i}, 日期={date_i}, 最高温={high_i}, 最低温={low_i}")
print(f"不存在的'湿度'列: {find_column(header_row, '湿度')}")

print("\n--- 数据 ---")
for row in reader:
    print(f"{row[date_i]} {row[city_i]} 最高 {row[high_i]} 最低 {row[low_i]}")

# 把 HEADER 的顺序打乱再跑，结果依然正确 —— 这就是按名字找列的意义
path.unlink()
