# conditional_expression.py —— 一行写完 if/else

age = 20
score = 85

# 传统写法：4 行
if age >= 18:
    status = "成年"
else:
    status = "未成年"

# 条件表达式：1 行
status = "成年" if age >= 18 else "未成年"
print("状态：", status)

# 更有用的例子：给变量找默认值
input_name = ""# 用户没填
display = input_name if input_name else "游客"# 空就用默认值
print("显示名：", display)

# 嵌套一层还能读（不推荐，但要能看懂）
level = "高" if score >= 90 else "中" if score >= 60 else "低"
print(f"{score} 分，水平：{level}")     # 85 分，水平：中

# 嵌套两层就别再压缩了，拆开写
if score >= 90:
    level = "优秀"
elif score >= 80:
    level = "良好"
elif score >= 60:
    level = "及格"
else:
    level = "不及格"
print(f"{score} 分，等级：{level}")     # 85 分，等级：良好
# 原则：可读性优先于行数，超过一层嵌套就该用 elif 链
