# reference_demo.py —— 引用陷阱的三种写法

import copy

# ===== 原写法：会互相影响 =====
cars = ["a", "b"]
other = cars# 注意：这里没有复制，只是多贴了一张标签
other.append("c")

print("实际输出：")
print(cars, other)          # ['a', 'b', 'c'] ['a', 'b', 'c']
print(cars is other)        # True

# 原因：把变量想象成贴在笔记本封面上的标签。
# other = cars 相当于给同一本笔记本再贴一张标签，
# 不管从哪张标签往本子上写字，本子都还是那一本。

# ===== 写法一：切片复制（浅拷贝）=====
cars = ["a", "b"]
other = cars[:]# 创建了一个全新的列表
other.append("c")
print("切片拷贝：", cars, other)      # ['a', 'b'] ['a', 'b', 'c']

# ===== 写法二：copy.copy() =====
cars = ["a", "b"]
other = copy.copy(cars)
other.append("c")
print("copy.copy：", cars, other)    # ['a', 'b'] ['a', 'b', 'c']

# ===== 写法三：完全独立（deepcopy）=====
cars = ["a", "b"]
other = copy.deepcopy(cars)
other.append("c")
print("deepcopy：", cars, other)     # ['a', 'b'] ['a', 'b', 'c']
