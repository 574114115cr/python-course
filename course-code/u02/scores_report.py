# scores_report.py —— 成绩分析（只用内置函数，不用循环）

scores = [88, 92, 79, 95, 60, 85, 91]

# 1）最高分与最低分
print("最高分：", max(scores))          # 95
print("最低分：", min(scores))          # 60

# 2）前三名：sorted 产生新列表，所以原scores 不受影响
top3 = sorted(scores, reverse=True)[:3]
print("前三名：", top3)                 # [95, 92, 91]
print("原列表没变：", scores)

# 3）平均分：sum 求和后除以元素个数
average = sum(scores) / len(scores)
print(f"平均分：{average:.2f}")# 84.29

# 4）低于 85 分的分数：用列表推导式过滤
low_scores = [s for s in scores if s < 85]
print("低于 85 分的：", low_scores)      # [79, 60]

# 顺带演示：如果不用推导式，手动构造也能做
low_manual = []
for s in scores:
    if s < 85:
        low_manual.append(s)
print("低分（手动版）：", low_manual)

# 5）最高分和最低分的差
print("极差：", max(scores) - min(scores))          # 35
