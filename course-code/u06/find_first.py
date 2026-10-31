# find_first.py —— 用 break 找第一个符合条件的数

numbers = [12, 5, 33, 7, 91, 26]

# ===== 写法一：用标志位（能表达"没找到"的情况）=====
target_value = 30
found = False
found_index = -1

for index, number in enumerate(numbers):
    if number > target_value:
        found_index = index
        found = True
        break                # 找到第一个就停

if found:
    print(f"第一个大于 {target_value} 的数是 {numbers[found_index]}，"
          f"下标是 {found_index}")
else:
    print(f"没有找到大于 {target_value} 的数")

# ===== 写法二：用一个哨兵值（-1）表达"没找到" =====
def find_first(items, limit):
    """返回第一个大于 limit 的元素及其下标，都找不到时返回 (None, -1)。"""
    for index, item in enumerate(items):
        if item > limit:
            return item, index
    return None, -1


result, index = find_first(numbers, 30)
if result is None:
    print("没有找到")
else:
    print(f"找到 {result}，下标 {index}")

# ===== 测试边界情况：全部都小于阈值 =====
print(find_first([1, 2, 3], 100))    # (None, -1)
print(find_first([1, 50, 3], 30))    # (50, 1)
