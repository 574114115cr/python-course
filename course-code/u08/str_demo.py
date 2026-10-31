# str_demo.py —— 让对象能被读懂地打印

class Book:
    def __init__(self, title, author, price, pages):
        self.title = title
        self.author = author
        self.price = price
        self.pages = pages

    def __str__(self):
        """定义对象转成字符串时的样子。"""
        return f"《{self.title}》/ {self.author}，{self.price} 元，{self.pages} 页"


book1 = Book("Python编程", "埃里克·马瑟斯", 89, 480)
book2 = Book("流畅的Python", "阿尔·拉玛", 139, 700)

# 没有 __str__ 时的默认输出：毫无意义的内存地址
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


p = Point(3, 5)
print("未定义 __str__ 的输出：")
print(p)      # <__main__.Point object at 0x000001...>  看不懂

# 有了 __str__ 之后
print("\n定义 __str__ 后的输出：")
print(book1)  # 《Python编程》/ 埃里克·马瑟斯，89 元，480 页
print(book2)  # 《流畅的Python》/ 阿尔·拉玛，139 元，700 页

# __str__ 会自动用在这些地方
print(f"这本书是 {book1}")     # f-string 内部会调用 __str__
print("列表里也是：", [book1])   # 列表打印时会调用元素的 __str__

# 顺带定义一个实用方法：每页多少钱
class BookWithMethod(Book):
    """在 Book 基础上加一个方法（这里用继承演示，单元后面会详讲）。"""

    def price_per_page(self):
        """计算每页价格，保留两位小数。"""
        return self.price / self.pages


book3 = BookWithMethod("流畅的Python", "阿尔·拉玛", 139, 700)
print(f"\n《{book3.title}》每页 {book3.price_per_page():.2f} 元")

# 属性和方法一起用
def show_book(book):
    """打印书籍信息。"""
    print(f"书名：{book.title}")        # 读属性，不写括号
    print(f"作者：{book.author}")
    if hasattr(book, "price_per_page"):    # 检查有没有这个方法
        print(f"每页价格：{book.price_per_page():.2f} 元")


print("\n--- 通用打印函数 ---")
show_book(book1)       # Book 类没有 price_per_page 方法
show_book(book3)       # BookWithMethod 有
