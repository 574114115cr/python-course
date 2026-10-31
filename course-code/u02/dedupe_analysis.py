# dedupe_analysis.py —— 不用 set，用列表方法做计数与查位置

nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

# 1）长度
print("列表长度：", len(nums))            # 10

# 2）统计 1 出现几次
print("1 出现了：", nums.count(1), "次")   # 2 次

# 3）找出 3 所在的所有位置
#思路：index() 只返回第一个位置，所以找到后把它替换成
#      一个绝不会出现在列表里的标记（这里是 0），然后继续往后找。
positions = []
temp = nums[:]# 用副本，不破坏原始数据

i = 0
while i < len(temp):                     # while 循环属于单元 6，先照抄即可
    if temp[i] == 3:
        positions.append(i)
        temp[i] = 0                     # 打标记，避免重复找到
    i += 1

print("3 出现的位置：", positions)        # [0, 9]
print("原数据没被破坏：", nums)

# 4）升序与降序（sorted 不修改原列表）
print("升序：", sorted(nums))             # [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]
print("降序：", sorted(nums, reverse=True))

# 5）反转，且不破坏原列表
print("反转副本：", nums[::-1])
print("原列表：", nums)               # [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

# 如果允许原地修改，才用 reverse()
flipped = nums[:]
flipped.reverse()
print("原地反转：", flipped)
