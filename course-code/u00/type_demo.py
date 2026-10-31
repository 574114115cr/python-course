# type_demo.py —— 认识 Python 的基本数据类型

age = 18# 整数 int
height = 1.75        # 小数 float
name = "小明"# 字符串 str
is_student = True    # 布尔值 bool（只有 True 和 False，首字母必须大写）

print(type(age), age)         # <class 'int'> 18
print(type(height), height)   # <class 'float'> 1.75
print(type(name), name)       # <class 'str'> 小明
print(type(is_student))       # <class 'bool'>

# type() 返回的是"类型"，数据才是真正存的东西
# 类比：type() 告诉你容器是什么，变量里装的是内容
