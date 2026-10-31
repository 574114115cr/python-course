# scores.py —— 列表套字典的统计
students = [
    {"name": "张三", "scores": [88, 92, 76]},
    {"name": "李四", "scores": [59, 64, 70]},
    {"name": "王五", "scores": [100, 95, 98]},
]

avgs = {}
for s in students:
    avg = sum(s["scores"]) / len(s["scores"])
    avgs[s["name"]] = avg
    tag = "及格" if avg >= 60 else "不及格"
    print(f"{s['name']} {avg:.1f} 分 · {tag}")

class_avg = sum(avgs.values()) / len(avgs)
print(f"班级平均 {class_avg:.1f} 分")

print("最高分", max(avgs, key=avgs.get))
