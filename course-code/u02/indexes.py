# indexes.py —— 正索引与负索引热身

numbers = [10, 20, 30, 40, 50]

print(numbers[0])                   # 10  第一个
print(numbers[-1])                  # 50  最后一个
print(numbers[2])                   # 30  中间那个（索引 2 = 第 3 个）
print(numbers[-2])                  # 40  倒数第二个
print(numbers[len(numbers) - 3])    # 20  用 len() 表达式表示"正数第二个"
