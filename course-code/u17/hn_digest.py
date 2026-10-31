# hn_digest.py —— Hacker News 两段式调用
# 跑完生成 hn_digest.html，可以删掉
import time

import pandas as pd
import plotly.express as px
import requests

TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
TOP_N = 10


def get_json(url):
    """try/except + 状态码检查，失败返回 None。"""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"  请求失败：{type(error).__name__}")
        return None
    if response.status_code != 200:
        print(f"  状态码 {response.status_code}，跳过")
        return None
    return response.json()


story_ids = get_json(TOP_URL)          # ===== 第一段：拿 id 列表 =====
titles, scores, authors, comments, links = [], [], [], [], []
skipped = 0

if not story_ids:
    print("拿不到列表，程序结束（网络不通时不画图，也不崩）")
else:
    print(f"第一段：{len(story_ids)} 个 id，只处理前 {TOP_N} 个")
    for index, story_id in enumerate(story_ids[:TOP_N]):   # ===== 第二段：逐个取详情 =====
        if index > 0:
            time.sleep(1)                 # 主动限速
        item_dict = get_json(ITEM_URL.format(id=story_id))
        # None = 网络/状态码问题；返回 JSON null = 条目已被删除，两种都要 continue
        if not isinstance(item_dict, dict):
            print(f"  id {story_id} 请求失败或已删除，跳过")
            skipped += 1
            continue
        titles.append(item_dict.get("title") or "(无标题)")
        scores.append(item_dict.get("score", 0))
        # ★ "by" 是合法 JSON 键，但 by 是 Python 关键字，只能直接取值
        authors.append(item_dict.get("by", "匿名"))
        comments.append(item_dict.get("descendants", 0))
        links.append(item_dict.get("url")          # ★ url 可能是 null，兜底讨论页
                     or f"https://news.ycombinator.com/item?id={story_id}")

if titles:
    print(f"\n成功 {len(titles)} 条，跳过 {skipped} 条")
    # x 轴标签自己截断到 30 字符，否则标签互相重叠看不清
    labels = [t if len(t) <= 30 else t[:29] + "…" for t in titles]
    df = pd.DataFrame({"title": labels, "score": scores, "author": authors,
                       "comments": comments, "link": links})
    fig = px.bar(df, x="title", y="score", hover_name="title",
                 custom_data=["author", "comments", "link"],
                 title="Top Hacker News Stories")
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>by %{customdata[0]}<br>Score: %{y:,}<br>"
                      "Comments: %{customdata[1]}<br>"
                      "<a href='%{customdata[2]}'>Read</a><extra></extra>")
    fig.update_layout(xaxis_title=None, yaxis_title="Score",
                      title={"text": "Top Hacker News Stories",
                             "x": 0.5, "xanchor": "center"},
                      xaxis={"tickangle": -30})   # 标签斜一点，少重叠
    fig.write_html("hn_digest.html")
else:
    print("没有可用数据，跳过画图")
