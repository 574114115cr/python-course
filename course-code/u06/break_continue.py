# break_continue.py —— 两个跳出关键字

# break：跳出整个循环
print("--- break 演示 ---")
for i in range(10):
    if i == 3:
        print("遇到 3，停止遍历")
        break            # 直接跳出，后面 4~9 都不再处理
    print(i)

# continue：跳过本轮
print("\n--- continue 演示 ---")
for i in range(10):
    if i % 2 == 0:
        continue         # 偶数跳过，只打印奇数
    print(i)

# 两者配合：过滤并求和
print("\n--- 综合运用 ---")
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = 0
for n in numbers:
    if n < 3:
        continue         # 小于 3 的不要
    if n > 8:
        break            # 大于 8 就停，反正后面只会更大
    total += n
print("3 到 8 的总和：", total)   # 3+4+5+6+7+8 = 33

# 常见错误：continue 之后的代码永远执行不到
print("\n--- 常见错误 ---")
for i in range(5):
    if i == 2:
        continue
        print("这里永远不会执行，因为 continue 已经跳到下一轮了")
    print(i)

# ===== continue 在 while 里的一个重要用途：输入校验 =====
print("\n--- 输入校验（关键模式）---")
while True:
    age = input("请输入你的年龄：")
    # 如果不是纯数字，int() 会报 ValueError
    try:
        age = int(age)
        break            # 转换成功，说明输入有效，跳出循环
    except ValueError:
        print("输入的不是有效整数，请重新输入")
# try/except 属于单元 9 的内容，但这个模式先感受一下
