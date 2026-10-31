# matrix.py —— 两种造矩阵的写法
good = [[0] * 3 for _ in range(2)]     # 每行都是新建的列表
bad = [[0] * 3] * 2                    # 复制的是同一个列表的引用

good[0][0] = 1
bad[0][0] = 1

print("good", good)
print("bad ", bad)
print("bad[0] is bad[1] →", bad[0] is bad[1])
