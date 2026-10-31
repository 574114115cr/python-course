# conftest.py —— pytest 会自动发现这个文件里的 fixture
import pytest
from cart import ShoppingCart


@pytest.fixture
def empty_cart():
    return ShoppingCart()
