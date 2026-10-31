# parameters.py —— 位置参数、关键字参数、默认参数

# 1）位置参数：按顺序对应
def describe_pet(animal_type, pet_name):
    """位置参数：调用时的顺序必须和定义时一致。"""
    return f"这是一只{animal_type}，名字叫{pet_name}"


print(describe_pet("狗", "旺财"))       # 狗 / 旺财
print(describe_pet("猫", "咪咪"))       # 猫 / 咪咪
# print(describe_pet("旺财", "狗"))    # 参数顺序错了，含义就全错了

# 2）关键字参数：按名字对应，顺序可以变
print(describe_pet(pet_name="旺财", animal_type="狗"))   # 顺序变了但结果正确

# 3）默认参数：可以不填，用默认值
def make_pizza(size=12, with_cheese=True):
    """默认参数：有默认值的参数必须写在最后。"""
    info = f"{size} 英寸披萨"
    if with_cheese:
        info += "，加芝士"
    else:
        info += "，不加芝士"
    return info


print(make_pizza())                          # 12 英寸披萨，加芝士
print(make_pizza(16))                         # 16 英寸披萨，加芝士
print(make_pizza(16, False))                  # 16 英寸披萨，不加芝士
print(make_pizza(with_cheese=False))          # 12 英寸披萨，不加芝士（跳过第一个）

# 4）可变参数 *args：收集所有的位置参数
def sum_all(*numbers):
    """接收任意多个位置参数。"""
    return sum(numbers)


print(sum_all(1, 2, 3))           # 6
print(sum_all(1, 2, 3, 4, 5))     # 15
print(sum_all())                  # 0

# 5）可变参数 **kwargs：收集所有的关键字参数
def build_profile(**info):
    """接收任意多个关键字参数，打包成字典。"""
    return info


print(build_profile(name="小明", age=18, city="杭州"))
print(build_profile())             # {}

# 6）四种参数混合使用（顺序有强制规定）
def full_demo(a, b=2, *args, **kwargs):
    """必填参数 -> 默认参数 -> *args -> **kwargs，顺序不能乱。"""
    print(f"a={a}")
    print(f"b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")


full_demo(1, 3, 5, 7, name="x", age=1)
# 错误示范：必填参数放在默认参数后面会报 SyntaxError
# def wrong(a=1, b):    # SyntaxError
#     pass
