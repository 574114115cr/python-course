# palindrome.py —— 忽略大小写与空格
def is_palindrome(s):
    cleaned = [ch.lower() for ch in s if ch != " "]   # 去掉空格并统一小写
    text = "".join(cleaned)
    return text == text[::-1]                          # 反转后比较


cases = ["上海自来水来自海上", "A man a plan a canal Panama", "python"]
for c in cases:
    print(c, "→", is_palindrome(c))
