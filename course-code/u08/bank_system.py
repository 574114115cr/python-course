# bank_system.py —— 银行账户系统（组合 + 类设计）

class Owner:
    """账户持有人。"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __str__(self):
        return f"{self.name} <{self.email}>"


class BankAccount:
    """一个银行账户。"""
    def __init__(self, account_number, owner, balance=0.0):
        self.account_number = account_number
        self.owner = owner          # 组合：持有一个 Owner 对象
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        """存款，金额必须大于 0。"""
        if amount <= 0:
            raise ValueError("存款金额必须大于 0")
        self.balance += amount
        self.history.append(f"存款 {amount:.2f} 元")
        return self.balance

    def withdraw(self, amount):
        """取款，余额必须充足。"""
        if amount <= 0:
            raise ValueError("取款金额必须大于 0")
        if amount > self.balance:
            raise ValueError(f"余额不足，当前余额 {self.balance:.2f} 元")
        self.balance -= amount
        self.history.append(f"取款 {amount:.2f} 元")
        return self.balance

    def transfer_to(self, other, amount):
        """转账到另一个账户。"""
        if other is self:
            raise ValueError("不能转账到自己")
        self.withdraw(amount)      # 余额不足时会自动报错
        other.deposit(amount)
        self.history.append(f"转账 {amount:.2f} 元给 {other.account_number}")
        other.history.append(f"收到来自 {self.account_number} 的 {amount:.2f} 元")
        return True

    def statement(self):
        """输出对账单。"""
        lines = [
            "=" * 46,
            f"账户号码：{self.account_number}",
            f"户主：  {self.owner}",
            f"余额：    {self.balance:.2f} 元",
            "-" * 46,
            "交易记录：",
        ]
        if not self.history:
            lines.append("  （暂无交易）")
        for i, record in enumerate(self.history, 1):
            lines.append(f"  {i}. {record}")
        lines.append("=" * 46)
        return "\n".join(lines)

    def __str__(self):
        return f"账户 {self.account_number}（{self.owner.name}）余额 {self.balance:.2f} 元"


class Bank:
    """银行 —— 组合多个账户。"""
    def __init__(self, name):
        self.name = name
        self.accounts = []
        self._next_number = 1001      # 自动递增的账户号码

    def open_account(self, owner, initial=0.0):
        """开户，返回新建的账户对象。"""
        account = BankAccount(self._next_number, owner, initial)
        self._next_number += 1       # 下一个账户号码
        self.accounts.append(account)
        if initial > 0:
            account.history.append(f"开户存入 {initial:.2f} 元")
        print(f"{self.name} 已为 {owner.name} 开户，账号 {account.account_number}")
        return account

    def find_account(self, owner_name):
        """按户主名字找账户，找到返回对象，找不到返回 None。"""
        for account in self.accounts:
            if account.owner.name == owner_name:
                return account
        return None

    def total_deposit(self):
        """所有账户余额之和。"""
        return sum(account.balance for account in self.accounts)

    def total_customers(self):
        """客户数量。"""
        return len(self.accounts)

    def richest_account(self):
        """余额最多的账户，没有账户时返回 None。"""
        if not self.accounts:
            return None
        richest = self.accounts[0]
        for account in self.accounts[1:]:
            if account.balance > richest.balance:
                richest = account
        return richest

    def print_all(self):
        """列出所有账户。"""
        print(f"--- {self.name} 全部账户（{len(self.accounts)} 个）---")
        for account in self.accounts:
            print(f"  {account}")


# ===== 测试 =====
print("=== 开户 ===")
bank = Bank("测试银行")
acc1 = bank.open_account(Owner("小明", "xiaoming@test.com"), 1000)
acc2 = bank.open_account(Owner("小红", "xiaohong@test.com"), 2000)
acc3 = bank.open_account(Owner("小刚", "xiaogang@test.com"))

print("\n=== 存取款 ===")
acc1.deposit(500)
acc2.withdraw(300)
print(acc1)
print(acc2)

print("\n=== 转账 ===")
acc1.transfer_to(acc3, 200)
print(acc1)
print(acc3)

print("\n=== 对账单 ===")
print(acc1.statement())

print("\n=== 查找账户 ===")
found = bank.find_account("小红")
print("按名字找小红：", found)
missing = bank.find_account("查无此人")
print("找一个不存在的人：", missing)      # None

print("\n=== 银行汇总 ===")
bank.print_all()
print(f"客户数量：{bank.total_customers()}")
print(f"存款总额：{bank.total_deposit():.2f} 元")
richest = bank.richest_account()
if richest:
    print(f"最高余额账户：{richest.owner.name}，{richest.balance:.2f} 元")

print("\n=== 错误处理 ===")
try:
    acc3.withdraw(99999)
except ValueError as error:
    print("操作失败：", error)

try:
    acc1.deposit(-100)
except ValueError as error:
    print("操作失败：", error)
