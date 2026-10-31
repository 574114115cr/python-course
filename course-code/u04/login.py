# login.py —— 模拟登录

# 用字典存用户名和密码（字典会在单元 5 正式讲，这里先直接用）
correct_username = "admin"
correct_password = "123456"

# 用 input() 读取用户输入
username = input("请输入用户名：")
password = input("请输入密码：")

# 两个条件用 and 连接：必须同时正确
if username == correct_username and password == correct_password:
    print("登录成功，欢迎回来！")
else:
    # 不告诉用户"是用户名错了还是密码错了"，这是安全习惯
    print("用户名或密码错误")
