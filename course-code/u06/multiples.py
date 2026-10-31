# multiples.py —— 用 while 输出倍数

# 1）1–50 之间所有 7 的倍数
print("--- 7 的倍数 ---")
n = 1
while n <= 50:
    if n % 7 == 0:
        print(n)
    n += 1

# 更简洁的等价写法：用 while 变量本身就以 7 为步长
print("--- 7 的倍数（步长版）---")
n = 7
while n <= 50:
    print(n)
    n += 7

# 2）1–50 之间同时是 3 和 5 的倍数（即 15 的倍数）
print("--- 同时是 3 和 5 的倍数 ---")
n = 1
while n <= 50:
    if n % 3 == 0 and n % 5 == 0:
        print(n)
    n += 1
# 输出：15 30 45

# 也可以用"lcm"（最小公倍数）的思路：15 的倍数就是答案
print("--- 15 的倍数 ---")
n = 15
while n <= 50:
    print(n)
    n += 15

# 顺带做一个和：1–100 之间所有 7 的倍数之和
total = 0
n = 7
while n <= 100:
    total += n
    n += 7
print(f"7 的倍数之和：{total}")   # 7+14+...+98 = 735
