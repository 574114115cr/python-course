# buggy_fixed.py —— 第二版：修复了 bug

def calculate_average(numbers):
    """求平均值。空列表返回 0。"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
