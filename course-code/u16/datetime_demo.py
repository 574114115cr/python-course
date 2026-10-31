# datetime_demo.py —— strptime / strftime 练习

from datetime import datetime, timedelta

# ===== 1. strptime：字符串 -> 日期对象（parse 解析）=====
samples = [
    ("2021-07-01", "%Y-%m-%d"),
    ("2021/07/01", "%Y/%m/%d"),
    ("2021-07-01 14:30:05", "%Y-%m-%d %H:%M:%S"),
    ("July 1, 2021", "%B %d, %Y"),
]

print("--- strptime 解析 ---")
for text, fmt in samples:
    date_obj = datetime.strptime(text, fmt)
    print(f"{text!r:24} + {fmt!r:22} -> {date_obj}")

# ===== 2. 格式码必须和字符串严格匹配，否则 ValueError =====
print("\n--- 格式不匹配会怎样 ---")
try:
    datetime.strptime("2021-07-01", "%Y/%m/%d")     # 字符串是 -，格式写 /
except ValueError as error:
    print("解析失败：", error)

# ===== 3. strftime：日期对象 -> 字符串（format 格式化）=====
first_date = datetime.strptime("2021-07-01", "%Y-%m-%d")
print("\n--- strftime 格式化 ---")
print(first_date.strftime("%Y年%m月%d日"))            # 2021年07月01日
print(first_date.strftime("%B"))                      # July（月份名）
print(first_date.strftime("%A"))                      # Thursday（星期名）

# ===== 4. 日期对象能做算术，字符串不能 =====
tomorrow = first_date + timedelta(days=30)
print(f"\n{first_date.date()} 往后 30 天是 {tomorrow.date()}")
print("字符串直接相加:", "2021-07-01" + "30")          # 2021-07-0130，没有意义
