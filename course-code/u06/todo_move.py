# todo_move.py —— 从待办搬到已完成，空字符串直接丢掉
pending = ["写周报", "", "回邮件", "订机票", ""]
done = []

while pending:                     # 列表非空就继续
    task = pending.pop(0)          # 从头取，保持原始顺序
    if not task:                   # 空字符串为假 → 这一项不算任务
        continue
    done.append(task)
    print(f"完成：{task}（还剩 {len(pending)} 项）")

print("已完成", done)
print("待办  ", pending)
