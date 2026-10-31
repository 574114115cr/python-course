# truthy.py —— bool 转换的真相表

values = [0, 1, 0.0, -1, "", "0", "False", [], [0], None]

# Python 判断"真/假"的唯一规则：空或零为假，其余为真
for value in values:
    print(f"bool({value!r:>10}) = {bool(value)}")

print()
print("=== 逐条解释 ===")
print("bool(0)      = False —— 整数零被视为假")
print("bool(1)      = True  —— 非零整数为真")
print("bool(0.0)    = False —— 浮点零同样为假")
print("bool(-1)     = True  —— 负数也是非零，为真")
print('bool("")     = False —— 空字符串为假')
print('bool("0")   = True  —— 字符串 \"0\" 非空，内容不是 \"\" 所以为真')
print('bool("False") = True —— 同上，非空字符串一律为真')
print("bool([])     = False —— 空列表为假")
print("bool([0])    = True  —— 列表里有一个元素，不为空，为真")
print("bool(None)   = False —— None 表示\"什么都没有\"，为假")
