# sort_compare.py —— sorted 与 sort 的区别
scores = [88, 92, 75, 100, 67]

print("原列表", scores)
print("升序  ", sorted(scores))
print("降序  ", sorted(scores, reverse=True))

mine = scores[:]          # 先复制，再原地排序
mine.sort()
print("原地排序后", mine)
print("原列表仍是", scores)
