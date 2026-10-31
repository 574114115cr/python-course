# while_basics.py —— while 循环的基本形态

# 1）最基础的计数循环
count = 0
while count < 5:
    print(f"第 {count} 次")
    count += 1# 关键：这行让条件最终变假，否则死循环
print("循环结束，count =", count)

# 2）条件一开始就为假 -> 循环体一次都不执行
count = 100
while count < 5:
    print("这句话永远不会打印")
    count += 1
print("因为条件为假，直接跳过了循环体")

# 3）条件为真就停（注意 != 的用法）
password = ""
while password != "python123":
    password = input("请输入密码：")
print("密码正确，欢迎！")

# 4）条件本身是数字：Python 允许（0 为假，非 0 为真）
n = 3
while n:
    print(n)
    n -= 1
print("n 减到 0，循环自动结束")

# ===== 死循环演示（请务必自己跑一次看看）=====
# count = 0
# while count < 3:
#     print("停不下来", count)
#     # 忘了写 count += 1，永远停不了
# 按 Ctrl+C 可以强制中断
