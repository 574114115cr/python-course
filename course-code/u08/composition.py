# composition.py —— 组合：用类装类

class Engine:
    """发动机。"""
    def __init__(self, horsepower, fuel_type):
        self.horsepower = horsepower
        self.fuel_type = fuel_type

    def __str__(self):
        return f"{self.horsepower}马力 {self.fuel_type}发动机"


class Wheel:
    """轮胎。"""
    def __init__(self, size=17):
        self.size = size


class CarWithParts:
    """汽车：组合了发动机和轮胎。"""
    def __init__(self, make, model, engine, wheels=None):
        self.make = make
        self.model = model
        self.engine = engine            # 组合：一个对象装着另一个对象
        self.wheels = wheels or [Wheel() for _ in range(4)]

    def __str__(self):
        return f"{self.make} {self.model}，搭载{self.engine}，{len(self.wheels)} 个轮胎"

    def horsepower(self):
        """返回马力数。"""
        return self.engine.horsepower


# 使用
engine = Engine(150, "汽油")
car = CarWithParts("丰田", "卡罗拉", engine)
print(car)
print("马力：", car.horsepower())

# 修改组合的对象，汽车也跟着变（因为是同一个对象）
engine.horsepower = 200
print("改发动机后：", car.horsepower())     # 200

# 组合 vs 继承的经验法则：
# - "是一个"（is-a）关系 -> 用继承：狗 是一 种 动物
# - "有一个"（has-a）关系 -> 用组合：车 有 一个 发动机
# 拿不准时优先用组合，它更灵活、更不容易出继承耦合问题。

print("\n--- 一个更完整的实际例子 ---")


class BankAccount:
    """银行账户。"""
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("存款金额必须大于 0")
        self.balance += amount
        self.history.append(f"存款 {amount}")
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount
        self.history.append(f"取款 {amount}")
        return self.balance

    def __str__(self):
        return f"{self.owner} 的账户余额：{self.balance} 元"


account = BankAccount("小明", 1000)
print(account)
account.deposit(500)
account.withdraw(200)
print(account)
print("操作记录：", account.history)

# try/except 属于单元 9，但这里先感受一下错误处理
try:
    account.withdraw(99999)
except ValueError as error:
    print("操作失败：", error)
