# users.py —— 列表套字典：遍历、分组、筛选
users = [
    {"name": "alice", "age": 30, "city": "上海"},
    {"name": "bob",   "age": 17, "city": "北京"},
    {"name": "carol", "age": 24, "city": "上海"},
]

# ① 逐条读取 + 条件判断
for u in users:
    status = "成年" if u["age"] >= 18 else "未成年"
    print(f"{u['name']}（{u['city']}）{u['age']} 岁 · {status}")

# ② 按城市分组：字典的值是列表
by_city = {}
for u in users:
    city = u["city"]
    if city not in by_city:        # 第一次遇到这个城市，先建空列表
        by_city[city] = []
    by_city[city].append(u["name"])
print("按城市", by_city)

# ③ 从字典列表里挑出符合条件的名字
adults = [u["name"] for u in users if u["age"] >= 18]
print("成年人", adults)
