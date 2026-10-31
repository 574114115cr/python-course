# range_demo.py —— range() 生成数字序列

print("range(5)：", list(range(5)))                # [0, 1, 2, 3, 4]
print("range(1, 6)：", list(range(1, 6)))          # [1, 2, 3, 4, 5]
print("range(2, 11, 2)：", list(range(2, 11, 2)))  # [2, 4, 6, 8, 10]
print("range(10, 0, -1)：", list(range(10, 0, -1)))# [10, ..., 1, 0]

# 关键：含起点不含终点
for i in range(1, 6):
    if i < 6:
        print(i, end=" ")
print()

# range(5) 等价于 range(0, 5)
print("两种写法相同：", list(range(5)) == list(range(0, 5)))

# len() 可以直接算 range 的长度，不必真的生成列表
print("range(1, 100) 有几个数：", len(range(1, 100)))      # 99

# 用 range 遍历列表下标
letters = ["a", "b", "c"]
for index in range(len(letters)):
    print(f"索引 {index} 的元素是 {letters[index]}")

# 更推荐的写法：enumerate
for index, letter in enumerate(letters):
    print(f"索引 {index} 的元素是 {letter}")
