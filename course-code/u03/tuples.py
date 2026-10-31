# tuples.py —— 元组：不可修改的序列

# 创建元组：用圆括号，或者直接逗号
point = (3, 5)
colors = "red", "green", "blue"          # 不加括号也合法，但建议加括号
empty_tuple = ()
single = (5,)                             # 单元素元组必须带逗号！
not_tuple = (5)                           # 这其实是整数 5

print("point：", point, "类型：", type(point))
print("not_tuple：", not_tuple, "类型：", type(not_tuple))   # int！括号只是分组
print("single：", single, "类型：", type(single))            # tuple，正确

# 读取和切片都可以
print("point[0]：", point[0])              # 3
print("point[-1]：", point[-1])             # 5
print("切片：", point[:1])                  # (3,)

# 修改会报 TypeError
# point[0] = 9      # TypeError: 'tuple' object does not support item assignment

# 但可以"整体替换"
point = (9, 5)
print("整体替换后：", point)                # (9, 5)

# 元组没有 append/remove 方法
# point.append(1)   # AttributeError: 'tuple' object has no attribute 'append'

# 常用场景1：坐标
location = (116.40, 39.90)
print("经度：", location[0], "纬度：", location[1])

# 常用场景2：日期（年、月、日天然固定）
date = (2026, 10, 14)
year, month, day = date                    # 解包，一次取出三个值
print(f"{year}年{month}月{day}日")

# 常用场景3：字典的键必须是不可变类型，所以常用元组
locations = {(116.40, 39.90): "北京", (121.47, 31.23): "上海"}
print("北京坐标：", locations[(116.40, 39.90)])    # 北京
print("键的类型：", type((116.40, 39.90)))         # tuple

# 元组和列表可以互相转换
t = (1, 2, 3)
print("元组转列表：", list(t))               # [1, 2, 3]
print("列表转元组：", tuple([1, 2, 3]))        # (1, 2, 3)
