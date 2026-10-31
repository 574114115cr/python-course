# todo.py —— 待办事项管理器（综合练习）

import json
import os

TASKS_FILE = "tasks.json"


class Task:
    """一个待办任务。"""
    PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}

    def __init__(self, title, priority="中", done=False):
        self.title = title
        self.priority = priority
        self.done = done

    def complete(self):
        """标记为已完成。"""
        self.done = True
        return self

    def to_dict(self):
        """转成字典，用于 JSON 序列化。"""
        return {
            "title": self.title,
            "priority": self.priority,
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data):
        """从字典还原成 Task 对象（反向操作）。"""
        return cls(
            title=data["title"],
            priority=data.get("priority", "中"),
            done=data.get("done", False),
        )

    def __str__(self):
        mark = "[已完成]" if self.done else "[待办]"
        return f"{mark} {self.title}（优先级：{self.priority}）"


class TodoManager:
    """待办事项管理器。"""

    def __init__(self, filename=TASKS_FILE):
        self.filename = filename
        self.tasks = []
        self.load()

    # ===== 文件读写 =====
    def load(self):
        """从 JSON 文件加载任务。文件不存在或损坏都不报错。"""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [Task.from_dict(item) for item in data]
            print(f"  已加载 {len(self.tasks)} 个任务")
        except FileNotFoundError:
            self.tasks = []
            print(f"  {self.filename} 不存在，从空列表开始")
        except json.JSONDecodeError:
            self.tasks = []
            print(f"  {self.filename} 内容损坏，从空列表开始")
        except OSError as error:
            self.tasks = []
            print(f"  读取失败：{error}")

    def save(self):
        """把所有任务保存到 JSON 文件。"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  已保存 {len(data)} 个任务到 {self.filename}")
        except OSError as error:
            print(f"  保存失败：{error}")

    # ===== 任务操作 =====
    def add(self, title, priority="中"):
        """添加一个任务。"""
        if any(task.title == title for task in self.tasks):
            print(f"  任务 '{title}' 已存在，跳过")
            return False
        self.tasks.append(Task(title, priority))
        print(f"  已添加：{title}")
        return True

    def complete(self, title):
        """标记指定任务为已完成。"""
        for task in self.tasks:
            if task.title == title:
                task.complete()
                print(f"  已完成：{title}")
                return True
        print(f"  未找到任务：{title}")
        return False

    def delete(self, title):
        """删除指定任务。"""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.title != title]
        if len(self.tasks) < original_count:
            print(f"  已删除：{title}")
            return True
        print(f"  未找到任务：{title}")
        return False

    def list_all(self, show_done=True):
        """列出任务，可选择是否显示已完成的。"""
        visible = [
            task for task in self.tasks
            if show_done or not task.done
        ]
        # 按优先级排序：高 -> 中 -> 低
        visible.sort(key=lambda t: Task.PRIORITY_ORDER.get(t.priority, 9))

        if not visible:
            print("  （没有任务）")
            return []

        print(f"  共 {len(visible)} 个任务：")
        for task in visible:
            print(f"    {task}")
        return visible

    def stats(self):
        """统计任务数量。"""
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.done])
        return {
            "总数": total,
            "已完成": done,
            "待办": total - done,
            "完成率": f"{done / total * 100:.1f}%" if total else "0%",
        }


# ===== 测试 =====
print("=== 1. 创建管理器（文件不存在）===")
manager = TodoManager()

print("\n=== 2. 添加任务 ===")
manager.add("写单元 9 讲义", "高")
manager.add("复习异常处理", "中")
manager.add("整理学习笔记", "低")
manager.add("写单元 9 讲义", "高")      # 故意重复，应该被拒绝

print("\n=== 3. 标记完成 ===")
manager.complete("复习异常处理")

print("\n=== 4. 列出所有任务 ===")
manager.list_all()

print("\n=== 5. 统计信息 ===")
for key, value in manager.stats().items():
    print(f"  {key}: {value}")

print("\n=== 6. 保存到文件 ===")
manager.save()

print("\n=== 7. JSON 文件内容 ===")
with open(TASKS_FILE, "r", encoding="utf-8") as f:
    print(f.read())

print("=== 8. 重新加载，验证数据完整性 ===")
# 关键：新建一个管理器，它会自动从文件读回数据
manager2 = TodoManager()
manager2.list_all()

print("\n=== 9. 验证：修改后再次保存，跨会话保持 ===")
manager2.add("开始单元 10：测试代码", "高")
manager2.save()

manager3 = TodoManager()
print("\n第三次加载后的任务列表：")
manager3.list_all()

# ===== 清理 =====
if os.path.exists(TASKS_FILE):
    os.remove(TASKS_FILE)
    print(f"\n已清理临时文件 {TASKS_FILE}")
