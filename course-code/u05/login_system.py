# login_system.py —— 简易登录系统

# 用户名 -> 密码
users = {
    "admin": "123456",
    "root": "root888",
    "user": "abc123",
}

# 允许重试 3 次
for attempt in range(1, 4):
    print(f"--- 第 {attempt} 次尝试（共 3 次机会）---")
    username = input("请输入用户名：")
    password = input("请输入密码：")

    # 第一步：判断用户名是否存在
    if username not in users:
        print(f"该用户不存在。\n可用用户名：{list(users.keys())}")

    # 第二步：用户名存在，再判断密码
    elif users[username] == password:
        print(f"登录成功，欢迎 {username}！")
        break# 登录成功，用 break 跳出循环

    # 第三步：密码错误
    else:
        print("密码错误")

    # 如果三次都失败，会走到这里
else:
    print("三次机会已用完，账户可能被锁定")
