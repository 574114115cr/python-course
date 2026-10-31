# list_order.py —— 顺序相关的实用方法

ages = [30, 25, 35, 20, 28]
print("原始：", ages)

# sort()：原地排序（修改原列表），返回 None
ages.sort()
print("升序 sort 后：", ages)      # [20, 25, 28, 30, 35]

# sort(reverse=True)：降序
ages.sort(reverse=True)
print("降序后：", ages)            # [35, 30, 28, 25, 20]

# sorted()：返回排好序的**新列表**，原列表不动
scores = [88, 95, 72, 100, 61]
top3 = sorted(scores, reverse=True)[:3]   # 前三名
print("原列表没变：", scores)     # [88, 95, 72, 100, 61]
print("前三名：", top3)           # [100, 95, 88]

# 按字母排序
names = ["dave", "alice", "Bob", "charlie"]
print("原样：", names)
print("按字母（区分大小写）：", sorted(names))          # Bob, alice, charlie, dave
print("忽略大小写：", sorted(names, key=str.lower))     # Alice, bob, charlie, dave

# reverse()：原地反转
nums = [1, 2, 3, 4, 5]
nums.reverse()
print("反转后：", nums)            # [5, 4, 3, 2, 1]

# count() 和 index()：计数与查找位置
fruits = ["苹果", "香蕉", "苹果", "橙子"]
print("苹果有几个：", fruits.count("苹果"))    # 2
print("橙子在第几个：", fruits.index("橙子"))  # 3（索引从 0 开始）
# print(fruits.index("葡萄"))     # ValueError: '葡萄' is not in list
