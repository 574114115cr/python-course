# csv_stringio.py —— 不下载文件也能练：用 StringIO 造表 + 按年统计
import csv
import io
from datetime import datetime

CSV_TEXT = """STATION,NAME,DATE,TMAX,TMIN
USC00042319,DEATH VALLEY,2021-01-01,71,51
USC00042319,DEATH VALLEY,2021-07-11,128,91
USC00042319,DEATH VALLEY,2021-12-31,64,40
USC00042319,DEATH VALLEY,2022-06-17,,88
USC00042319,DEATH VALLEY,2022-07-09,127,90
USW00025333,SITKA,2022-07-05,64,52
"""

stream = io.StringIO(CSV_TEXT)          # 文件对象？StringIO 假装自己是文件
reader = csv.DictReader(stream)          # ★ 用表头当键，不用记列号
print("表头：", reader.fieldnames)
rows = list(reader)
print(f"数据行：{len(rows)} 条；第一行：{rows[0]}")

by_year = {}                             # 年份 -> {"tmax": 最高温, "when": 哪天}
missing = 0
for row in rows:
    when = datetime.strptime(row["DATE"], "%Y-%m-%d")
    try:
        high = int(row["TMAX"])
    except (TypeError, ValueError):
        missing += 1                     # 空字段 -> None，int(None) 抛 TypeError
        print(f"  跳过 {row['DATE']}：TMAX 缺失")
        continue
    best = by_year.setdefault(when.year, {"tmax": high, "when": when})
    if high > best["tmax"]:
        by_year[when.year] = {"tmax": high, "when": when}

print(f"\n=== 每年最高温（共 {len(by_year)} 年，跳过 {missing} 条缺数据）===")
for year in sorted(by_year):
    item = by_year[year]
    print(f"{year}：{item['tmax']}°F 出现在 {item['when']:%Y-%m-%d}")

print("\n=== 两个站点各有多少条 ===")
stations = {}
for row in rows:
    stations[row["NAME"]] = stations.get(row["NAME"], 0) + 1
for name, count in sorted(stations.items()):
    print(f"  {name:<14}{count} 条")

print("\n=== 换成 json 输出（plotly 那边要的就是这种结构）===")
import json

payload = [{"year": year, "tmax": item["tmax"],
            "date": item["when"].strftime("%Y-%m-%d")}
           for year, item in sorted(by_year.items())]
print(json.dumps(payload, ensure_ascii=False))
