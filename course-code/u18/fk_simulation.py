# fk_simulation.py —— 模拟 models.ForeignKey 背后发生的事

class Topic:
    """主题：相当于数据库表 learning_logs_topic 里的一行。"""

    def __init__(self, topic_id, text):
        self.id = topic_id
        self.text = text

    def __str__(self):
        return self.text


class Entry:
    """条目：topic 这一列「指向」某个主题——这就是外键。"""

    def __init__(self, entry_id, topic, text):
        self.id = entry_id
        self.topic = topic          # 外键：记住自己属于哪个主题
        self.text = text

    def __str__(self):
        return self.text[:20]


# ===== 造数据：两个主题、三条条目（一对多）=====
python_topic = Topic(1, "Python")
django_topic = Topic(2, "Django")
entries = [
    Entry(1, python_topic, "列表推导式很好用"),
    Entry(2, python_topic, "生成器可以省内存"),
    Entry(3, django_topic, "先建虚拟环境再装包"),
]

print("删除前，所有条目：")
for entry in entries:
    print(f"  条目{entry.id}: {entry} -> 属于《{entry.topic}》")


# ===== 模拟 on_delete=models.CASCADE（级联删除）=====
def delete_topic_cascade(topic, all_entries):
    """级联删除：剔除该主题，以及挂在它下面的全部条目。"""
    return [e for e in all_entries if e.topic is not topic]


entries = delete_topic_cascade(python_topic, entries)
print("\n删除《Python》后（CASCADE 生效），剩下的条目：")
for entry in entries:
    print(f"  条目{entry.id}: {entry} -> 属于《{entry.topic}》")

# ===== 对比：没有 on_delete 规则会怎样 =====
orphan = Entry(99, python_topic, "这条的作者已经没人认领了")
print(f"\n假如没有级联删除，数据库里会留下孤儿：")
print(f"  条目{orphan.id}: {orphan} -> 指向的主题《{orphan.topic}》已不存在")
print("  => 显示、查询时全是麻烦，所以 on_delete 必须显式写清楚")
