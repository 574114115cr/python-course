# longest_word.py —— 找出最长单词

def longest_word_loop(words):
    """用普通循环找最长单词，长度相同返回第一个。"""
    if not words:               # 空列表要提前处理
        return ""

    longest = words[0]          # 假设第 0 个最长
    for word in words:
        if len(word) > len(longest):     # 严格大于，所以同长度保留先来的
            longest = word
    return longest


def longest_word_max(words):
    """用内置 max 找最长单词。"""
    if not words:
        return ""
    return max(words, key=len)


# 测试
words = ["apple", "banana", "watermelon", "kiwi"]
print("输入：", words)
print("循环版：", longest_word_loop(words))     # watermelon
print("max 版：", longest_word_max(words))      # watermelon
print("两者一致：", longest_word_loop(words) == longest_word_max(words))

# 边界情况：长度相同时都应返回第一个
tie = ["apple", "mango", "pear"]              # mango 和 pear 都是 5 个字母
print()
print("并列时循环版：", longest_word_loop(tie))    # mango
print("并列时 max 版：", longest_word_max(tie))     # mango
# max 也返回第一个，这是 Python 的稳定行为

# 空列表
print()
print("空列表：", repr(longest_word_loop([])), repr(longest_word_max([])))

# 顺带演示：所有单词都返回
def all_longest_words(words):
    """返回所有达到最长长度的单词。"""
    if not words:
        return []
    max_len = max(len(w) for w in words)
    return [w for w in words if len(w) == max_len]


print("所有最长的：", all_longest_words(tie))    # ['mango', 'pear']
