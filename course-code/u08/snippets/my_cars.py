# （片段）my_cars.py
import car
from car import ElectricCar

print(car.Car("大众", "高尔夫", 2020).describe())          # ① 模块名.类名
print(ElectricCar("蔚来", "ET5", 2023).describe())         # ② 直接用类名
