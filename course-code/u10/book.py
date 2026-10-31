# book.py —— 被测模块

class Book:
    """一本书。"""
    def __init__(self, title, price, available=True):
        self.title = title
        self.price = price
        self.available = available

    def borrow(self):
        """借出图书。已被借出时抛出 ValueError。"""
        if not self.available:
            raise ValueError(f"《{self.title}》已被借出，无法再次借出")
        self.available = False
        return self

    def return_book(self):
        """归还图书。"""
        self.available = True
        return self

    def apply_discount(self, rate):
        """打折，rate 是 0-1 之间的折扣率。"""
        if not 0 <= rate <= 1:
            raise ValueError("折扣率必须在 0 到 1 之间")
        self.price = self.price * rate
        return self.price
