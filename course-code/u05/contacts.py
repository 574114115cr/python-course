# contacts.py —— 通讯录的基本操作

contacts = {
    "小明": "13800138000",
    "小红": "13900139000",
}

# 1）安全取不存在的键
print("小刚的电话：", contacts.get("小刚", "未知"))   # 未知

# 2）方括号取已知存在的键
print("小红的电话：", contacts["小红"])    # 13900139000

# 3）用 in 判断是否存在
print("小刚在通讯录里吗：", "小刚" in contacts)     # False
print("小明在通讯录里吗：", "小明" in contacts)     # True

# 4）新增
contacts["小刚"] = "13700137000"
print("新增后：", contacts)

# 5）遍历所有联系人和电话（用 items）
print("--- 通讯录 ---")
for name, phone in contacts.items():
    print(f"{name}: {phone}")

# 6）删除
del contacts["小红"]
print("删除小红后：", contacts)

# 顺带演示：也可以按名字筛选（比如只找出 13 开头的号码）
print("--- 号码以 138 开头的人 ---")
for name, phone in contacts.items():
    if phone.startswith("138"):
        print(f"{name}: {phone}")
