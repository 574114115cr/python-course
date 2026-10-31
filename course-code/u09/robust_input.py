# robust_input.py —— 健壮的用户输入处理

print("=== 读取 1-100 的整数 ===")

MAX_ATTEMPTS = 3
attempts = 0

while attempts < MAX_ATTEMPTS:
    raw = input("请输入 1-100 的整数：")
    attempts += 1
    try:
        value = int(raw)
    except ValueError as error:
        print(f"  '{raw}' 不是有效整数：{error}")
    else:
        # else 块：只有转换成功才会执行
        print(f"  转换成功：{value}")
        if 1 <= value <= 100:
            print(f"✓ 数字在有效范围内：{value}")
            break
        else:
            print(f"  {value} 不在 1-100 范围内，请重新输入")
    finally:
        print(f"  （第 {attempts}/{MAX_ATTEMPTS} 次尝试结束）")

print("\n=== 读取一个正数（float）===")

while True:
    try:
        raw = input("请输入一个正数：")
        price = float(raw)
    except ValueError as error:
        print(f"  '{raw}' 不是有效数字：{error}")
    except KeyboardInterrupt:
        # 关键：明确捕获 Ctrl+C，并优雅退出。
        # 这体现了"不要用裸 except"的价值 —— 裸 except 会把
        # KeyboardInterrupt 一起吞掉，导致 Ctrl+C 完全失效。
        print("\n检测到 Ctrl+C，正在退出...")
        raise           # 重新抛出，让程序正常结束
    else:
        if price > 0:
            print(f"✓ 有效正数：{price}")
            break
        print(f"  {price} 不是正数，请重新输入")
    finally:
        print("  （本次输入处理完毕）")

print("\n=== 程序结束 ===")

# ===== 为什么必须单独处理 KeyboardInterrupt =====
print("""
三个重要认识：

1. ValueError 说明"用户数据格式不对"，是预期内的，
   应该处理掉，让用户重试。

2. KeyboardInterrupt 说明"用户想中止程序"，
   不应该被当成错误处理掉，而应该尊重用户意图，
   让程序正常结束。裸 except 会把它一起吞掉，
   造成"按 Ctrl+C 没反应"的严重问题。

3. else 块的价值：把"业务逻辑"和"错误处理"分开，
   try 里只放可能出错的最小代码，else 里放成功后的逻辑，
   代码读起来非常清晰。
""")
