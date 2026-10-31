# shapes.py —— 多态实战：统一管理不同形状

class Shape:
    """形状基类：定义所有形状共有的东西。"""

    def __init__(self, name):
        self.name = name

    def area(self):
        """计算面积 —— 由子类各自重写。"""
        print(f"警告：{self.name} 没有实现 area()，父类返回 None")
        return None

    def perimeter(self):
        """计算周长 —— 由子类各自重写。"""
        print(f"警告：{self.name} 没有实现 perimeter()，父类返回 None")
        return None

    def __str__(self):
        return f"{self.name}（{type(self).__name__}）"


class Rectangle(Shape):
    """矩形。"""
    def __init__(self, width, height):
        # 先调用父类的 __init__ 设置共有的 name 属性
        super().__init__("矩形")
        # 再设置自己的属性
        self.width = width
        self.height = height

    def area(self):
        """重写：矩形的面积。"""
        return self.width * self.height

    def perimeter(self):
        """重写：矩形的周长。"""
        return 2 * (self.width + self.height)


class Circle(Shape):
    """圆形。"""
    PI = 3.14159      # 类属性：圆周率

    def __init__(self, radius):
        super().__init__("圆形")
        self.radius = radius

    def area(self):
        """重写：圆的面积。"""
        return self.PI * self.radius ** 2

    def perimeter(self):
        """重写：圆的周长。"""
        return 2 * self.PI * self.radius


class Triangle(Shape):
    """三角形。"""
    def __init__(self, base, height):
        super().__init__("三角形")
        self.base = base
        self.height = height

    def area(self):
        return self.base * self.height / 2

    def perimeter(self):
        # 假设是等腰三角形，两腰长为 sqrt((base/2)^2 + height^2)
        side = ((self.base / 2) ** 2 + self.height ** 2) ** 0.5
        return self.base + 2 * side


class Square(Rectangle):
    """正方形 —— 继承矩形，只需要一个边长。"""
    def __init__(self, side):
        # 直接调用父类（矩形）的 __init__
        super().__init__(side, side)


# ===== 测试：多态的关键演示 =====
shapes = [
    Rectangle(3, 4),
    Circle(2),
    Triangle(6, 4),
    Square(5),
]

print(f"{'形状':<20}{'面积':>12}{'周长':>12}")
print("-" * 44)

total_area = 0
for shape in shapes:
    area = shape.area()          # 每种形状自己算自己的
    perimeter = shape.perimeter()
    total_area += area
    print(f"{str(shape):<20}{area:>12.2f}{perimeter:>12.2f}")

print("-" * 44)
print(f"{'总面积':<20}{total_area:>12.2f}")

# ===== 证明多态的价值 =====
print("\n--- 加一种新形状，上面的循环代码一个字都不用改 ---")


class Trapezoid(Shape):
    """梯形 —— 这是运行后新加的类型。"""
    def __init__(self, top, bottom, height):
        super().__init__("梯形")
        self.top = top
        self.bottom = bottom
        self.height = height

    def area(self):
        return (self.top + self.bottom) * self.height / 2


shapes.append(Trapezoid(3, 5, 4))
print(f"加入梯形后，总数：{len(shapes)}")
for shape in shapes[-1:]:
    print(f"{shape} 面积 {shape.area():.2f}")

# ===== 调用未重写的方法会怎样 =====
print("\n--- 父类未重写方法的行为 ---")
generic = Shape("神秘形状")
print(f"area() 返回：{generic.area()}")
print("这就是多态：同一段调用，不同的对象有不同的表现")
