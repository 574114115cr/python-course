# vehicle.py —— 关卡验收 2：含继承的三层类设计（下面的 test_vehicle.py 依赖它）

class Vehicle:
    """交通工具基类。"""
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name}（{type(self).__name__}，{self.price} 元）"

    def describe(self):
        """基类的通用描述，子类可以重写。"""
        return f"这是一辆 {self.name}"


class Car(Vehicle):
    """汽车。"""
    def __init__(self, name, price, fuel_consumption):
        super().__init__(name, price)
        self.fuel_consumption = fuel_consumption    # 每百公里耗油量

    def fuel_cost(self, distance, price_per_liter=8):
        """计算行驶指定距离的油费。"""
        liters = distance / 100 * self.fuel_consumption
        return liters * price_per_liter


class ElectricCar(Car):
    """电动汽车 —— 继承 Car，但重写相关方法。"""
    def __init__(self, name, price, battery_capacity):
        super().__init__(name, price, fuel_consumption=0)
        self.battery_capacity = battery_capacity      # 电池容量 kWh
        self.charge = 100                             # 剩余电量百分比

    def fuel_cost(self, distance, price_per_liter=0):
        """★ 重写：电动车不用油，用电。"""
        electricity_per_100km = 15                   # 百公里耗电 15 度
        kwh = distance / 100 * electricity_per_100km
        return kwh * 0.6                             # 电价 0.6 元/度

    def describe(self):
        """★ 重写：用父类信息 + 自己的信息。"""
        return f"{super().describe()}，纯电动，电池 {self.battery_capacity} kWh"


# ===== 测试 =====
vehicles = [
    Car("燃油轿车", 120000, 7.5),
    ElectricCar("特斯拉 Model 3", 280000, 60),
    Car("越野车", 260000, 12.0),
]

print("--- 多态：同一段代码调用 describe() ---")
for v in vehicles:
    print(v.describe())

print("\n--- 费用对比（同一段代码，行为不同）---")
distance = 300
for v in vehicles:
    cost = v.fuel_cost(distance)
    print(f"{v.name}：行驶 {distance} 公里，成本 {cost:.2f} 元")

print("\n--- 验证继承关系 ---")
ec = ElectricCar("测试", 100000, 50)
print(f"是 Car 的实例吗：{isinstance(ec, Car)}")
print(f"是 Vehicle 的实例吗：{isinstance(ec, Vehicle)}")
print(f"继承自：{[c.__name__ for c in type(ec).__mro__]}")
print(f"重写的方法：ElectricCar.fuel_cost 是 Car.fuel_cost 吗？"
      f"{ElectricCar.fuel_cost is Car.fuel_cost}")
