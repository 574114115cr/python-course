# grade_level.py —— 四档成绩等级

score = 85

# elif 链必须从高分往低分排，这样"高分"条件先命中，
# 后面的低分条件才有机会给中等分学生用
if score >= 90:
    level = "优秀"
elif score >= 80:
    level = "良好"
elif score >= 60:
    level = "及格"
else:
    level = "不及格"

# 输出结果
print(f"成绩为 {score} 分，等级为{level}")

# 批量演示，确认每一档都能命中
for s in [95, 85, 65, 45]:
    if s >= 90:
        lv = "优秀"
    elif s >= 80:
        lv = "良好"
    elif s >= 60:
        lv = "及格"
    else:
        lv = "不及格"
    print(f"  {s} 分 -> {lv}")
