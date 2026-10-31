# check_ledger.py —— 断言就是最小的测试：跑通没报错，就说明这几条不变式成立
import json
import os
import tempfile


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def add(items, kind, amount):
    if kind not in ("收", "支"):
        raise ValueError("kind")
    if amount <= 0:
        raise ValueError("amount")
    items.append({"kind": kind, "amount": amount})


work = tempfile.mkdtemp()
fresh = os.path.join(work, "a.json")
broken = os.path.join(work, "b.json")
open(broken, "w", encoding="utf-8").write("{不是 JSON")

assert load(fresh) == []                  # 文件不存在 → 空账本，不抛异常
assert load(broken) == []                 # 内容坏了 → 也是空账本
assert load(fresh) is not load(fresh)     # 每次都是新列表，不会共享

items = []
add(items, "收", 100)
add(items, "支", 30)
assert sum(i["amount"] for i in items if i["kind"] == "收") == 100
assert sum(i["amount"] for i in items if i["kind"] == "支") == 30

for kind, amount in (("借", 10), ("支", 0), ("支", -5)):
    try:
        add(items, kind, amount)
        raise AssertionError(f"应该拒绝 {kind} {amount}")
    except ValueError:
        pass

print(f"6 条断言全部通过，账本仍有 {len(items)} 条记录")
