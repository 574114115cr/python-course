# eq_vs_is.py —— 什么时候用 ==，什么时候用 is

# == 比较内容
print("hello" == "hello")        # True
print(1000 == 1000)              # True

# is 比较对象身份
first = "hello"
second = "he" + "llo"
print(first == second)           # True  内容一样
print(first is second)           # False 可能是不同的两个对象

# 小整数是"缓存"的，恰好会命中同一个对象
a = 1000
b = 1000
print(a is b)                    # False 大整数不共享
c = 100
d = 100 + 0
print(c is d)                    # True  小整数被 Python 缓存了

# 唯一必须用 is 的场景：判断 None
value = None
if value is None:
    print("value 是 None")
if value is not None:
    print("这句不会执行")

# 结论：
# 比较内容   -> 用 ==
# 判断空值   -> 用 is None / is not None
