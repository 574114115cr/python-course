# divider.py —— 被测模块

def divide(a, b):
    """返回 a 除以 b 的结果。

    除数为 0 时会抛出 ZeroDivisionError。
    """
    return a / b


def divide_safe(a, b, default=0.0):
    """安全除法：除数为 0 时返回默认值。"""
    try:
        return a / b
    except ZeroDivisionError:
        return default
