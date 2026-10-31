# main.py —— 项目骨架

# 1）导入
import json
import os

# 2）常量配置
DATA_FILE = "data.json"

# 3）数据模型（类）
class Item:
    """一条数据。"""
    def __init__(self, title, value=0):
        self.title = title
        self.value = value

    def __str__(self):
        return f"{self.title} ({self.value})"


# 4）业务逻辑（函数）—— 核心逻辑必须是纯函数，方便测试
def add_items(items, new_items):
    """合并两个列表，返回新列表。"""
    return items + new_items


def summarize(items):
    """统计数据，返回字典。"""
    if not items:
        return {"count": 0, "total": 0, "max": None}
    values = [item.value for item in items]
    return {
        "count": len(items),
        "total": sum(values),
        "max": max(values),
    }


# 5）持久化层
def load_data(filename=DATA_FILE):
    """从文件加载，失败时返回空列表而不是崩溃。"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Item(d["title"], d["value"]) for d in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_data(items, filename=DATA_FILE):
    """保存到文件。"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            [{"title": i.title, "value": i.value} for i in items],
            f,
            ensure_ascii=False,
            indent=2,
        )


# 6）用户交互层
def main():
    """程序入口。"""
    items = load_data()
    print(f"已加载 {len(items)} 条数据")

    while True:
        print("\n1. 查看统计  2. 添加数据  3. 保存退出")
        choice = input("请选择：")

        if choice == "1":
            stats = summarize(items)
            for key, value in stats.items():
                print(f"  {key}: {value}")
        elif choice == "2":
            try:
                title = input("标题：")
                value = int(input("数值："))
                items.append(Item(title, value))
                print(f"已添加：{items[-1]}")
            except ValueError:
                print("数值必须是整数")
        elif choice == "3":
            save_data(items)
            print("已保存，再见！")
            break
        else:
            print("无效选项")


# 7）入口保护：只有直接运行这个文件时才执行 main
if __name__ == "__main__":
    main()
