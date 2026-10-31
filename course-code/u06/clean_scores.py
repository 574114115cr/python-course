# clean_scores.py —— 两种「删干净」的写法
scores = [88, 0, 92, 0, 75, 0, 100]

# 写法一：while + remove（remove 一次只删一个，所以要用循环）
while 0 in scores:
    scores.remove(0)
print(f"有效成绩 {len(scores)} 个，平均 {sum(scores) / len(scores):.1f} 分")

# 写法二：遍历副本，验证结果一致
scores2 = [88, 0, 92, 0, 75, 0, 100]
for s in scores2[:]:            # [:] 造一份副本，删原列表不影响遍历
    if s == 0:
        scores2.remove(s)
print("两次结果一致：", scores == scores2)
