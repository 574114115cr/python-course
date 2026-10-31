# todo_manager.py —— 综合项目 1：命令行待办事项管理器

import json
import os
import csv

TODO_FILE = "todos.json"
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
STOP_WORDS = set()


class Task:
    """一个待办任务。"""
    def __init__(self, title, priority="中", done=False, created_at=None):
        if priority not in PRIORITY_ORDER:
            raise ValueError("优先级必须是高、中、低之一")
        self.title = title
        self.priority = priority
        self.done = done
        self.created_at = created_at or self._now()

    @staticmethod
    def _now():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def complete(self):
        """标记完成，返回自身支持链式调用。"""
        self.done = True
        return self

    def undo(self):
        """取消完成。"""
        self.done = False
        return self

    def toggle(self):
        """切换完成状态。"""
        self.done = not self.done
        return self

    def matches(self, keyword):
        """是否包含关键字（不区分大小写）。"""
        return keyword.lower() in self.title.lower()

    def to_dict(self):
        return {
            "title": self.title,
            "priority": self.priority,
            "done": self.done,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            priority=data.get("priority", "中"),
            done=data.get("done", False),
            created_at=data.get("created_at"),
        )

    def __str__(self):
        mark = "✓" if self.done else "○"
        return f"{mark} [{self.priority}] {self.title}"


class TodoManager:
    """待办管理器：负责所有业务逻辑与数据持久化。"""

    def __init__(self, filename=TODO_FILE):
        self.filename = filename
        self.tasks = []
        self.load()

    # ===== 持久化 =====
    def load(self):
        """从文件加载，失败时降级为空列表。"""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [Task.from_dict(item) for item in data]
            print(f"已从 {self.filename} 加载 {len(self.tasks)} 个任务")
        except FileNotFoundError:
            self.tasks = []
            print(f"{self.filename} 不存在，从空列表开始")
        except json.JSONDecodeError:
            self.tasks = []
            print(f"{self.filename} 内容损坏，已重置为空列表")
        except Exception as error:
            self.tasks = []
            print(f"加载失败：{error}")

    def save(self):
        """保存到文件。"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"已保存到 {self.filename}")
        except Exception as error:
            print(f"保存失败：{error}")

    # ===== 增删改查 =====
    def add(self, title, priority="中"):
        """添加任务，标题重复时返回 False。"""
        title = title.strip()
        if not title:
            print("标题不能为空")
            return False
        if any(task.title == title for task in self.tasks):
            print(f"任务 '{title}' 已存在")
            return False
        try:
            self.tasks.append(Task(title, priority))
            print(f"已添加：{self.tasks[-1]}")
            return True
        except ValueError as error:
            print(f"添加失败：{error}")
            return False

    def find(self, title):
        """按标题找任务，找不到返回 None。"""
        for task in self.tasks:
            if task.title == title:
                return task
        return None

    def toggle(self, title):
        task = self.find(title)
        if task is None:
            print(f"未找到任务：{title}")
            return False
        task.toggle()
        status = "已完成" if task.done else "已取消完成"
        print(f"'{title}' 已标记为{status}")
        return True

    def delete(self, title):
        original = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.title != title]
        if len(self.tasks) < original:
            print(f"已删除：{title}")
            return True
        print(f"未找到任务：{title}")
        return False

    # ===== 查询与统计（纯函数，不做 I/O）=====
    def list_all(self, show_done=True):
        """按优先级列出任务。"""
        visible = [t for t in self.tasks if show_done or not t.done]
        visible.sort(key=lambda t: (PRIORITY_ORDER[t.priority], t.created_at))
        if not visible:
            print("  （没有任务）")
            return []
        print(f"  共 {len(visible)} 个任务：")
        for task in visible:
            print(f"    {task}")
        return visible

    def search(self, keyword):
        """按关键字搜索。"""
        found = [t for t in self.tasks if t.matches(keyword)]
        if not found:
            print(f"  没有包含 '{keyword}' 的任务")
            return []
        print(f"  找到 {len(found)} 个任务：")
        for task in found:
            print(f"    {task}")
        return found

    def statistics(self):
        """统计信息。"""
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.done])
        by_priority = {}
        for priority in PRIORITY_ORDER:
            count = len([t for t in self.tasks if t.priority == priority])
            by_priority[priority] = count
        return {
            "总数": total,
            "已完成": done,
            "待办": total - done,
            "高优先级": by_priority["高"],
            "中优先级": by_priority["中"],
            "低优先级": by_priority["低"],
            "完成率": f"{done / total * 100:.1f}%" if total else "0.0%",
        }

    def export_csv(self, filename="todos.csv"):
        """导出为 CSV。"""
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["标题", "优先级", "状态", "创建时间"])
                for task in self.tasks:
                    writer.writerow([
                        task.title,
                        task.priority,
                        "已完成" if task.done else "待办",
                        task.created_at,
                    ])
            print(f"已导出到 {filename}")
            return True
        except Exception as error:
            print(f"导出失败：{error}")
            return False


# ===== 用户交互 =====
MENU = """
========== 待办事项管理器 ==========
1. 添加任务
2. 列出任务
3. 标记完成/取消
4. 删除任务
5. 搜索任务
6. 统计信息
7. 导出 CSV
0. 保存并退出
===================================
"""


def main():
    manager = TodoManager()

    while True:
        print(MENU)
        choice = input("请选择操作：").strip()

        try:
            if choice == "1":
                title = input("任务标题：")
                priority = input("优先级（高/中/低，直接回车为中）：").strip() or "中"
                manager.add(title, priority)
            elif choice == "2":
                show_done = input("显示已完成任务吗？(y/n)：").lower() != "n"
                manager.list_all(show_done)
            elif choice == "3":
                title = input("要切换的任务标题：")
                manager.toggle(title)
            elif choice == "4":
                title = input("要删除的任务标题：")
                confirm = input(f"确定删除 '{title}' 吗？(y/n)：").lower()
                if confirm == "y":
                    manager.delete(title)
            elif choice == "5":
                keyword = input("搜索关键字：")
                manager.search(keyword)
            elif choice == "6":
                print("\n--- 统计信息 ---")
                for key, value in manager.statistics().items():
                    print(f"  {key}: {value}")
            elif choice == "7":
                manager.export_csv()
            elif choice == "0":
                manager.save()
                print("再见！")
                break
            else:
                print("无效选项，请重新输入")

        except KeyboardInterrupt:
            # 不该被裸 except 吞掉
            print("\n检测到 Ctrl+C，正在保存并退出...")
            manager.save()
            break
        except Exception as error:
            # 兜底：保证任何意外都不会让程序崩溃
            print(f"发生未预期的错误：{error}")

    # 清理
    if os.path.exists(TODO_FILE):
        os.remove(TODO_FILE)


if __name__ == "__main__":
    main()
