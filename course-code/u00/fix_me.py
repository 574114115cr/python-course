# fix_me.py —— 修复后的正确版本
# 原代码有 3 个错误：两处右括号缺失（SyntaxError），一处靠报错才能发现

print("1 加 2 等于 3")   # 错误 1：结尾少了右括号 -> SyntaxError
x = 1 + 2               # 这一行本身是对的
print("1 加 2 等于", x)  # 错误 2：结尾少了右括号 -> SyntaxError

# 顺带说明：Python 中 x 这个名字必须在使用它之前就已经被赋值，
# 如果把 print 移到 x = 1 + 2 之前，就会报 NameError。
# 这属于"使用顺序"问题，不是语法问题。
