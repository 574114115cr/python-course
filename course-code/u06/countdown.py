# countdown.py —— while 的经典应用：倒计时

# 1）从 5 数到 1
count = 5
while count > 0:
    print(count)
    count -= 1
print("起飞！")

# 2）模拟"游戏存档"：一个简单的登录重试流程
print("\n--- 登录重试 ---")
max_attempts = 3
current_attempt = 0
correct_password = "python2024"

while current_attempt < max_attempts:
    password = input("请输入密码：")
    current_attempt += 1# 先计数，这样"最后一次"的判断才准

    if password == correct_password:
        print("登录成功！")
        break
    else:
        remaining = max_attempts - current_attempt
        if remaining > 0:
            print(f"密码错误，还有 {remaining} 次机会")
        else:
            print("机会用尽，账户已锁定")

# 3）===== 调试死循环的救命技巧 =====
print("\n--- 死循环调试法 ---")
# 如果 while 停不下来，先在循环体第一行加 print 观察变量：
i = 0
while i < 3:
    print(f"当前 i = {i}")   # 关键：这行告诉你 i 到底变没变
    i += 1
# 如果输出一直是"当前 i = 0"，说明你根本没写 i += 1，
# 或者写在了缩进错误的位置（比如写到了 while 外面）。
