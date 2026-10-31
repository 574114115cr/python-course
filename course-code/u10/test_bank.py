# test_bank.py —— 测试类：把相关测试归类

import pytest


class BankAccount:
    """被测的银行账户类。"""
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        """存款。"""
        if amount <= 0:
            raise ValueError("存款金额必须大于 0")
        self.balance += amount
        self.history.append(f"存款 {amount}")
        return self.balance

    def withdraw(self, amount):
        """取款。"""
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount
        self.history.append(f"取款 {amount}")
        return self.balance


class TestBankAccountDeposit:
    """测试类：只用来分组，不能有 __init__。"""

    def test_deposit_increases_balance(self):
        """存款后余额增加。"""
        account = BankAccount("小明", 100)
        account.deposit(50)
        assert account.balance == 150

    def test_deposit_returns_new_balance(self):
        """存款方法返回新的余额。"""
        account = BankAccount("小明", 100)
        result = account.deposit(50)
        assert result == 150

    def test_deposit_zero_raises(self):
        """存 0 元应该报错。"""
        account = BankAccount("小明", 100)
        with pytest.raises(ValueError):
            account.deposit(0)

    def test_deposit_negative_raises(self):
        """存负数应该报错。"""
        account = BankAccount("小明", 100)
        with pytest.raises(ValueError):
            account.deposit(-50)

    def test_history_records_transaction(self):
        """交易记录应该被保存。"""
        account = BankAccount("小明", 100)
        account.deposit(50)
        assert len(account.history) == 1
        assert "存款 50" in account.history[0]


class TestBankAccountWithdraw:
    """另一组测试，同样针对 BankAccount。"""

    def test_withdraw_reduces_balance(self):
        account = BankAccount("小明", 100)
        account.withdraw(30)
        assert account.balance == 70

    def test_withdraw_all_succeeds(self):
        """取光全部余额应该允许。"""
        account = BankAccount("小明", 100)
        account.withdraw(100)
        assert account.balance == 0

    def test_withdraw_too_much_raises(self):
        """取超额应该报错。"""
        account = BankAccount("小明", 100)
        with pytest.raises(ValueError):
            account.withdraw(150)
