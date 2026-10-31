# score_manager.py —— CSV 成绩管理系统

import csv
import os

FILENAME = "scores.csv"
FIELDS = ["姓名", "数学", "英语", "总分"]


def init_file(filename=FILENAME):
    """创建文件并写入表头（覆盖已有文件）。"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
    print(f"已初始化 {filename}")


def add_student(name, math, english, filename=FILENAME):
    """追加一名学生，总分自动计算。"""
    total = math + english
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, math, english, total])
    print(f"已添加：{name}（总分 {total}）")


def read_all(filename=FILENAME):
    """返回所有学生数据（字典列表），文件不存在时返回空列表。"""
    try:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"  {filename} 不存在，返回空列表")
        return []


def class_average(subject, filename=FILENAME):
    """返回某科目的班级平均分。"""
    students = read_all(filename)
    if not students:
        return 0
    total = sum(float(s[subject]) for s in students)
    return total / len(students)


def ranking(filename=FILENAME):
    """返回按总分降序排好的学生列表。"""
    students = read_all(filename)
    return sorted(students, key=lambda s: float(s["总分"]), reverse=True)


def delete_student(name, filename=FILENAME):
    """删除指定学生：读出 -> 过滤 -> 重写文件。"""
    students = read_all(filename)
    remaining = [s for s in students if s["姓名"] != name]

    if len(remaining) == len(students):
        print(f"  未找到学生 {name}")
        return False

    # 重写整个文件
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        for student in remaining:
            writer.writerow([
                student["姓名"],
                student["数学"],
                student["英语"],
                student["总分"],
            ])

    print(f"  已删除 {name}，剩余 {len(remaining)} 人")
    return True


def show_all(filename=FILENAME):
    """格式化显示所有学生。"""
    students = read_all(filename)
    if not students:
        print("  （暂无数据）")
        return

    print(f"  {'姓名':<8}{'数学':>8}{'英语':>8}{'总分':>8}")
    print("  " + "-" * 32)
    for student in students:
        print(f"  {student['姓名']:<8}{student['数学']:>8}"
              f"{student['英语']:>8}{student['总分']:>8}")


# ===== 测试 =====
print("=== 初始化 ===")
init_file()

print("\n=== 添加学生 ===")
add_student("小明", 92, 88)
add_student("小红", 78, 95)
add_student("小刚", 65, 72)
add_student("小丽", 88, 91)

print("\n=== 全部学生 ===")
show_all()

print("\n=== 班级平均分 ===")
print(f"  数学平均分：{class_average('数学'):.2f}")
print(f"  英语平均分：{class_average('英语'):.2f}")

print("\n=== 排名（按总分降序）===")
for i, student in enumerate(ranking(), 1):
    print(f"  {i}. {student['姓名']}，总分 {student['总分']}")

print("\n=== 删除学生 ===")
delete_student("小红")
show_all()

print("\n=== CSV 文件的原始内容 ===")
with open(FILENAME, "r", newline="", encoding="utf-8") as f:
    print(f.read())

# 清理
if os.path.exists(FILENAME):
    os.remove(FILENAME)
