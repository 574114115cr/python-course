# list_basics.py —— 列表的创建与元素访问

# 用方括号创建列表，元素之间用逗号分隔
cars = ["小红帽", "二手柯尼塞格", "凯迪拉克"]
numbers = [1, 10, 100, 1000]
mixed = ["hello", 3.14, True, None]   # 元素类型可以混合
empty = []                            # 空列表

# 按索引读取元素：索引从 0 开始
print(cars[0])       # 小红帽（第一个）
print(cars[1])       # 二手柯尼塞格（第二个）
print(cars[2])       # 凯迪拉克（第三个）

# 负索引：从末尾往回数，-1 是最后一个
print(cars[-1])      # 凯迪拉克
print(cars[-2])      # 二手柯尼塞格
print(cars[-3])      # 小红帽

# len() 求长度：元素个数
print("cars 的长度：", len(cars))     # 3
print("empty 的长度：", len(empty))   # 0

# 常见错误：索引越界
# print(cars[3])     # IndexError: list index out of range
# print(cars[-4])    # IndexError: list index out of range

# 用 len() 配合负索引，可以取到"倒数第几个"
print("倒数第二个：", cars[len(cars) - 2])   # 二手柯尼塞格
