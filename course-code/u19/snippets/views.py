# learning_logs/views.py（片段）—— new_entry() 加归属检查（教材练习 19.4）
@login_required
def new_entry(request, topic_id):
    """在特定主题中添加新条目。"""
    topic = Topic.objects.get(id=topic_id)
    # 保存条目之前，先确认主题属于当前用户
    check_topic_owner(topic, request)

    if request.method != "POST":
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect("learning_logs:topic", topic_id=topic_id)

    context = {"topic": topic, "form": form}
    return render(request, "learning_logs/new_entry.html", context)
