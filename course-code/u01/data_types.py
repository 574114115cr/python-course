# data_types.py —— Python 四种基本数据类型

name = "小明"      # str：字符串，文字必须用引号包起来
age = 18# int：整数，没有小数点
height = 1.75      # float：小数，有小数点
is_student = True  # bool：布尔值，只有 True/False，首字母大写

# type() 返回变量的类型
print(type(name))        # <class 'str'>
print(type(age))         # <class 'int'>
print(type(height))      # <class 'float'>
print(type(is_student))  # <class 'bool'>

# 类型决定了能做什么：整数能加，小数能加，字符串也能加（但含义不同）
print(age + 1)        # 19      数值加法
print(height + 0.1)   # 1.85    数值加法
print(name + "同学")   # 小明同学    字符串拼接（连接）
# print(age + name)  # 报错 TypeError：不同类型不能直接相加
