# logic_ops.py —— and / or / not 与短路求值

age = 20
income = 8000
is_student = False

# and：全部为真才为真
print(age >= 18 and income >= 3000)         # True
print(age >= 18 and income >= 10000)        # False
# or：有一个为真就为真
print(age < 18 or income >= 3000)           # True
# not：取反
print(not is_student)                       # True

# ===== 短路求值：真实的安全价值 =====
numbers = [5, 8, 13]

# 安全写法：先问"长度够不够"，再问"内容是什么"
if len(numbers) > 0 and numbers[0] == 5:
    print("第一个数是 5")

# 危险写法：先访问元素，空列表直接崩溃
empty = []
# if empty[0] == 5 and len(empty) > 0:
#     print("这行永远不会安全执行")

# 正确演示：对比两个空列表
print("--- 短路求值演示 ---")
if empty and empty[0] == 5:
    print("第一个数是 5")
else:
    print("列表为空，跳过检查（短路了，没有访问 empty[0]）")

# and / or 可以直接返回操作数本身，不只返回布尔值
print("--- or 的一个实用技巧 ---")
name = ""
display_name = name or "匿名用户"# 空字符串为假，所以取了右边
print("显示名：", display_name)

real_name = "小明"
print("显示名：", real_name or "匿名用户")   # 小明

# 这就是单元 9 里写文件时的常见写法：
# content = text or "默认内容"
