# ledger.py —— 换成你自己的路径也能直接跑
import json
import os
import tempfile


class Ledger:
    def __init__(self, path):
        self.path = path
        self.items = []
        self.load()

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                self.items = json.load(f)
        except FileNotFoundError:
            self.items = []          # 第一次运行：没有文件是正常的
        except json.JSONDecodeError:
            self.items = []          # 文件坏了：不崩，从空账本开始
            print("！账本文件损坏，已重置")

    def add(self, kind, amount, note=""):
        if kind not in ("收", "支"):
            raise ValueError("kind 只能是「收」或「支」")
        if amount <= 0:
            raise ValueError("金额必须大于 0")
        self.items.append({"kind": kind, "amount": amount, "note": note})

    def income(self):
        return sum(i["amount"] for i in self.items if i["kind"] == "收")

    def spend(self):
        return sum(i["amount"] for i in self.items if i["kind"] == "支")

    def balance(self):
        return self.income() - self.spend()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)


path = os.path.join(tempfile.mkdtemp(), "ledger.json")
book = Ledger(path)
print("空账本：", book.items, "余额", book.balance())

book.add("收", 8000, "工资")
book.add("支", 1200, "房租")
book.add("支", 35.5, "午饭")
print(f"收入 {book.income()} 支出 {book.spend()} 余额 {book.balance()}")

book.save()
print("写入文件：", os.path.basename(path), os.path.getsize(path), "字节")

again = Ledger(path)             # 重新读一次，验证真的落盘了
print("重新读入条数：", len(again.items), "余额", again.balance())

for kind, amount in (("借", 100), ("支", 0)):
    try:
        again.add(kind, amount)
    except ValueError as e:
        print("拒绝：", e)
