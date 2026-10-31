# convert_quiz.py —— 类型转换练习

s = "42"

print(int(s))    # 42    字符串 "42" -> 整数 42
print(float(s))  # 42.0  字符串 "42" -> 小数 42.0
print(str(s))    # 42字符串 -> 字符串（内容看起来一样，但类型是 str）
print(bool(s))   # True  非空字符串一律为真

# int("hello") 会抛出 ValueError: invalid literal for int() with base 10: 'hello'
# 原因：Python 无法把 "hello" 理解成一个十进制数字，所以在转换时直接报错。
# 如果想"转换失败也不崩溃"，需要用 try/except 包裹：
#   try:
#       print(int("hello"))
#   except ValueError:
#       print("这个字符串不是合法的整数")
# 单元 9 会正式讲 try/except 的写法。
