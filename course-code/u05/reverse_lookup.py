# reverse_lookup.py —— 字典的反向查找

scores = {"小明": 95, "小红": 88, "小刚": 72, "小丽": 91}

# 1）字典推导式构造反向字典 {分数: 姓名}
name_by_score = {score: name for name, score in scores.items()}
print("正向（姓名 -> 分数）：", scores)
print("反向（分数 -> 姓名）：", name_by_score)

# 2）查询 91 分是谁
target = 91
print(f"{target} 分是谁：", name_by_score.get(target, "查无此人"))   # 小丽

# 3）找出分数最高的学生的姓名
# 错误思路：max(name_by_score) 拿到的是最大的"键"，也就是 95
# 那是分数，不是姓名
top_name = max(scores, key=scores.get)
print(f"最高分学生：{top_name}，{scores[top_name]} 分")   # 小明，95 分
# key=scores.get 的意思是"比较时用 scores 里对应的值当标准"

# 最低分学生
low_name = min(scores, key=scores.get)
print(f"最低分学生：{low_name}，{scores[low_name]} 分")

# 4）按分数从高到低排好的姓名列表
ordered_names = [
    name
    for name, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
]
print("排名：", ordered_names)    # ['小明', '小丽', '小红', '小刚']

# 用 lambda 解释一下：item 就是一个 (姓名, 分数) 的元组，
# item[1] 就是分数，我们按分数排序。
# 如果写成 key=scores.get 也可以，那是因为 sorted 前要先转成列表对齐名字，
# 但用 lambda 更通用、更清楚。
