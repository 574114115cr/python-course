# test_review.py —— 这是一个可以直接运行的 pytest 测试文件

import json
import os
import tempfile

import pytest


# ===== 被测函数 =====
def add(a, b):
    """两数相加。"""
    return a + b


def divide(a, b):
    """两数相除，除零抛异常。"""
    return a / b


class Account:
    """账户类。"""
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("金额必须大于 0")
        self.balance += amount
        return self.balance


class SavingsAccount(Account):
    """储蓄账户，比普通账户多一个利率。"""
    def __init__(self, owner, balance=0, rate=0.03):
        super().__init__(owner, balance)
        self.rate = rate

    def add_interest(self):
        """计算利息。"""
        interest = self.balance * self.rate
        self.balance += interest
        return interest


# ===== 测试函数 =====
def test_add():
    """正常用例。"""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),
    (9, 3, 3.0),
    (-10, 2, -5.0),
])
def test_divide(a, b, expected):
    """参数化测试。"""
    assert divide(a, b) == expected


def test_divide_by_zero():
    """异常用例。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


# ===== 测试类 =====
class TestAccount:
    def test_default_balance(self):
        assert Account("小明").balance == 0

    def test_deposit(self):
        account = Account("小明", 100)
        account.deposit(50)
        assert account.balance == 150

    @pytest.mark.parametrize("amount", [0, -1, -100])
    def test_invalid_deposit(self, amount):
        """异常用例：非法金额。"""
        with pytest.raises(ValueError):
            Account("小明").deposit(amount)


class TestSavingsAccount:
    """测试继承。"""
    def test_inherits_account_attributes(self):
        account = SavingsAccount("小红", 1000)
        assert account.owner == "小红"
        assert account.balance == 1000

    def test_default_rate(self):
        assert SavingsAccount("小红").rate == 0.03

    def test_add_interest(self):
        account = SavingsAccount("小红", 1000, 0.05)
        interest = account.add_interest()
        assert interest == pytest.approx(50.0)
        assert account.balance == pytest.approx(1050.0)

    def test_is_account_instance(self):
        """子类对象也是父类实例。"""
        assert isinstance(SavingsAccount("小红"), Account)


# ===== 文件测试（用临时目录，不污染工作区）=====
def test_json_roundtrip():
    """测试 JSON 写入再读出，数据应该一致。"""
    # tempfile 提供临时目录，测试结束后自动清理
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.json")
        data = {"name": "小明", "scores": [90, 85]}

        # 写
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        # 读
        with open(filename, "r", encoding="utf-8") as f:
            loaded = json.load(f)

    assert loaded == data
    assert loaded["name"] == "小明"


def test_read_nonexistent_file_raises():
    """读取不存在的文件应该抛 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        with open("根本不存在.json", "r", encoding="utf-8") as f:
            f.read()
