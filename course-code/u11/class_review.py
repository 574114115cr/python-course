# class_review.py —— 类的全部要素复习

class Shape:
    """抽象基类。"""
    def __init__(self, name):
        self.name = name

    def area(self):
        """子类必须重写。"""
        raise NotImplementedError("子类必须重写 area()")

    def describe(self):
        """共有的方法，所有子类都能用。"""
        return f"{self.name}的面积是 {self.area():.2f}"


class Rectangle(Shape):
    """矩形。"""
    def __init__(self, width, height):
        super().__init__("矩形")
        self.width = width
        self.height = height

    def area(self):
        """重写父类方法。"""
        return self.width * self.height


class Circle(Shape):
    """圆形。"""
    PI = 3.14159

    def __init__(self, radius):
        super().__init__("圆形")
        self.radius = radius

    def area(self):
        return self.PI * self.radius ** 2


class Square(Rectangle):
    """正方形 —— 多层继承。"""
    def __init__(self, side):
        super().__init__(side, side)

    def describe(self):
        """重写父类的方法。"""
        return f"正方形，边长 {self.width}"


# 多态验证
shapes = [Rectangle(3, 4), Circle(2), Square(5)]

for shape in shapes:
    print(shape.describe())

print()

# 属性名与方法名不能重名（常见错误）
class BadDemo:
    """INTENTIONALLY-BROKEN 演示：属性名和方法名重名会互相覆盖"""
    def __init__(self):
        self.perimeter = 10      # 属性

    def perimeter(self):         # 同名方法覆盖了属性
        return 20

# 正确做法：给属性加前缀区分
class GoodDemo:
    def __init__(self, width, height):
        self._perimeter_value = 2 * (width + height)

    def perimeter(self):
        return self._perimeter_value


good = GoodDemo(3, 4)
print(f"正确写法：perimeter() = {good.perimeter()}")   # 14
