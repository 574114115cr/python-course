# make_profile.py —— 必填 + 默认 + **extras 的组合

def make_profile(name, age=18, city="未知", **extras):
    """创建用户档案字典。

    必填：name
    选填：age（默认 18）、city（默认"未知"）
    其余任意关键字参数会进入 extras
    """
    profile = {
        "name": name,
        "age": age,
        "city": city,
    }
    # 把其余的关键字参数也加进去
    for key, value in extras.items():
        profile[key] = value
    return profile


# 测试各种调用方式
print(make_profile("小明"))
# {'name': '小明', 'age': 18, 'city': '未知'}

print(make_profile("小红", 25))
# {'name': '小红', 'age': 25, 'city': '未知'}

print(make_profile("小刚", 20, "杭州", email="x@x.com", hobby="篮球"))
# {'name': '小刚', 'age': 20, 'city': '杭州', 'email': 'x@x.com', 'hobby': '篮球'}

# 用关键字参数跳过中间的默认值
print(make_profile("小丽", city="北京"))
# {'name': '小丽', 'age': 18, 'city': '北京'}

# 注意：extras 只能接关键字参数，位置参数会报错
# print(make_profile("小强", 20, "上海", "额外的"))    # TypeError
