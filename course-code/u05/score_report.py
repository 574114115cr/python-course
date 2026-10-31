# score_report.py —— 成绩单分析

scores = {"语文": 90, "数学": 85, "英语": 78, "物理": 55, "化学": 92}

# 1）最高分的科目和分数
#max() 的 key 参数告诉它"按什么标准比大小"
best_subject = max(scores, key=scores.get)
print(f"最高分：{best_subject}，{scores[best_subject]} 分")    # 化学，92 分

# 最直接的对比：也可以排序
sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
print("第一名到第三名：")
for subject, score in sorted_items[:3]:
    print(f"  {subject}: {score} 分")

# 2）不及格的科目（<60 分）
failed = [subject for subject, score in scores.items() if score < 60]
print("不及格：", failed)      # ['物理']

# 3）所有科目名
print("所有科目：", list(scores.keys()))
print("科目数量：", len(scores))

# 4）平均分
total = sum(scores.values())
average = total / len(scores)
print(f"总分：{total}，平均分：{average:.2f}")

# 顺带：最高分和最低分的差
print("极差：", max(scores.values()) - min(scores.values()))
