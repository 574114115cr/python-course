# json_demo.py —— 用 JSON 保存和读取结构化数据

import json

# 准备一个包含各种类型的数据
data = {
    "name": "小明",
    "age": 18,
    "score": 92.5,
    "is_student": True,
    "hobbies": ["篮球", "编程", "音乐"],
    "address": {"city": "杭州", "zip": "310000"},
    "notes": None,
}

# ===== Python 对象 -> JSON 字符串 =====
# 默认中文会变成 \uXXXX，可读性差
print("--- 默认 dumps ---")
print(json.dumps(data)[:80])

# ensure_ascii=False 让中文正常显示
print("\n--- ensure_ascii=False ---")
text = json.dumps(data, ensure_ascii=False)
print(text)

# indent=2 格式化输出，人和机器都好看
print("\n--- indent=2（会保存到文件的样子）---")
pretty = json.dumps(data, ensure_ascii=False, indent=2)
print(pretty)

# ===== JSON 字符串 -> Python 对象 =====
# 反序列化，还原成字典
back = json.loads(text)
print("\n--- 解析回来 ---")
print(f"类型：{type(back).__name__}")
print(f"姓名：{back['name']}")
print(f"爱好：{back['hobbies']}")
print(f"城市：{back['address']['city']}")
print(f"备注：{back['notes']}")

# ===== 读写 JSON 文件 =====
filename = "data.json"

# 写
with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\n已写入 {filename}")

# 读
with open(filename, "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(f"从文件读回来的姓名：{loaded['name']}")
print(f"类型还是 dict吗：{type(loaded).__name__}")
print(f"爱好列表：{loaded['hobbies']}")

# 验证往返一致
print(f"往返一致：{loaded == data}")

# ===== JSON 语法要点 =====
# 1）JSON 的 true/false/null 全是小写，和 Python 不同
# 2）JSON 对象的键必须是双引号的字符串
# 3）JSON 不支持注释
# 4）JSON 不支持元组和集合，元组会变成列表

# 手写一个 JSON 字符串测试
manual = '{"name": "小红", "age": 22, "tags": ["a", "b"]}'
parsed = json.loads(manual)
print(f"\n手动 JSON 解析：{parsed}")

# 元组变列表的演示
with_tuple = {"point": (1, 2)}
print(f"元组被转成：{json.dumps(with_tuple)}")      # [1, 2]

import os
os.remove(filename)
