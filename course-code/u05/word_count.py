# word_count.py —— 用字典统计词频

text = "the quick brown fox jumps over the lazy dog the end"
print("原文：", text)

# 1）转小写，避免 The 和 the 被当成不同的词
text = text.lower()

# 2）按空格切分成单词列表
words = text.split(" ")          # ['the', 'quick', 'brown', ...]
print("切分结果：", words)

# 3）用字典计数（最基础也最重要的写法）
counts = {}
for word in words:
    if word in counts:
        counts[word] += 1     # 已经见过，计数加一
    else:
        counts[word] = 1      # 第一次见，计数为一

print("词频统计：", counts)
# {'the': 3, 'quick': 1, 'brown': 1, 'fox': 1, 'jumps': 1,
#  'over': 1, 'lazy': 1, 'dog': 1, 'end': 1}

# 4）找出出现次数最多的词
most_common_word = max(counts, key=counts.get)
print(f"出现最多的词：{most_common_word}，出现了 {counts[most_common_word]} 次")

# ===== 进阶版本：处理带标点的文本 =====
messy = "Hello, world! Hello Python, python is fun. Is python fun?"
print("\n原始文本：", messy)

# 先把所有常见标点替换成空格，这样 split 就能切干净
cleaned = messy
for symbol in [",", "!", ".", "?", ";", ":"]:
    cleaned = cleaned.replace(symbol, " ")
print("清洗后：", cleaned)

counts2 = {}
for word in cleaned.lower().split():
    counts2[word] = counts2.get(word, 0) + 1

print("词频：", counts2)
# 进阶写法：counts2[word] = counts2.get(word, 0) + 1
# 含义是"取这个键的值，没有就用 0；然后加 1 再存回去"。
# 这一行等价于上面的 if/else 两种情况，是最常用的计数写法。
