# while_else.py —— 循环正常结束才执行的 else

# 猜数游戏：猜对用 break，猜满次数落进 else
secret = 7
attempts = 3
guess = 0

while guess < attempts:
    answer = int(input("1-10 猜一个数："))
    if answer == secret:
        print("猜对了！")
        break                # 被 break 打断 -> else 不执行
    else:
        print("猜错了，再试一次")
        guess += 1
else:
    # 只有循环正常走完（没被 break）才会到这里
    print(f"{attempts} 次机会用完了，正确答案是 {secret}")

print("游戏结束")

# ===== 用同样的逻辑写个"密码强度检查" =====
password = "abc"

while len(password) < 8:
    print("密码太短，要求至少 8 位")
    break
else:
    print(f"密码长度合格：{'*' * len(password)}")

# short_password = "123"
# while len(short_password) < 8:
#     print("密码太短，要求至少 8 位")
#     break
# else:
#     print("长度合格")
