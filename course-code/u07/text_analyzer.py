# text_analyzer.py —— 文本统计分析函数

def analyze_text(text):
    """分析一段文本，返回包含各项统计信息的字典。

    返回的字典包含：
        字符数     不含空格的字符总数
        单词数     按空格切分后的单词数量
        最长单词   长度最大的单词
        各单词次数 {单词: 出现次数}
    """
    # 切分成单词列表
    words = text.split()

    # 统计各单词出现次数（单元 5 的计数方法）
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1

    # 找最长单词
    longest = ""
    for word in words:
        if len(word) > len(longest):
            longest = word

    return {
        "字符数": len(text.replace(" ", "")),
        "单词数": len(words),
        "最长单词": longest,
        "各单词次数": counts,
    }


def print_report(text):
    """调用 analyze_text 并格式化输出所有信息。"""
    result = analyze_text(text)

    print("=" * 40)
    print("文本分析报告")
    print("=" * 40)
    print(f"原文：{text}")
    print(f"字符数（不含空格）：{result['字符数']}")
    print(f"单词数：{result['单词数']}")
    print(f"最长单词：{result['最长单词']}（{len(result['最长单词'])} 个字母）")
    print("-" * 40)
    print("词频统计：")
    for word, count in sorted(result["各单词次数"].items(), key=lambda x: -x[1]):
        print(f"  {word:<10} {count} 次")


# 测试
text = "the quick brown fox jumps over the lazy dog"
print_report(text)

# 进阶：统计出现次数最多的词
print()
result = analyze_text(text)
top_word = max(result["各单词次数"], key=result["各单词次数"].get)
print(f"出现最多的词是 '{top_word}'，出现了 {result['各单词次数'][top_word]} 次")

# 顺带演示：注意"字符数不含空格"和"含空格"的区别
sample = "a b c"
print()
print(f"'{sample}' 的字符数（不含空格）：{analyze_text(sample)['字符数']}")  # 3
print(f"'{sample}' 的单词数：{analyze_text(sample)['单词数']}")             # 3
