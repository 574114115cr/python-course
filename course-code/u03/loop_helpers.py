# loop_helpers.py —— for 循环的三个高性价比搭档

letters = ["a", "b", "c"]

# 1）enumerate()：同时拿到下标和元素
for index, letter in enumerate(letters):
    print(f"第 {index} 位是 {letter}")

# start 参数可以指定下标起点
for index, letter in enumerate(letters, start=1):
    print(f"第 {index} 个是 {letter}")

# 2）zip()：同时遍历多个列表（长度不等时以最短的为准）
names = ["小明", "小红", "小刚"]
scores = [88, 95, 72, 100]#故意多一个
for name, score in zip(names, scores):
    print(f"{name} 得了 {score} 分")
# 小明 88 / 小红 95 / 小刚 72 —— 第 4 个分数因为没有对应名字被忽略

# 3）在循环里做条件筛选
for letter in letters:
    if letter in ["a", "c"]:
        print("找到元音：", letter)

# 累加器模式：循环最常见的用途
total = 0
for score in [88, 95, 72]:
    total += score# 等价于 total = total + score
print("总分：", total)         # 255
