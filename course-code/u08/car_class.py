# car_class.py —— 类属性与实例属性的实践

class Car:
    """汽车类。"""

    # ===== 类属性：所有实例共享 =====
    wheels = 4
    made_in = "中国"

    def __init__(self, make, model, color="白色"):
        # ===== 实例属性：每个对象独有 =====
        self.make = make
        self.model = model
        self.color = color
        self.odometer = 0

    def drive(self, miles):
        """行驶指定里程，累加总里程。"""
        self.odometer += miles
        return self.odometer

    def is_new(self):
        """判断是否还是新车（里程小于 100 公里）。"""
        return self.odometer < 100

    def show_info(self):
        """输出完整信息。"""
        status = "新车" if self.is_new() else "二手车"
        return (
            f"{self.color} {self.make} {self.model} | "
            f"里程 {self.odometer} 公里 | {status} | "
            f"{self.wheels} 轮 | {self.made_in}制造"
        )

    def __str__(self):
        return f"{self.make} {self.model}"


# ===== 测试 =====
car1 = Car("丰田", "卡罗拉", "红色")
car2 = Car("本田", "雅阁")           # color 用默认值"白色"

print("--- 初始状态 ---")
print("car1:", car1.show_info())
print("car2:", car2.show_info())

# 修改实例属性：只影响这一个对象
car1.color = "黑色"
print("\n--- 改 car1 的颜色 ---")
print("car1:", car1.color)      # 黑色
print("car2:", car2.color)      # 白色  没变！

# 行驶后里程变化
print("\n--- 行驶之后 ---")
car1.drive(150)
car2.drive(30)
print("car1:", car1.show_info())   # 二手车
print("car2:", car2.show_info())   # 还是新车

# 修改类属性：影响所有对象
print("\n--- 修改类属性 wheels = 6 ---")
Car.wheels = 6
print("car1:", car1.wheels)       # 6
print("car2:", car2.wheels)       # 6都变了

# 陷阱：不要通过实例改类属性
print("\n--- 陷阱演示 ---")
car1.wheels = 8                  # 这样做创建的是 car1 的实例属性
print("car1.wheels =", car1.wheels)    # 8
print("car2.wheels =", car2.wheels)    # 6  没跟着变
print("Car.wheels =", Car.wheels)      # 6  类属性也没变
print("结论：改类属性必须写 Car.wheels = X，写 car1.wheels = X 是错的")

# 恢复
Car.wheels = 4
