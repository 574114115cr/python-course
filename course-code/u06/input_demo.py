# input_demo.py —— input() 永远返回字符串

# 观察类型：无论输入什么，type 都是 str
age = input("请输入年龄：")
print(f"你输入了 {age}，类型是 {type(age)}")

# 直接做加法会报错（取消下面两行的注释运行看看）
# print(age + 1)     # TypeError: can only concatenate str to int

# 正确做法：三步模板
age = int(input("请输入年龄："))     # 第1、2 步：输入 + 转整数
next_age = age + 1# 第 3 步：参与运算
print(f"明年你{next_age} 岁")

# float 输入
price = float(input("请输入价格："))
print(f"含税价格：{price * 1.13:.2f} 元")

# ===== 三步模板的完整演示 =====
# 第 1 步：用 input() 拿字符串
raw = input("请输入两个数，用空格分隔（如 10 5）：")
# 第 2 步：用 split() 拆开，再转成数字
parts = raw.split()# 得到字符串列表 ['10', '5']
a = int(parts[0])
b = int(parts[1])
# 第 3 步：运算
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} × {b} = {a * b}")
