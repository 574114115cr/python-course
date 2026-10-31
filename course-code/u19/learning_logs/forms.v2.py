# learning_logs/forms.py —— 把模型变成表单（ModelForm）
from django import forms

from .models import Topic, Entry


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["text"]                     # 白名单：只暴露 text
        labels = {"text": ""}                 # 不生成字段标签


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["text"]
        labels = {"text": ""}
        widgets = {"text": forms.Textarea(attrs={"cols": 80})}
