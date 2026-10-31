# text_analyzer.py —— 综合项目 3：文本统计工具

import json
import os
import re
import sys

STOP_WORDS = {
    "的", "了", "是", "在", "和", "有", "我", "你", "他", "她", "它",
    "这", "那", "就", "都", "而", "及", "与", "着", "或", "一个", "没有",
    "我们", "你们", "他们", "这个", "那个", "什么", "可以", "因为", "所以",
    "但是", "如果", "这样", "那样", "自己", "已经", "还是", "就是", "不是",
    # 英文常见停用词
    "the", "a", "an", "is", "are", "was", "were", "and", "or", "of",
    "to", "in", "on", "at", "it", "this", "that",
}


def clean_text(text):
    """清洗文本：去掉多余空白，统一为单个空格分隔。"""
    return re.sub(r"\s+", " ", text).strip()


def count_chars(text, include_spaces=False):
    """统计字符数。"""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def count_words(text):
    """统计单词数（中文按连续汉字计为一个词，英文按空格切分）。

    这是本项目的核心难点：用正则把中英文分别处理。
    """
    # 英文单词：连续字母
    english = re.findall(r"[a-zA-Z]+", text)
    # 中文：连续的汉字串算一个"词"
    chinese = re.findall(r"[\u4e00-\u9fff]+", text)
    return len(english) + len(chinese)


def count_lines(text):
    """统计行数。"""
    if not text:
        return 0
    return len(text.split("\n"))


def count_sentences(text):
    """统计句子数（按中英文句号、问号、感叹号划分）。"""
    sentences = re.split(r"[。！？.!?]+", text)
    # 过滤掉空白片段
    return len([s for s in sentences if s.strip()])


def tokenize(text):
    """把文本切分成词列表（中英文都处理）。"""
    tokens = re.findall(r"[a-zA-Z]+|[\u4e00-\u9fff]+", text)
    return [t.lower() for t in tokens]


def word_frequency(text, remove_stop_words=True, min_length=1):
    """统计词频，返回 {词: 次数}。"""
    tokens = tokenize(text)
    counts = {}
    for token in tokens:
        if len(token) < min_length:
            continue
        if remove_stop_words and token in STOP_WORDS:
            continue
        counts[token] = counts.get(token, 0) + 1
    return counts


def top_words(text, n=10, remove_stop_words=True):
    """返回出现频率最高的 n 个词。"""
    counts = word_frequency(text, remove_stop_words)
    # 先按次数降序，次数相同时按词本身排序，保证结果稳定
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:n]


def analyze_text(text):
    """综合分析，返回完整结果字典。这是核心的纯函数。"""
    cleaned = clean_text(text)
    counts = word_frequency(cleaned)
    return {
        "字符数": count_chars(cleaned),
        "字符数_含空格": count_chars(cleaned, include_spaces=True),
        "单词数": count_words(cleaned),
        "句子数": count_sentences(cleaned),
        "行数": count_lines(text),
        "不同词数": len(counts),
        "总词频": sum(counts.values()),
        "高频词": dict(top_words(cleaned, 10)),
        "平均句长": (
            round(count_words(cleaned) / count_sentences(cleaned), 2)
            if count_sentences(cleaned) > 0 else 0.0
        ),
    }


def analyze_file(filepath, remove_stop_words=True):
    """分析单个文件，容错处理各种异常。"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {"错误": f"文件不存在：{filepath}"}
    except UnicodeDecodeError:
        # 尝试其他编码
        for encoding in ("gbk", "utf-8-sig", "latin-1"):
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            return {"错误": f"无法解码文件（编码不匹配）：{filepath}"}
    except IsADirectoryError:
        return {"错误": f"这是一个目录，不是文件：{filepath}"}
    except PermissionError:
        return {"错误": f"没有读取权限：{filepath}"}
    except OSError as error:
        return {"错误": f"读取失败：{error}"}

    if not text.strip():
        return {"错误": f"文件是空的：{filepath}"}

    result = analyze_text(text)
    result["文件"] = filepath
    result["文件名"] = os.path.basename(filepath)
    result["过滤停用词"] = remove_stop_words
    return result


def save_report(results, filename="text_report.json"):
    """把分析结果保存为 JSON。"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"报告已保存到 {filename}")
        return True
    except Exception as error:
        print(f"保存失败：{error}")
        return False


def print_report(result):
    """格式化打印分析结果。"""
    if "错误" in result:
        print(f"  [错误] {result['错误']}")
        return

    print(f"\n{'=' * 46}")
    print(f"文件：{result['文件名']}")
    print(f"{'=' * 46}")
    print(f"  字符数（不含空格）：{result['字符数']}")
    print(f"  字符数（含空格）：  {result['字符数_含空格']}")
    print(f"  单词数：    {result['单词数']}")
    print(f"  句子数：    {result['句子数']}")
    print(f"  行数：      {result['行数']}")
    print(f"  不同词数：  {result['不同词数']}")
    print(f"  平均句长：  {result['平均句长']}")
    print(f"  高频词 Top 10：")
    for word, count in result["高频词"].items():
        bar = "█" * min(count, 20)
        print(f"    {word:<12}{count:>4} 次 {bar}")


def main():
    print("=" * 50)
    print("文本统计工具")
    print("=" * 50)

    # 命令行参数传入文件，或者交互式输入
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        print(f"\n分析 {len(files)} 个文件：")
    else:
        print("\n请输入要分析的文件路径（多个用空格分隔）：")
        user_input = input("> ").strip()
        files = user_input.split() if user_input else []

    if not files:
        print("没有指定文件。示例：python text_analyzer.py article.txt")
        # 用示例文本演示
        demo = "Python 是一种编程语言。它简单易学，功能强大。Python 在数据科学领域应用广泛。"
        print("\n=== 示例文本分析 ===")
        result = analyze_text(demo)
        result["文件名"] = "（内置示例）"
        result["文件"] = "内存"
        result["过滤停用词"] = True
        print_report(result)
        return

    results = []
    for filepath in files:
        result = analyze_file(filepath)
        print_report(result)
        results.append(result)

    # 汇总
    successful = [r for r in results if "错误" not in r]
    if successful:
        print(f"\n{'=' * 46}")
        print(f"汇总：成功分析 {len(successful)} 个文件，"
              f"失败 {len(results) - len(successful)} 个")
        total_words = sum(r["单词数"] for r in successful)
        print(f"总单词数：{total_words}")

        if input("\n是否保存报告到 JSON？(y/n)：").lower() == "y":
            save_report(results)


if __name__ == "__main__":
    main()
