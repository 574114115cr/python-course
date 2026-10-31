# interactive_skeleton.py —— 所有交互程序的通用骨架

# ===== 骨架 1：菜单循环 =====
# while True + break + continue 的完整组合
while True:
    print("\n===== 简易计算器 =====")
    print("1. 加法")
    print("2. 减法")
    print("3. 退出")

    choice = input("请选择操作：")

    if choice == "3":
        print("再见！")
        break# 唯一的出口：用户要求退出

    if choice not in ["1", "2"]:
        print("无效的选项，请重新输入")
        continue             # 回到循环开头，菜单重新打印

    a = float(input("请输入第一个数："))
    b = float(input("请输入第二个数："))

    if choice == "1":
        print(f"结果：{a + b}")
    else:
        print(f"结果：{a - b}")

print("循环外的代码，只有 break 出来才会执行")

# ===== 骨架 2：多条退出路径 =====
# 三个不同的条件都要能退出循环，用标志位最清晰
attempts_left = 3
locked = False

for i in range(attempts_left):
    print(f"你还有 {attempts_left - i} 次机会")
    answer = input("输入 'quit' 可以放弃：")

    if answer == "quit":
        print("你选择了放弃")
        break
    if answer != "yes":
        print("答案错误")
        continue

    print("回答正确！")
    locked = True
    break
else:
    print("机会用完，锁定账户")

if locked:
    print("=== 已解锁 ===")
