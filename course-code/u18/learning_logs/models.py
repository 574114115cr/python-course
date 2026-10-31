# learning_logs/models.py —— 学习笔记的数据模型
from django.db import models


class Topic(models.Model):
    """用户学习的主题（一对多关系里的「一」）。"""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """在管理网站和 shell 里显示主题时，返回 text。"""
        return self.text


class Entry(models.Model):
    """学到的有关某个主题的具体知识（一对多关系里的「多」）。"""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "entries"      # 否则管理网站会显示难看的 Entrys

    def __str__(self):
        """条目可能很长，只截取前 50 个字符显示。"""
        return f"{self.text[:50]}..."
