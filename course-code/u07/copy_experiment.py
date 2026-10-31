# copy_experiment.py —— 副本语义验证实验

print("===== 实验1：传整数 =====")
num = 10
print(f"调用前：num = {num}")


def modify_int(n):
    n = n + 1          # 只是让参数指向了新整数，原数据没动
    print(f"  函数内 n = {n}")


modify_int(num)
print(f"调用后：num = {num}\n")     # 10  没变

print("===== 实验2：传字符串 =====")
text = "abc"
print(f"调用前：text = {text}")


def modify_str(s):
    s = s.upper()      # 返回新字符串，参数指向了它
    print(f"  函数内 s = {s}")


modify_str(text)
print(f"调用后：text = {text}\n")   # abc  没变

print("===== 实验3：传列表 =====")
fruits = ["苹果"]
print(f"调用前：fruits = {fruits}")


def modify_list(items):
    items.append("香蕉")    # 直接改的就是同一份列表
    print(f"  函数内 items = {items}")


modify_list(fruits)
print(f"调用后：fruits = {fruits}\n")  # ['苹果', '香蕉']  变了！

print("===== 实验4：传字典 =====")
user = {"name": "张三"}
print(f"调用前：user = {user}")


def modify_dict(d):
    d["name"] = "李四"     # 改的是同一个字典
    print(f"  函数内 d = {d}")


modify_dict(user)
print(f"调用后：user = {user}\n")     # name 变成李四

print("===== 规律总结 =====")
print("整数、浮点数、字符串、布尔 -> 不可变类型 -> 函数内修改不影响原变量")
print("列表、字典 -> 可变类型 -> 函数内修改会直接影响原数据")

print("\n===== 修复方案 =====")
fruits = ["苹果"]


def safe_modify_list(items):
    """安全版：先造副本再修改，返回新列表。"""
    items = items[:]      # 关键一行：造一份独立的副本
    items.append("香蕉")
    return items


result = safe_modify_list(fruits)
print(f"原列表：{fruits}")# ['苹果']没变
print(f"新列表：{result}")  # ['苹果', '香蕉']

# 生活化总结：
# 传整数像"递进去一瓶牛奶"，厨房贴自己的标签，你的牛奶没动。
# 传列表像"递进去一盘菜"，厨房直接吃你的菜并加了料，你的盘子内容变了。
