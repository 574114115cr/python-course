# library.py —— 图书管理系统雏形

class Book:
    """一本书。"""
    def __init__(self, title, author, available=True):
        self.title = title
        self.author = author
        self.available = available

    def borrow(self):
        """借出图书，成功返回 True。"""
        if not self.available:
            return False
        self.available = False
        return True

    def return_book(self):
        """归还图书。"""
        self.available = True
        return True

    def status(self):
        """返回可借状态文字。"""
        return "在架" if self.available else "已借出"

    def __str__(self):
        return f"《{self.title}》/ {self.author}"


class Library:
    """图书馆。"""
    def __init__(self, name="市图书馆"):
        self.name = name
        self.books = []

    def add_book(self, book):
        """添加一本书。"""
        self.books.append(book)
        print(f"已入库：{book}")

    def find_book(self, title):
        """按书名查找，找到返回 Book 对象，找不到返回 None。"""
        for book in self.books:
            if book.title == title:
                return book
        return None

    def borrow_book(self, title):
        """按书名借书。"""
        book = self.find_book(title)
        if book is None:
            print(f"未找到《{title}》")
            return False
        if book.borrow():
            print(f"成功借出《{book.title}》")
            return True
        print(f"《{book.title}》已被借出，无法再次借出")
        return False

    def return_book(self, title):
        """按书名还书。"""
        book = self.find_book(title)
        if book is None:
            print(f"未找到《{title}》")
            return False
        book.return_book()
        print(f"已归还《{book.title}》")
        return True

    def list_available(self):
        """列出所有在架图书。"""
        available = [book for book in self.books if book.available]
        print(f"--- {self.name}在架图书（{len(available)} 本）---")
        for book in available:
            print(f"  {book} / {book.author}")
        if not available:
            print("  （暂无在架图书）")
        return available

    def statistics(self):
        """统计图书状态。"""
        total = len(self.books)
        on_shelf = sum(1 for book in self.books if book.available)
        return {
            "馆名": self.name,
            "总数": total,
            "在架": on_shelf,
            "借出": total - on_shelf,
        }


# ===== 测试 =====
library = Library("市第二图书馆")
print("=== 入库===")
library.add_book(Book("Python编程", "埃里克"))
library.add_book(Book("流畅的Python", "拉玛"))
library.add_book(Book("算法图解", "格罗宁"))
library.add_book(Book("深入理解计算机系统", "布莱恩特"))
library.add_book(Book("重构", "福勒"))

print("\n=== 借书 ===")
library.borrow_book("Python编程")
library.borrow_book("重构")
library.borrow_book("算法图解")

print("\n=== 重复借同一本 ===")
library.borrow_book("Python编程")

print("\n=== 借一本不存在的书 ===")
library.borrow_book("不存在的书")

print("\n=== 在架列表 ===")
library.list_available()

print("\n=== 还书 ===")
library.return_book("重构")
library.list_available()

print("\n=== 统计信息 ===")
stats = library.statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")
