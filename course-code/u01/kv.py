# kv.py —— 一行配置拆成字典，再按 key 排序输出
raw = "name=张三;age=18;city=北京"

d = {}
for pair in raw.split(";"):
    k, v = pair.split("=", 1)          # 只拆第一个 =，值里再有 = 也不会被切碎
    d[k] = v

print(d)
print(" | ".join(f"{k}={v}" for k, v in sorted(d.items())))
print(f"{d['name']} 今年 {int(d['age'])} 岁")
