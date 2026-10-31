# function_basics.py —— 函数的定义与调用

def greet_user():
    """一个最简单的函数：打招呼。"""
    print("你好，欢迎使用 Python！")


greet_user()      # 调用：写函数名加括号
greet_user()      # 可以反复调用，每次都执行一遍

# 带参数的函数
def greet_name(name):
    """向指定的人打招呼。"""
    print(f"你好，{name}！")


greet_name("小明")
greet_name("小红")

# 带默认值的参数
def greet_with_title(name, title="同学"):
    """带称呼的问候，title 可以不填。"""
    print(f"你好，{title} {name}！")


greet_with_title("小明")              # 你好，同学 小明！
greet_with_title("李老师", "老师")     # 你好，老师 李老师！

# 多参数函数
def rectangle_area(width, height):
    """计算矩形面积。"""
    return width * height


print(f"面积：{rectangle_area(5, 3)}")        # 面积：15
