# learning_logs/models.py —— Entry.__str__() 仅在超过 50 字符时加省略号
from django.db import models


class Topic(models.Model):
    """用户学习的主题"""

    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Entry(models.Model):
    """学到的有关某个主题的具体知识"""

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "entries"

    def __str__(self):
        """条目超过 50 个字符时才加省略号。"""
        if len(self.text) > 50:
            return f"{self.text[:50]}..."
        return self.text
