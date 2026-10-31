# test_fixture.py —— 用 setup_method 准备测试数据

import pytest


class ShoppingCart:
    """被测的购物车。"""
    def __init__(self):
        self.items = []

    def add(self, name, price):
        self.items.append({"name": name, "price": price})

    def remove(self, name):
        self.items = [item for item in self.items if item["name"] != name]

    def total(self):
        return sum(item["price"] for item in self.items)

    def count(self):
        return len(self.items)


class TestShoppingCart:
    """用 setup_method 为每个测试准备一个全新的购物车。"""

    def setup_method(self):
        """pytest 会在每个测试函数之前自动调用这个方法。"""
        self.cart = ShoppingCart()
        self.cart.add("苹果", 5.0)
        self.cart.add("香蕉", 3.0)

    def test_cart_is_empty_before_add(self):
        """测试：初始购物车是空的。"""
        empty = ShoppingCart()
        assert empty.count() == 0
        assert empty.total() == 0.0

    def test_setup_added_two_items(self):
        """测试：setup_method 确实准备好数据了。"""
        assert self.cart.count() == 2
        assert self.cart.total() == 8.0

    def test_add_item(self):
        self.cart.add("橙子", 4.0)
        assert self.cart.count() == 3
        assert self.cart.total() == 12.0

    def test_remove_item(self):
        self.cart.remove("苹果")
        assert self.cart.count() == 1
        assert self.cart.total() == 3.0

    def test_remove_nonexistent(self):
        """删除不存在的商品不应该报错，也不应该改变购物车。"""
        self.cart.remove("西瓜")
        assert self.cart.count() == 2
