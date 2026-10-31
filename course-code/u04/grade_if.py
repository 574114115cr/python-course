# grade_if.py —— 多分支：成绩等级评定

score = 85

# 从最严格的条件开始，逐步放宽
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"分数 {score}，等级 {grade}")     # 分数 85，等级 B

# 演示"只执行一个分支"
print("---")
for s in [95, 85, 75, 65, 45]:
    if s >= 90:
        g = "A"
    elif s >= 80:
        g = "B"
    elif s >= 70:
        g = "C"
    elif s >= 60:
        g = "D"
    else:
        g = "F"
    print(f"{s} -> {g}")
# 95->A, 85->B, 75->C, 65->D, 45->F

# 注意 else 块里不能再写 if；如果需要，必须用 elif 串成一条链
# 下面这种写法是错的（else 后面不能跟 elif）：
# else:
#     if s >= 0:
#         g = "零分"
