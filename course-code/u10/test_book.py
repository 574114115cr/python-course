# test_book.py —— 测试模块

import pytest

from book import Book


class TestBookInitialization:
    """测试 Book 的创建与默认值。"""

    def test_default_available_is_true(self):
        """新建的书默认可借。"""
        book = Book("Python编程", 89)
        assert book.available is True

    def test_stores_title_and_price(self):
        """标题和价格正确保存。"""
        book = Book("Python编程", 89)
        assert book.title == "Python编程"
        assert book.price == 89

    def test_can_set_unavailable_on_creation(self):
        """创建时可以直接指定为不可借。"""
        book = Book("旧书", 20, available=False)
        assert book.available is False


class TestBookBorrow:
    """测试借阅功能。"""

    def test_borrow_sets_unavailable(self):
        """借出后标记为不可借。"""
        book = Book("Python编程", 89)
        book.borrow()
        assert book.available is False

    def test_borrow_returns_self(self):
        """borrow() 返回自身，支持链式调用。"""
        book = Book("Python编程", 89)
        result = book.borrow()
        assert result is book

    def test_borrow_twice_raises(self):
        """★ 已被借出的书再次借出应该报错。"""
        book = Book("Python编程", 89)
        book.borrow()
        with pytest.raises(ValueError):
            book.borrow()

    def test_borrow_unavailable_raises(self):
        """创建时就是不可借状态，借出应报错。"""
        book = Book("旧书", 20, available=False)
        with pytest.raises(ValueError):
            book.borrow()


class TestBookReturn:
    """测试归还功能。"""

    def test_return_sets_available(self):
        """归还后标记为可借。"""
        book = Book("Python编程", 89)
        book.borrow()
        book.return_book()
        assert book.available is True

    def test_can_borrow_after_return(self):
        """归还后可以再次借出。"""
        book = Book("Python编程", 89)
        book.borrow()
        book.return_book()
        book.borrow()                    # 这次不应报错
        assert book.available is False


class TestBookDiscount:
    """测试打折功能。"""

    def test_apply_discount(self):
        book = Book("Python编程", 100)
        book.apply_discount(0.8)
        assert book.price == pytest.approx(80.0)

    @pytest.mark.parametrize("rate", [1.5, -0.1, 2])
    def test_invalid_discount_raises(self, rate):
        """★ 非法折扣率应该报错。"""
        book = Book("Python编程", 100)
        with pytest.raises(ValueError):
            book.apply_discount(rate)
