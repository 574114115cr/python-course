# if_single.py —— 最简单的条件判断

age = 20

# 缩进的行才是条件成立时执行的
if age >= 18:
    print("你已成年，可以进入")

# 条件不成立时，这段代码被完全跳过（不是报错，是安静地跳过）
if age < 18:
    print("你未成年，禁止进入")
print("这句无论条件如何都会执行")     # 缩进退回一级 = 在 if 外面

# 注意：= 是赋值，== 才是比较。下面这行会报 SyntaxError
# if age = 18:
#     print("错误写法")

# 多个条件用 and 连接
age = 20
has_ticket = True
if age >= 18 and has_ticket:
    print("可以入场")

# 也可以写成链式比较（数字专用）
if 18 <= age < 60:
    print("处于 18 到 60 之间")
