# dict_modify.py —— 遍历时能不能改字典

scores = {"语文": 90, "数学": 85, "英语": 78}

# 遍历过程中删除键值对 -> RuntimeError
# for key in scores:
#     if scores[key] < 80:
#         del scores[key]     # RuntimeError: dictionary changed size during iteration

# 正确做法一：先复制一份键的列表，再遍历副本
for key in list(scores.keys()):
    if scores[key] < 80:
        del scores[key]
print("删除低于 80 的：", scores)   # {'语文': 90, '数学': 85}

# 正确做法二：用 .items() 复制元组列表
scores = {"语文": 90, "数学": 85, "英语": 78}
for key, value in list(scores.items()):
    if value < 80:
        del scores[key]
print("结果一样：", scores)         # {'语文': 90, '数学': 85}

# 修改键的值（不改变字典大小）是允许的
scores = {"语文": 90, "数学": 85}
for key in scores:
    if scores[key] < 90:
        scores[key] += 10
print("提分后：", scores)           # {'语文': 90, '数学': 95}
# 注意：改值不改长度，所以不需要复制

# 翻面理解这个规则：
# 遍历是"照着名单念名字"，而删除会让名单页数变少，后面就念乱了。
# 但改名字内容不影响名单长度，所以是安全的。
