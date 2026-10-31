# text_pipeline.py —— 字符串方法接力，全过程不修改原变量

text = "   python is FUN   "

# ① 原样输出：普通 print 看不出首尾空格，用 repr() 可以看清
print(repr(text))

# ② 只去掉两端空白
print(repr(text.strip()))

# ③ 再转小写
print(text.strip().lower())

# ④ 再每个单词首字母大写
print(text.strip().title())

# ⑤ 处理完之后的长度
print(len(text.strip()))

# 验证：原字符串自始至终没有被改动
print("原变量仍然是：", repr(text))

# 如果想让 text 本身保存处理结果，必须显式赋值
# text = text.strip().title()
# print(text)
