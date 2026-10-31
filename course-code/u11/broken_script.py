# broken_script.py —— INTENTIONALLY-BROKEN 这段有 3 个错误，请修复

def calculate_statistics(numbers)
    """计算一组数字的统计信息。"""
    total = 0
    for number in numbers:
        total += number

    count = len(numbers)
    average = total / count
    maximum = max(numbers)
    minimum = min(numbers)

    return {
        "总和": total,
        "个数": count,
        "平均": average,
    }

def print_report(stats)
    """打印统计信息。"""
    print("===== 统计报告 =====")
    for key in stats:
        print(f"{key}: {stats[key]}")

numbers = [10, 25, 3, 47, 8, 91]
result = calculate_statistics(numbers)
print_report(result)
