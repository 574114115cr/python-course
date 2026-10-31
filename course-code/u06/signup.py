# signup.py —— while + input 收集，再按姓名排序输出
signups = {}

while True:
    name = input("姓名（输入 q 结束）：").strip()
    if name == "q":
        break
    if not name:                       # 防手滑直接回车
        continue
    if name in signups:
        print(f"{name} 已报名，将覆盖原选择")
    signups[name] = input("想学的课程：").strip()

print(f"共 {len(signups)} 人报名")
for name in sorted(signups):           # 按姓名字母序，不排序则按插入顺序
    print(f"{name} → {signups[name]}")
