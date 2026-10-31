# file_review.py —— 文件与异常的完整复习

import json
import csv
import os
import tempfile


def file_basics_demo():
    """读写文件与三种模式。"""
    filename = "复习_文件.txt"

    # w：写入并清空
    with open(filename, "w", encoding="utf-8") as f:
        f.write("第一行\n")

    # a：追加
    with open(filename, "a", encoding="utf-8") as f:
        f.write("第二行\n")

    # r：读取全部
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 逐行读（推荐方式）
    lines = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())

    os.remove(filename)
    return content, lines


def json_demo():
    """JSON 读写。"""
    filename = "复习_data.json"
    data = {"name": "小明", "scores": [90, 85, 92], "active": True}

    # 写
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 读
    with open(filename, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    os.remove(filename)
    return loaded, loaded == data


def csv_demo():
    """CSV 读写。"""
    filename = "复习_data.csv"
    rows = [["姓名", "成绩"], ["小明", 92], ["小红", 88]]

    # 写
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

    # 读
    with open(filename, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    os.remove(filename)
    return data


def exception_demo():
    """四种异常结构。"""
    results = []

    # try / except
    try:
        int("abc")
    except ValueError as error:
        results.append(f"捕获异常：{error}")

    # try / except / else
    try:
        value = int("42")
    except ValueError:
        results.append("不该走到这里")
    else:
        results.append(f"else 分支：转换成功 {value}")

    # try / finally
    def with_finally():
        try:
            return "try 的返回值"
        finally:
            results.append("finally 一定会执行")

    with_finally()

    # 主动抛出
    def validate(age):
        if age < 0:
            raise ValueError("年龄不能为负")
        return True

    try:
        validate(-1)
    except ValueError as error:
        results.append(f"主动抛出被捕获：{error}")

    return results


if __name__ == "__main__":
    print("【文件读写】")
    print(file_basics_demo())

    print("\n【JSON】")
    print(json_demo())

    print("\n【CSV】")
    print(csv_demo())

    print("\n【异常】")
    for item in exception_demo():
        print(" ", item)
