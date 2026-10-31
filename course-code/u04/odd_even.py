# odd_even.py —— 判断奇偶，只用一个 if

number = 7

# 一个 if + else 就够了，不需要两个独立的 if
if number % 2 == 0:
    print(f"{number} 是偶数")
else:
    print(f"{number} 是奇数")

# 注意：% 是取余运算符，任意数都能用它做奇偶判断
#   正奇数 % 2 == 1，正偶数 % 2 == 0
#   负数也能正确处理：-7 % 2 == 1  （Python 的 % 总是非负）
print("-7 是奇数吗：", -7 % 2 == 1)      # True

# 反过来说：不要写if number % 2: 这种写法，
# 虽然结果对（0 是假、1 是真），但可读性差，别人看不出你的意图。
