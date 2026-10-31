# ranges.py —— range 的四种形式

print("range(1, 10)：", list(range(1, 10)))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

print("range(2, 20, 3)：", list(range(2, 20, 3)))
# [2, 5, 8, 11, 14, 17]

print("range(10, 0, -2)：", list(range(10, 0, -2)))
# [10, 8, 6, 4, 2]

print("range(0)：", list(range(0)))
# []

# 练习问答题
# 步长为 5，从 3 到 99：序列是 3, 8, 13, ..., 98
# 用公式计算：(stop - start) / step 需要向下取整
count = len(range(3, 100, 5))
print("len(range(3, 100, 5)) =", count)     # 20
# 验证一下具体内容
print(list(range(3, 100, 5)))
