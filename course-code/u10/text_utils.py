# text_utils.py —— 被测模块

def count_words(text):
    """返回文本中的单词数，以空格分隔。"""
    if not text.strip():
        return 0
    return len(text.split())


def reverse(text):
    """返回反转后的字符串。"""
    return text[::-1]


def is_palindrome(text):
    """判断是否回文（忽略大小写、空格和常见标点）。"""
    # 清洗：只保留字母和数字，统一小写
    cleaned = "".join(
        char.lower()
        for char in text
        if char.isalnum()
    )
    return cleaned == cleaned[::-1]
