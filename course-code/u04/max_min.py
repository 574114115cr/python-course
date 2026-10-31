# max_min.py —— 三个数中找最大值和最小值

a = 3
b = 9
c = 5

# 思路：先假设 a 是最大的和最小的，再逐一挑战
max_value = a    # 初始假设
min_value = a

if b > max_value:
    max_value = b
if c > max_value:
    max_value = c

if b < min_value:
    min_value = b
if c < min_value:
    min_value = c

print(f"最大值: {max_value}，最小值: {min_value}")

# 顺带输出中间值：三个数之和减去最大和最小
middle = a + b + c - max_value - min_value
print(f"中间值: {middle}")

# 换一组数据验证
a, b, c = -5, 2, -5
max_value = max(min_value := a, b, c)   # 顺带展示海象运算符，可省略
print(f"-5, 2, -5 -> 最大 {max_value}，最小 {min_value}")
