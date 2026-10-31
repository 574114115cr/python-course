# lottery.py —— 分档抽奖，已中奖的人不再参与下一档
import random

students = [f"学员{i:02d}" for i in range(1, 31)]
random.seed(2026)

first = random.sample(students, 1)
rest = [s for s in students if s not in first]        # 排除已中奖

second = random.sample(rest, 3)
rest = [s for s in rest if s not in second]

third = random.sample(rest, 6)

print("一等奖", first)
print("二等奖", second)
print("三等奖", third)
