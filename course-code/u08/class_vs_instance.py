# class_vs_instance.py —— 两种属性的区别

class Car:
    """汽车类。"""

    # 类属性：所有实例共享
    wheels = 4
    made_in = "中国"

    def __init__(self, make, model, color):
        # 实例属性：每个实例独有
        self.make = make
        self.model = model
        self.color = color
        self.odometer = 0

    def drive(self, miles):
        """行驶指定里程。"""
        self.odometer += miles
        return self.odometer

    def show(self):
        return f"{self.color} {self.make} {self.model}，已行驶 {self.odometer} 公里"


car1 = Car("丰田", "卡罗拉", "红色")
car2 = Car("本田", "雅阁", "蓝色")

print(car1.show())
print(car2.show())

# 修改实例属性：只影响这一个对象
car1.color = "黑色"
print("\n改后 car1：", car1.color)      # 黑色
print("car2 不受影响：", car2.color)      # 蓝色

# 修改类属性：影响所有对象
print("\n所有车的轮子数：", car1.wheels, car2.wheels)
Car.wheels = 6
print("改类属性后：", car1.wheels, car2.wheels)   # 6 6 都变了

# 警告：不要通过实例去改类属性（这会意外创建一个实例属性，掩盖真值）
car1.wheels = 8
print("\n通过 car1 改轮子数后：")
print("  car1.wheels =", car1.wheels)      # 8
print("  car2.wheels =", car2.wheels)      # 6  没变
print("  Car.wheels =", Car.wheels)        # 6  类属性也没变
# 结论：要用 Car.wheels = X 改类属性，不要用 car1.wheels = X

# 判断属性归属的方法
print("\n--- 属性归属判断 ---")
print("wheels 在 car1 自己的字典里吗：", "wheels" in car1.__dict__)   # False
print("color 在 car1 自己的字典里吗：", "color" in car1.__dict__)     # True
print("wheels 是类属性：", "wheels" in Car.__dict__)                # True
