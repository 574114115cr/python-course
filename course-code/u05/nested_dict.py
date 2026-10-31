# nested_dict.py —— 嵌套字典：真实数据的形态

users = {
    "u1": {
        "name": "小明",
        "age": 18,
        "skills": ["Python", "SQL"],
    },
    "u2": {
        "name": "小红",
        "age": 22,
        "skills": ["Java", "Python"],
    },
    "u3": {
        "name": "小刚",
        "age": 25,
        "skills": ["C++"],
    },
}

# 连续取值：直接按层往下取
print("u1 的名字：", users["u1"]["name"])
print("u2 的年龄：", users["u2"]["age"])

# 安全取值
print("u9 的名字：", users.get("u9", {}).get("name", "查无此人"))

# 遍历两层：外层 uid 和 info，内层再用 info 的键
for uid, info in users.items():
    print(f"【{uid}】{info['name']}，{info['age']} 岁")

# 提取所有人的名字
all_names = [info["name"] for uid, info in users.items()]
print("所有人：", all_names)

# 筛选：谁会Python
python_users = [
    info["name"]
    for uid, info in users.items()
    if "Python" in info["skills"]
]
print("会 Python 的：", python_users)      # ['小明', '小红']

# 统计平均年龄
total_age = 0
for uid, info in users.items():
    total_age += info["age"]
average = total_age / len(users)
print(f"平均年龄：{average:.1f} 岁")# 21.7 岁

# 找出技能最多的用户
most_skilled = ""
max_count = 0
for uid, info in users.items():
    if len(info["skills"]) > max_count:
        max_count = len(info["skills"])
        most_skilled = info["name"]
print(f"技能最多的是{most_skilled}，有 {max_count} 项")
