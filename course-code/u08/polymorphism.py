# polymorphism.py —— 重写与多态

class Vehicle:
    """交通工具抽象基类。"""
    def __init__(self, name):
        self.name = name

    def move(self):
        """怎么移动 —— 由子类各自决定。"""
        raise NotImplementedError("子类必须重写这个方法")

    def fuel(self):
        """用什么能源。"""
        return "未定义"


class Car(Vehicle):
    def move(self):
        print(f"{self.name} 在公路上行驶")

    def fuel(self):
        return "汽油"


class ElectricCar(Vehicle):
    def move(self):
        print(f"{self.name} 在充电桩旁边安静地待着")

    def fuel(self):
        return "电能"


class Ship(Vehicle):
    def move(self):
        print(f"{self.name} 在水上航行")

    def fuel(self):
        return "柴油"


# ===== 多态：完全不需要判断类型 =====
vehicles = [
    Car("卡车"),
    ElectricCar("特斯拉"),
    Ship("泰坦尼克"),
]

print("--- 同一段代码，不同表现 ---")
for vehicle in vehicles:
    vehicle.move()                 # 每辆车各自"表现"不同

print("\n--- 统计各类型的数量（靠 isinstance 判断）---")
for vehicle in vehicles:
    print(f"{vehicle.name} 用的能源是 {vehicle.fuel()}")

print("\n--- 多态的核心价值：加新类型不用改老代码 ---")
vehicles.append(Ship("泰坦尼克号"))
print("现在有", len(vehicles), "个交通工具，上面的循环代码一个字都不用改")

print("\n--- 父类的 move 提醒：子类必须重写 ---")
v = Vehicle("抽象交通工具")
# v.move()      # NotImplementedError: 子类必须重写这个方法
print("父类的 fuel 默认返回：", v.fuel())   # 未定义
