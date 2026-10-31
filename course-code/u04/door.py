# door.py —— 忽略大小写与空格的门禁判断
members = ["alice", "bob", "carol"]
visitors = ["Alice", "dave", "BOB", "", "carol"]

for raw in visitors:
    name = raw.strip()                  # 先去首尾空格
    if not name:                        # 空串 → 无效，提前结束本轮
        print("无效输入")
        continue
    if name.lower() in members:         # 统一小写再比
        print(f"准入: {name}")
    else:
        print(f"拒绝: {name}")
