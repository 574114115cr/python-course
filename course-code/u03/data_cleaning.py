# data_cleaning.py —— 数据清洗实战

raw = ["  苹果  ", "香蕉", "", "  ", "橙子", None, "  葡萄"]

# ===== 写法一：列表推导式（简洁）=====
# 注意：`if item` 这个条件能过滤掉 ""，但过滤不掉 None，
# 因为 None 在 if 判断中等于 False，所以其实是能过滤掉的。
# 写两个条件也可以，但一个 if item 就够了。
cleaned = [item.strip() for item in raw if item]
print("推导式结果：", cleaned)
# ['苹果', '香蕉', '橙子', '葡萄']

# ===== 写法二：普通 for 循环（逻辑更清晰时用）=====
cleaned2 = []
for item in raw:
    if item is None:# 先挡掉 None，否则 .strip() 会崩
        continue                     # continue = 跳过本轮，继续下一次循环
    stripped = item.strip()# 去首尾空格
    if stripped:                     # 非空才留下
        cleaned2.append(stripped)

print("循环结果：", cleaned2)
print("两者一致：", cleaned == cleaned2)

# 统计清洗掉了几个
print("原始数量：", len(raw), "清洗后数量：", len(cleaned))
print("清掉了：", len(raw) - len(cleaned), "个")   # 3 个

# 去重（保序）
unique = []
for item in cleaned:
    if item not in unique:
        unique.append(item)
print("去重后：", unique)
