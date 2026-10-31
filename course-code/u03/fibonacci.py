# fibonacci.py —— 用列表生成斐波那契数列

fib = [1, 1]
print("初始：", fib)         # [1, 1]

# 循环 13 次，一共得到 15 个数
for i in range(13):
    next_number = fib[-1] + fib[-2]    # 最后两个数相加
    fib.append(next_number)

print("前 15 个斐波那契数：")
print(fib)
# [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

# 打印成更好看的格式
print("用空格分隔：")
for number in fib:
    print(number, end=" ")
print()

# 顺带验证：斐波那契数列有个性质，第 n 项等于它前面两项之和
print("fib[10] + fib[11] =", fib[10] + fib[11], "，等于 fib[12] =", fib[12])
