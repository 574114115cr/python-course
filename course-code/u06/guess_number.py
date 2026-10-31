# guess_number.py —— 完整的猜数字游戏

import random


def play_guess_number():
    """启动猜数字游戏主流程。"""
    # 生成 1–100 的随机整数
    secret = random.randint(1, 100)
    count = 0
    history = []             # 记录猜测历史，方便复盘

    print("=" * 40)
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个 1 到 100 之间的整数")
    print("输入 'quit' 可以随时退出")
    print("=" * 40)

    # ===== 标准骨架：while True + 唯一出口 break =====
    while True:
        raw = input("请输入你的猜测（1-100）：")

        # 退出通道：用户主动结束
        if raw in ["quit", "q", "exit"]:
            print("游戏已退出，答案是", secret)
            print("你的猜测记录：", history)
            break

        # 把字符串转成整数，转换失败就重新问
        try:
            guess = int(raw)
        except ValueError:
            print(f"'{raw}' 不是有效数字，请重新输入")
            continue

        # 超出范围提示
        if guess < 1 or guess > 100:
            print("请输入 1 到 100 之间的数字")
            continue

        count += 1
        history.append(guess)

        if guess < secret:
            print(f"太小了，再大一点（第 {count} 次猜测）")
        elif guess > secret:
            print(f"太大了，再小一点（第 {count} 次猜测）")
        else:
            print("=" * 40)
            print(f"恭喜你猜对了！答案就是 {secret}")
            print(f"你一共猜了 {count} 次")
            print(f"你的猜测记录：{history}")
            print("=" * 40)
            break                   # 猜对了，唯一的正常出口

    return count


# 游戏结束后统计一下平均猜测次数
counts = [play_guess_number()]
print(f"本次游戏共猜了 {counts[0]} 次")
