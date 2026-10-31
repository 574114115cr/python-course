# inventory.py —— 遍历、判断、统计
inventory = {"苹果": 12, "香蕉": 0, "橙子": 5, "榴莲": 0}

for name, qty in inventory.items():
    if qty > 0:
        print(f"{name} 有货（{qty}）")
    else:
        print(f"{name} 缺货")

out = [name for name, qty in inventory.items() if qty == 0]
print("缺货", out)

total = sum(inventory.values())
in_stock = len([q for q in inventory.values() if q > 0])
print(f"总数 {total}，有货品类 {in_stock}")
