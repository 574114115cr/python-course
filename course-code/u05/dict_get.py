# dict_get.py —— .get() 的价值

scores = {"语文": 90, "数学": 85}

# 方括号取值：键不存在直接崩
print(scores["语文"])# 90
# print(scores["英语"])   # KeyError: '英语'

# .get() 取值：键不存在返回 None
print(scores.get("语文"))    # 90
print(scores.get("英语"))    # None
# 注意：返回 None 说明"键不存在"，
# 也可能说明"键存在但值就是 None"。要区分用 in

# .get() 带默认值
print(scores.get("英语", 0))            # 0
print(scores.get("英语", "缺考"))         # 缺考
print(scores.get("语文", 0))            # 90  键存在时忽略默认值

# 判断键是否存在
print("英语" in scores)         # False
print("语文" in scores)         # True

# 区分"不存在"和"值为 None"
data = {"a": None}
print(data.get("a"))                # None
print("a" in data)                  # True   键存在，只是值是 None
print(data.get("b", "没有这个键"))    # 没有这个键

# ===== .get() 链式访问：处理嵌套数据的利器 =====
users = {"u1": {"name": "小明", "age": 18}}

# 传统写法：啰嗦
if "u1" in users:
    if "name" in users["u1"]:
        name = users["u1"]["name"]
print(name)

# .get() 链式写法：简洁且永不崩溃
name = users.get("u9", {}).get("name", "查无此人")
print(name)      # 查无此人
# 关键在那个 {} —— u9 不存在时给一个空字典，
# 这样后面的 .get("name") 就有东西可操作，链条不断裂
