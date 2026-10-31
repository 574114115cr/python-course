# rectangle_class.py —— 矩形类

class Rectangle:
    """矩形。"""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        """返回面积。"""
        return self.width * self.height

    def perimeter(self):
        """返回周长。"""
        return 2 * (self.width + self.height)

    def is_square(self):
        """返回是否是正方形（宽等于高）。"""
        return self.width == self.height

    def __str__(self):
        return f"宽 {self.width}，高 {self.height}"


# ===== 测试：用元组列表存数据 =====
rectangles = [
    Rectangle(3, 4),
    Rectangle(5, 5),      # 正方形
    Rectangle(2, 8),
    Rectangle(6, 6),      # 正方形
    Rectangle(7, 3),
]

print(f"{'矩形':<20}{'面积':>10}{'周长':>10}{'是否正方形':>12}")
print("-" * 52)

square_count = 0
total_area = 0

for rect in rectangles:
    is_square = rect.is_square()
    if is_square:
        square_count += 1
    total_area += rect.area()
    print(
        f"{str(rect):<20}{rect.area():>10}{rect.perimeter():>12}"
        f"{'是' if is_square else '否':>12}"
    )

print("-" * 52)
print(f"总共{len(rectangles)} 个矩形，正方形有 {square_count} 个")
print(f"面积总和：{total_area}")

# 单个矩形的详细信息
print("\n--- 单个矩形 ---")
r = Rectangle(10, 4)
print(f"{r} 面积 {r.area()}，周长 {r.perimeter()}")
print("是正方形吗：", r.is_square())
