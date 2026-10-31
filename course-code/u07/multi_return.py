# multi_return.py —— 多返回值与解包

def analyze_numbers(numbers):
    """返回 (总和, 平均值, 最大值, 最小值, 偶数个数) 组成的元组。"""
    total = sum(numbers)
    average = total / len(numbers)
    largest = max(numbers)
    smallest = min(numbers)
    even_count = 0
    for n in numbers:
        if n % 2 == 0:
            even_count += 1
    # 逗号分隔多个值，Python 会自动打包成元组返回
    return total, average, largest, smallest, even_count


def count_vowels(text):
    """返回 (元音数量, 元音列表) 组成的元组。"""
    vowels = "aeiouAEIOU"
    found = []
    for char in text:
        if char in vowels:
            found.append(char)
    return len(found), found


# ===== 解包接收全部结果 =====
data = [3, 8, 12, 5, 20, 7]

total, average, largest, smallest, even_count = analyze_numbers(data)
print(f"总和：{total}")
print(f"平均值：{average:.2f}")
print(f"最大值：{largest}")
print(f"最小值：{smallest}")
print(f"偶数个数：{even_count}")

# 元组也可以整体接收，然后按下标访问
result = analyze_numbers(data)
print(f"\n下标访问：总和 {result[0]}，最大 {result[2]}")

# 星号解包：只要中间几个，中间用 * 忽略
total, _, largest, *_ = analyze_numbers(data)
print(f"只要总和和最大值：{total}，{largest}")

# 元音统计
vowel_count, vowel_list = count_vowels("Hello World, Python is Fun!")
print(f"\n元音数量：{vowel_count}")
print(f"元音列表：{vowel_list}")

# 顺带演示一个实用技巧：打印表格
print("\n--- 数据报告 ---")
print(f"{'总和':<10}{total}")
print(f"{'平均值':<10}{average:.2f}")
print(f"{'最大值':<10}{largest}")
print(f"{'最小值':<10}{smallest}")
print(f"{'偶数个数':<10}{even_count}")
