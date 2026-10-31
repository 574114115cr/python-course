# （片段）pizza.py —— 函数放在这里，文件名就是模块名
def make_pizza(size, *toppings):
    """概述要制作的披萨。"""
    print(f"\n制作 {size} 寸披萨，配料：")
    for t in toppings:
        print(f"  - {t}")


if __name__ == "__main__":
    make_pizza(12, "蘑菇", "青椒")     # 只有直接运行 pizza.py 才执行
