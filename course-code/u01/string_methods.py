# string_methods.py —— 字符串的"复印与改写"

name = "  ada lovelace  "

# .upper() / .lower() 大小写转换
print(name.upper())       # '  ADA LOVELACE  '
print(name.lower())       # '  ada lovelace  '

# .strip() 去掉两端空白（不会去掉中间的空格）
print(repr(name.strip()))# 'ada lovelace'  用 repr() 才能看清首尾有没有空格

# .title() 每个单词首字母大写
print(name.strip().title())   # 'Ada Lovelace'

# .len() 计算长度（算的是字符个数）
print(len(name.strip()))      # 12

# .count() 数某个字符出现几次
print("banana".count("a"))        # 3

# .replace() 替换
print("hello world".replace("world", "python"))   # 'hello python'

# 关键：上面所有方法都"没有改动" name
print(name)                    #  '  ada lovelace  '  ← 原字符串原封不动
print(type(name.strip()))      # <class 'str'>  返回的是一个新字符串

# 想真正保存结果，必须接住返回值
name = name.strip().title()
print(name)                    # 'Ada Lovelace'  ← 现在才是新值
