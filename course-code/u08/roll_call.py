# roll_call.py —— 随机点名：抽一个、抽三个、打乱顺序
import random

names = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]

random.seed(7)                          # 固定随机序列 → 结果可复现
print("抽一个  ", random.choice(names))
print("抽三个  ", random.sample(names, 3))     # 不放回，三人不重复

random.shuffle(names)                   # 原地打乱，不要接返回值
print("排队    ", names)
