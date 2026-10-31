# for_basics.py —— for 循环的标准结构

cars = ["小红帽", "凯迪拉克", "雷克萨斯"]

# 结构：for 临时变量 in 数据集合:  然后缩进的循环体
for car in cars:
    print(car)

# 循环结束后，变量依然存在，保留最后一个值
print("循环结束后 car =", car)      # 雷克萨斯

# 循环体内的多行都属于循环
for car in cars:
    print("正在处理：", car)     # 执行 3 次
    print("处理完毕")             # 也执行 3 次
print("全部处理完毕")             # 只执行 1 次

# 缩进错误的后果：下面这段会报 IndentationError
# for car in cars:
# print(car)
