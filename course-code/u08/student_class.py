# student_class.py —— 学生类

class Student:
    """学生。"""
    def __init__(self, name, scores=None):
        self.name = name
        # 注意：这里用 None 然后再造列表，避免直接引用外部列表
        self.scores = list(scores) if scores else []

    def add_score(self, score):
        """添加一次成绩。"""
        self.scores.append(score)
        return self.scores

    def average(self):
        """返回平均分，没有成绩时返回 0。"""
        if not self.scores:
            return 0
        return sum(self.scores) / len(self.scores)

    def highest(self):
        """返回最高分，没有成绩时返回 None。"""
        if not self.scores:
            return None
        return max(self.scores)

    def lowest(self):
        """返回最低分。"""
        if not self.scores:
            return None
        return min(self.scores)

    def is_pass(self):
        """平均分 60 分以上算及格。"""
        return self.average() >= 60

    def __str__(self):
        return f"{self.name} 的平均分是 {self.average():.2f}"


# ===== 测试 =====
student = Student("小明")
for score in [88, 92, 76, 95, 61]:
    student.add_score(score)

print(student)
print(f"最高分：{student.highest()}")
print(f"最低分：{student.lowest()}")
print(f"及格了吗：{'是' if student.is_pass() else '否'}")
print(f"全部成绩：{student.scores}")

# 边界情况：没有成绩
print("\n--- 没有成绩的情况 ---")
empty = Student("小刚")
print(f"平均分：{empty.average()}")
print(f"最高分：{empty.highest()}")
print(f"及格了吗：{empty.is_pass()}")

# ===== 副本语义演示 =====
print("\n--- 副本语义：构造时传入的列表是否被引用 ---")
original_scores = [70, 80]
student2 = Student("小红", original_scores)
student2.add_score(90)

print(f"student2 的成绩：{student2.scores}")     # [70, 80, 90]
print(f"原始列表：{original_scores}")            # [70, 80]  没变！

# 原因：构造函数里写了 list(scores)，造了一份副本。
# 如果去掉 list() 直接self.scores = scores，
# 那么student2.scores 和 original_scores 就是同一个对象，
# student2 加分会影响原始列表。

# 多名学生管理
print("\n--- 班级成绩单 ---")
students = [
    Student("小明", [88, 92, 76]),
    Student("小红", [95, 89, 99]),
    Student("小刚", [45, 60, 55]),
]

for s in students:
    print(f"  {s}  最高 {s.highest()} 分  "
          f"{'及格' if s.is_pass() else '不及格'}")

passed = [s.name for s in students if s.is_pass()]
print("及格名单：", passed)
