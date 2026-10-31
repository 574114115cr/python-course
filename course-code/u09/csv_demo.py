# csv_demo.py —— 读写 CSV 表格

import csv

filename = "students.csv"

# ===== 写 CSV =====
# newline="" 是必须写的，encoding="utf-8" 保证中文不乱码
with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["姓名", "年龄", "城市", "成绩"])     # 表头
    writer.writerow(["小明", 18, "杭州", 92.5])
    writer.writerow(["小红", 22, "北京", 88.0])
    writer.writerow(["小刚", 20, "上海", 76.5])

print(f"已写入 {filename}")

# ===== 读 CSV =====
with open(filename, "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(f"  {row}")

print("\n--- 读成字典列表（更方便处理）---")
with open(filename, "r", newline="", encoding="utf-8") as f:
    # DictReader 把每行和表头对应起来
    reader = csv.DictReader(f)
    students = list(reader)

for student in students:
    print(f"  {student['姓名']}：{student['年龄']} 岁，"
          f"在 {student['城市']}，成绩 {student['成绩']}")

# 用字典形式处理数据非常顺手
print("\n--- 基于字典做统计 ---")
total_score = sum(float(s["成绩"]) for s in students)
print(f"总成绩：{total_score}")
print(f"平均分：{total_score / len(students):.2f}")
best = max(students, key=lambda s: float(s["成绩"]))
print(f"最高分：{best['姓名']}，{best['成绩']}")

# ===== 追加数据 =====
with open(filename, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["小丽", 19, "广州", 95.0])

with open(filename, "r", newline="", encoding="utf-8") as f:
    print(f"\n追加后的行数：{sum(1 for _ in f)}")

import os
os.remove(filename)
