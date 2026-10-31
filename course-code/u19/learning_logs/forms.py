# learning_logs/forms.py —— 根据模型 Topic 自动生成表单
from django import forms

from .models import Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic                  # 根据哪个模型生成
        fields = ["text"]              # 白名单：只暴露 text 这一个字段
        labels = {"text": ""}          # 不生成字段标签
