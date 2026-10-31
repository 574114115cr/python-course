# test_cart.py —— 测试模块

import pytest

from cart import ShoppingCart


class TestShoppingCart:
    """购物车测试。每个测试前会自动重置购物车。"""

    def setup_method(self):
        """pytest 在每个测试前自动调用，准备一份干净数据。"""
        self.cart = ShoppingCart()
        self.cart.add("苹果", 5.0)
        self.cart.add("香蕉", 3.0)

    # ===== 添加 =====
    def test_empty_cart(self):
        """新购物车是空的。"""
        empty = ShoppingCart()
        assert empty.count() == 0
        assert empty.total() == 0.0

    def test_setup_prepared_data(self):
        """确认 setup_method 准备了 2 件商品，总价 8。"""
        assert self.cart.count() == 2
        assert self.cart.total() == 8.0

    def test_add_item(self):
        """添加后件数和总价都增加。"""
        self.cart.add("橙子", 4.0)
        assert self.cart.count() == 3
        assert self.cart.total() == 12.0

    def test_add_zero_price_raises(self):
        """★ 价格为 0 应该报错。"""
        with pytest.raises(ValueError):
            self.cart.add("免费商品", 0)

    def test_add_negative_price_raises(self):
        """★ 负价格应该报错。"""
        with pytest.raises(ValueError):
            self.cart.add("奇怪商品", -5.0)

    # ===== 删除 =====
    def test_remove_item(self):
        """删除后件数和总价都减少。"""
        self.cart.remove("苹果")
        assert self.cart.count() == 1
        assert self.cart.total() == 3.0

    def test_remove_nonexistent(self):
        """★ 删除不存在的商品不报错，也不改变购物车。"""
        result = self.cart.remove("西瓜")
        assert result is False
        assert self.cart.count() == 2
        assert self.cart.total() == 8.0

    def test_remove_last_item_gives_zero_total(self):
        """★ 删掉最后一件商品后总价必须是 0。"""
        self.cart.remove("苹果")
        self.cart.remove("香蕉")
        assert self.cart.count() == 0
        assert self.cart.total() == 0.0

    # ===== 清空 =====
    def test_clear(self):
        """清空后一切归零。"""
        self.cart.clear()
        assert self.cart.count() == 0
        assert self.cart.total() == 0.0

    # ===== 参数化 =====
    @pytest.mark.parametrize("name,expected_total", [
        ("苹果", 3.0),      # 删苹果，剩香蕉
        ("香蕉", 5.0),      # 删香蕉，剩苹果
    ])
    def test_remove_each_item(self, name, expected_total):
        """分别删除不同商品，验证总价正确。"""
        self.cart.remove(name)
        assert self.cart.total() == expected_total
