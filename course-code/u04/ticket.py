# ticket.py —— 四段票价
ages = [3, 6, 17, 18, 59, 60]

for age in ages:
    if age < 6:
        price, note = 0, "免票"
    elif age < 18:
        price, note = 40, "半价"
    elif age < 60:
        price, note = 80, "全价"
    else:
        price, note = 0, "免票"
    print(f"{age} 岁 → {price} 元（{note}）")
