# copy_demo.py —— 三种"复制"的对照
a = [1, 2, 3]
b = a            # 只是多一个名字，不是复制
c = a[:]         # 切片复制：新的外层列表
d = a.copy()     # 同 c

a.append(4)

print("a", a)                  # [1, 2, 3, 4]
print("b", b)                  # [1, 2, 3, 4]  ← 跟着变
print("c", c)                  # [1, 2, 3]     ← 没变
print("d", d)                  # [1, 2, 3]     ← 没变
print("b is a", b is a, "| c is a", c is a)

# 但切片复制只复制第一层
grid = [[1, 2], [3, 4]]
g2 = grid[:]
g2[0][0] = 99
print("grid", grid)            # [[99, 2], [3, 4]]  ← 原列表也被改了
print("g2  ", g2)
