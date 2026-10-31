# comprehension.py —— 列表推导式：传统写法 vs 一行写法

# 案例1：计算平方
# 传统写法
squares = []
for number in range(1, 6):
    squares.append(number ** 2)
print("传统写法：", squares)

# 推导式写法（完全等价）
squares = [number ** 2 for number in range(1, 6)]
print("推导式：", squares)          # [1, 4, 9, 16, 25]

# 案例2：筛选偶数
# 传统写法
evens = []
for number in range(1, 11):
    if number % 2 == 0:
        evens.append(number)
print("传统筛选：", evens)

# 推导式 + if 条件
evens = [number for number in range(1, 11) if number % 2 == 0]
print("推导式筛选：", evens)        # [2, 4, 6, 8, 10]

# 案例3：字符串统一大写
words = ["python", "is", "fun"]
print("大写：", [word.upper() for word in words])

# 案例4：三元表达式放进推导式
nums = [1, 2, 3, 4, 5, 6]
print("标记奇偶：", [("偶" if n % 2 == 0 else "奇") for n in nums])

# 什么时候不要用推导式：逻辑复杂时老老实实写循环
# 下面这种嵌套推导式虽然能跑，但没人看得懂：
# print([x * y for x in range(3) for y in range(3) if x != y])
# 可读性优先于行数。
