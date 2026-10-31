# copy_semantics.py —— 函数里修改参数，到底影响不影响原数据

# ===== 情况1：传整数 -> 不影响原变量 =====
def add_one(n):
    n = n + 1         # 只是让参数 n 指向了一个新整数
    print(f"  函数内 n = {n}")


age = 10
add_one(age)
print(f"  函数外 age = {age}\n")     # 10  没变

# ===== 情况2：传字符串 -> 不影响 =====
def shout(word):
    word = word.upper()   # 返回了新字符串，参数指向了它
    print(f"  函数内 word = {word}")


name = "tom"
shout(name)
print(f"  函数外 name = {name}\n")   # tom  没变

# ===== 情况3：传列表 -> 会影响原列表！=====
def add_item(items):
    items.append("新元素")     # 直接改的是同一份列表
    print(f"  函数内 items = {items}")


fruits = ["苹果", "香蕉"]
add_item(fruits)
print(f"  函数外 fruits = {fruits}\n")   # ['苹果', '香蕉', '新元素']  变了！

# ===== 情况4：传字典 -> 同样会影响 =====
def set_name(profile):
    profile["name"] = "李四"    # 改的是同一个字典


user = {"name": "张三", "age": 20}
set_name(user)
print(f"  函数外 user = {user}\n")       # name 变成了李四

# ===== 三种修复方案 =====
fruits = ["苹果", "香蕉"]

# 方案1：函数内自己造副本（推荐）
def safe_append(items):
    items = items[:]      # 先复制一份，只动副本
    items.append("新元素")
    return items


result = safe_append(fruits)
print(f"方案1：原列表 {fruits}，新列表 {result}\n")

# 方案2：调用时传副本
def append_direct(items):
    items.append("新元素")


result = fruits[:]        # 调用方给副本
append_direct(result)
print(f"方案2：原列表 {fruits}，新列表 {result}\n")

# 方案3：用 + 产生新列表，天然不改原数据
def append_pure(items):
    return items + ["新元素"]


result = append_pure(fruits)
print(f"方案3：原列表 {fruits}，新列表 {result}")
