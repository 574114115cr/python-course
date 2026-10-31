# score_loop.py —— 循环遍历、累加与统计

scores = [88, 92, 79, 95, 60]

# 1）逐个打印分数和序号（从 1 开始）
for index, score in enumerate(scores, start=1):
    print(f"第 {index} 个分数：{score}")

# 2）累加总分
total = 0
for score in scores:
    total += score
print("总分：", total)         # 414

# 3）最高分与最低分
print("最高分：", max(scores))        # 95
print("最低分：", min(scores))        # 60

# 4）平均分：先累加再除，用 f-string 保留两位小数
average = total / len(scores)
print(f"平均分：{average:.2f}")# 82.80

# 顺带演示：不改动原列表的情况下排序
print("降序排列：", sorted(scores, reverse=True))
