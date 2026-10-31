# input_validation.py —— 读入一个有效的正整数

print("请输入一个正整数：")

while True:
    raw = input("> ")

    # ===== 方式一：try/except（推荐，单元 9 会正式讲）=====
    try:
        number = int(raw)
    except ValueError:
        print(f"'{raw}' 不是有效的整数，请重新输入")
        continue             # 回到循环开头重新要一次

    # 整数校验通过，再检查范围
    if number <= 0:
        print("请输入大于 0 的整数")
        continue

    # 到这里说明输入完全合法，用 break 跳出无限循环
    print(f"你输入的数是 {number}")
    break

print("程序继续往下执行，说明已经拿到了有效输入")

# ===== 方式二：不用 try，用 str.isdigit() =====
# 注意 isdigit() 的局限：
#   "12".isdigit()    -> True
#   "-12".isdigit()   -> False  （负号不是数字字符）
#   "1.5".isdigit()   -> False  （小数点不是数字字符）
print("\n--- 用 isdigit 的版本 ---")
while True:
    raw = input("> ")
    if not raw.isdigit():
        print("请输入纯数字")
        continue
    number = int(raw)
    if number <= 0:
        print("请输入大于 0 的整数")
        continue
    print(f"你输入的数是 {number}")
    break
