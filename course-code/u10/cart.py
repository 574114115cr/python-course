# cart.py —— 被测模块

class ShoppingCart:
    """购物车。"""
    def __init__(self):
        self.items = []

    def add(self, name, price):
        """添加商品。price 必须大于 0。"""
        if price <= 0:
            raise ValueError("价格必须大于 0")
        self.items.append({"name": name, "price": price})
        return self

    def remove(self, name):
        """移除指定商品。商品不存在时不报错，返回是否真的移除了。"""
        original = len(self.items)
        self.items = [item for item in self.items if item["name"] != name]
        return len(self.items) < original

    def total(self):
        """返回总价。"""
        return sum(item["price"] for item in self.items)

    def count(self):
        """返回商品件数。"""
        return len(self.items)

    def clear(self):
        """清空购物车。"""
        self.items = []
        return self
