# dict_methods.py —— 字典常用方法速查

config = {"host": "localhost", "port": 8080, "debug": True}

# get：安全取值
print(config.get("port"))            # 8080
print(config.get("timeout", 30))     # 30

# pop：取值并删除
port = config.pop("port")
print(f"取出的端口：{port}，剩余：{config}")

# setdefault：键不存在时才设置并返回
config.setdefault("timeout", 30)
print("timeout：", config["timeout"])    # 30  新增了
config.setdefault("timeout", 60)
print("再设一次：", config["timeout"])# 30  没变，因为已存在

# update：用另一个字典批量合并
config.update({"host": "127.0.0.1", "level": "info"})
print("更新后：", config)

# 键和值的视图
print("所有键：", list(config.keys()))
print("所有值：", list(config.values()))
print("所有对：", list(config.items()))

# 计数小技巧：用字典统计出现次数
# （这比 collections.Counter 更基础，务必掌握）
fruits = ["苹果", "香蕉", "苹果", "橙子", "苹果", "香蕉"]
counts = {}
for fruit in fruits:
    if fruit in counts:
        counts[fruit] += 1# 已出现过，计数 +1
    else:
        counts[fruit] = 1     # 第一次出现，计数为 1
print("统计结果：", counts)   # {'苹果': 3, '香蕉': 2, '橙子': 1}

# 反向字典：值 -> 键
scores = {"小明": 95, "小红": 88, "小刚": 72}
name_by_score = {score: name for name, score in scores.items()}
print("反向字典：", name_by_score)   # {95: '小明', 88: '小红', 72: '小刚'}
