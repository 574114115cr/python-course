# flag_demo.py —— 用标志位组织复杂退出条件

# 问题：如果密码错误 和 用户名不存在 都要跳出，怎么写？
username = "admin"
password = "wrong"

#===== 做法一：标志位（推荐，可读性最好）=====
username_ok = False
password_ok = False

if username == "admin":
    username_ok = True
if password == "123456":
    password_ok = True

if username_ok and password_ok:
    print("登录成功")
else:
    print("用户名或密码错误")

# ===== 做法二：逻辑运算符（更简洁）=====
if username == "admin" and password == "123456":
    print("登录成功")
else:
    print("用户名或密码错误")

# ===== 标志位的真正用武之地：在循环里 =====
numbers = [10, 25, 3, 47, 8, 91]
target = 47

# 找出目标值的下标，找不到返回 -1
found_index = -1

# 标志位：记录"找到了没有"
found = False

for i, n in enumerate(numbers):
    if n == target:
        found_index = i
        found = True
        break            # 找到了就停，不必再往下看

# 用标志位决定后续走哪条路
if found:
    print(f"在索引 {found_index} 处找到了 {target}")
else:
    print(f"列表中没有 {target}")

# 也可以不用标志位，直接判断 found_index != -1
print(f"（等价判断）索引是 {found_index}")
