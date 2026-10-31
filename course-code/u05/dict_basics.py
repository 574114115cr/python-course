# dict_basics.py —— 字典的创建与访问

# 用 {} 创建字典，键值对之间用逗号分隔，键和值之间用冒号
user = {"name": "小明", "age": 18, "city": "杭州"}

print("字典：", user)
print("长度：", len(user))            # 3  键值对的数量
print("name 的值：", user["name"])# 小明
print("age 的值：", user["age"])       # 18

# 取不存在的键会报 KeyError
# print(user["phone"])  # KeyError: 'phone'

# 键可以是不同类型：字符串、数字、元组
mixed = {
    "name": "小明",
    100: "百",
    (116.4, 39.9): "北京坐标",
    True: "布尔键也可以",
}
print(mixed["name"])
print(mixed[100])
print(mixed[(116.4, 39.9)])
print(mixed[True])

# 但列表不能当键
# bad = {[1, 2]: "列表当键"}    # TypeError: unhashable type: 'list'
# 原因：列表可以修改内容，改了就找不到了

# 空字典
empty = {}
print("空字典长度：", len(empty))     # 0
print("空字典是假值吗：", bool(empty))   # False
