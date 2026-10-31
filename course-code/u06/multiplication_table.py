# multiplication_table.py —— 嵌套 while 循环

# 完整九九乘法表
print("--- 完整九九乘法表 ---")
i = 1
while i <= 9:
    j = 1
    while j <= i:                     # 内层：每行输出 i 个式子
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()# 换行，让下一个 i 另起一行
    i += 1

# 只输出前 3 行
print("\n--- 前 3 行 ---")
i = 1
while i <= 3:
    j = 1
    while j <= i:
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()
    i += 1

# ===== 嵌套循环的经典 bug：内层变量没重置 =====
# 下面这段会输出错误结果
# i = 1
# while i <= 3:
#     j = 1
#     while j <= i:
#         print(j, end=" ")
#         j += 1
#     print()
#     # 忘记写 j = 1，第二轮 i=2 时 j 已经是 2，循环一次都不执行
#     i += 1

# 正确写法：内层循环的变量必须在每轮外层循环里重新初始化
print("\n--- 固定版---")
i = 1
while i <= 3:
    j = 1                 # 关键：每轮外层循环开始时重置
    while j <= i:
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()
    i += 1

# 观察输出：
# 1×1=1
# 1×2=2   2×2=4
# 1×3=3   2×3=6   3×3=9
