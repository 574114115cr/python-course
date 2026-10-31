# class_data.py —— 嵌套字典的综合提取

class_data = {
    "class1": {
        "teacher": "李老师",
        "students": [
            {"name": "小明", "score": 92},
            {"name": "小红", "score": 78},
            {"name": "小刚", "score": 85},
        ],
    },
    "class2": {
        "teacher": "王老师",
        "students": [
            {"name": "小丽", "score": 88},
            {"name": "小强", "score": 95},
        ],
    },
}

# 1）每个班的老师和学生人数
print("--- 班级概况 ---")
for class_name, info in class_data.items():
    print(
        f"{class_name}: 老师{info['teacher']}，"
        f"共{len(info['students'])} 名学生"
    )

# 2）所有学生中分数最高的
highest_name = ""
highest_score = -1
for class_name, info in class_data.items():
    for student in info["students"]:
        if student["score"] > highest_score:
            highest_score = student["score"]
            highest_name = student["name"]
print(f"\n最高分：{highest_name}，{highest_score} 分")

# 3）总分最高的班级
print("\n--- 班级总分 ---")
best_class = ""
best_total = -1
for class_name, info in class_data.items():
    total = 0
    for student in info["students"]:
        total += student["score"]
    average = total / len(info["students"])
    print(f"{class_name}: 总分 {total}，平均 {average:.1f}")
    if total > best_total:
        best_total = total
        best_class = class_name
print(f"总分最高的是 {best_class}（{best_total} 分）")

# 4）所有学生的平均分
all_scores = []
for class_name, info in class_data.items():
    for student in info["students"]:
        all_scores.append(student["score"])
overall = sum(all_scores) / len(all_scores)
print(f"\n全校平均分：{overall:.2f}")     # 87.60

# 5）安全地取不存在的班级
teacher = class_data.get("class3", {}).get("teacher", "班级不存在")
print("\nclass3 的老师：", teacher)

# 用推导式做同样的事，更短
all_names = [
    student["name"]
    for class_name, info in class_data.items()
    for student in info["students"]
]
print("所有学生：", all_names)
