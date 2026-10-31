# make_weather_csv.py —— 生成 mini 版气温 CSV，练习读表头
# 跑完可以删掉生成的 weather_data 文件夹

import csv
from pathlib import Path

# ===== 1. 造一份和教材 sitka_weather_2021_simple.csv 同格式的小文件 =====
# 表头六列：STATION, NAME, DATE, TAVG, TMAX, TMIN；TAVG 故意留空模拟缺失
rows = [
    ["STATION", "NAME", "DATE", "TAVG", "TMAX", "TMIN"],
    ["USW00025333", "SITKA AIRPORT, AK US", "2021-01-01", "", "44", "40"],
    ["USW00025333", "SITKA AIRPORT, AK US", "2021-01-02", "", "44", "35"],
    ["USW00025333", "SITKA AIRPORT, AK US", "2021-01-03", "", "43", "36"],
    ["USW00025333", "SITKA AIRPORT, AK US", "2021-01-04", "", "45", "39"],
]

data_dir = Path("weather_data")
data_dir.mkdir(exist_ok=True)            # 文件夹不存在就创建
path = data_dir / "sitka_weather_2021_simple.csv"

# newline="" 是 csv 模块的标准要求，防止 Windows 上多出空行
with open(path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
print(f"已生成 {path}")

# ===== 2. 教材同款读法：read_text -> splitlines -> csv.reader =====
lines = path.read_text(encoding="utf-8").splitlines()
reader = csv.reader(lines)
header_row = next(reader)                # 取出表头，reader 剩下的是数据

print("\n--- 表头（列号: 列名）---")
for index, column_name in enumerate(header_row):
    print(f"第 {index} 列: {column_name}")

# ===== 3. 用列名找列号，而不是硬编码 =====
column_index = {name: i for i, name in enumerate(header_row)}
date_i = column_index["DATE"]
high_i = column_index["TMAX"]
low_i = column_index["TMIN"]
print(f"\nDATE 在第 {date_i} 列，TMAX 在第 {high_i} 列，TMIN 在第 {low_i} 列")

# ===== 4. 按名字取数，就算以后列顺序变了也不会错 =====
print("\n--- 按列名取数据 ---")
for row in reader:
    print(f"{row[date_i]}: 最高 {row[high_i]}, 最低 {row[low_i]}")
