# dict_traverse.py —— keys / values / items

user = {"name": "小明", "age": 18, "city": "杭州"}

# 1）遍历键 —— 直接 for 就是遍历键
print("--- 遍历键 ---")
for key in user:
    print(key)
for key in user.keys():    # 等价写法，更显式
    print(key)

# 2）遍历值
print("--- 遍历值 ---")
for value in user.values():
    print(value)

# 3）遍历键值对 —— 最常用
print("--- 遍历键值对 ---")
for key, value in user.items():
    print(f"{key}: {value}")

# 常见坑：for item in user 拿到的是键，不是键值对
print("--- 陷阱演示 ---")
for item in user:
    print(f"item = {item}")
# 输出的是 name / age / city，不含值

# 想同时拿到键和值，必须用 items()
for item in user.items():
    print(f"item = {item}")        # ('name', '小明') 这种元组形式

# 综合运用：统计每个键的值是数字还是字符串
for key, value in user.items():
    print(f"{key} 的类型是{type(value).__name__}")
