# dict_crud.py —— 字典的增删改查

scores = {"语文": 90, "数学": 85}

# 新增：键不存在时赋值 = 添加一对
scores["英语"] = 78
print("新增后：", scores)      # {'语文': 90, '数学': 85, '英语': 78}
print("长度：", len(scores))   # 3

# 修改：键已存在时赋值 = 改值（覆盖）
scores["数学"] = 92
print("修改后：", scores)      # {'语文': 90, '数学': 92, '英语': 78}
print("长度依然是：", len(scores))   # 3，没有变长！

# 删除：用 del
del scores["英语"]
print("删除后：", scores)      # {'语文': 90, '数学': 92}

# 删除的第二种写法：pop()，能拿到被删的值
removed = scores.pop("语文")
print("pop 出来的分数：", removed)     # 90
print("现在剩下：", scores)             # {'数学': 92}

# popitem()：删除最后加入的那一对，返回 (键, 值) 元组
scores = {"语文": 90, "数学": 92}
pair = scores.popitem()
print("popitem 返回：", pair)         # ('数学', 92)

# 清空
scores.clear()
print("清空后：", scores, "长度", len(scores))   # {} 长度 0
