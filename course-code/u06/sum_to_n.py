# sum_to_n.py —— while 与 for 两种写法的对比

n = int(input("请输入一个正整数 n："))

# ===== while 写法 =====
total = 0
i = 1
while i <= n:
    total += i
    i += 1
print(f"while 写法：1 到 {n} 的和是 {total}")

# ===== for 写法（更简洁，因为次数已知）=====
total2 = sum(range(1, n + 1))
print(f"for 写法：1 到 {n} 的和是 {total2}")

# ===== 另一种 while 写法：用累加器技巧 =====
total3 = 0
counter = n
while counter > 0:
    total3 += counter
    counter -= 1
print(f"倒着加：{total3}")

# 验证几个固定答案
for n in [1, 5, 10, 100]:
    print(f"n={n} 时和为 {sum(range(1, n + 1))}")
# n=1 -> 1, n=5 -> 15, n=10 -> 55, n=100 -> 5050
