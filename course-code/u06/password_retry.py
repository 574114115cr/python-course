# password_retry.py —— 用 while...else 实现重试机制

correct_password = "py2026"
max_attempts = 3
attempt = 0

while attempt < max_attempts:
    password = input(f"请输入密码（还可尝试 {max_attempts - attempt} 次）：")
    attempt += 1

    # 主动放弃
    if password == "exit":
        print("你选择了放弃本次输入")
        break

    if password == correct_password:
        print(f"密码正确！你在第 {attempt} 次尝试时成功登录")
        break
    else:
        print("密码错误")
else:
    # 只有循环正常走完（尝试满 3 次都没 break）才会到这里
    print("-" * 30)
    print("错误次数已达上限，账户被锁定")
    print("-" * 30)

# ===== 对比：如果不用 while...else，长什么样 =====
# 需要一个额外的标志位来记住"是不是正常走完的"
# attempt < max_attempts 这个循环结束后，
# 如果 attempt == max_attempts，说明三次都错了
attempt2 = 0
while attempt2 < max_attempts:
    pwd = input("密码：")
    if pwd == "exit":
        break
    if pwd == correct_password:
        print("成功")
        break
    attempt2 += 1

if attempt2 == max_attempts:
    print("账户锁定")
# 结论：while...else 把"是否正常结束"这件事表达得干净得多
