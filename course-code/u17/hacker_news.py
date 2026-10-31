# hacker_news.py —— 先列表、再详情，限速 + 失败处理
# 没网时自动改用内置样例，保证程序跑完；跑完的 hn_top.html 可以删掉
import time

import pandas as pd
import plotly.express as px
import requests

TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
TOP_N = 5
FALLBACK = {38491381: {"title": "Hammerspace Interaction", "score": 216},
            38491760: {"title": "Ask HN", "score": 158,
                       "url": None},                   # ★ 没外链，测兜底
            38491822: {"title": "Why SQLite", "score": 142}}


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


# ===== 第一段：拿 id 列表；拿不到就用内置样例 =====
story_ids = get_json(TOP_URL) or list(FALLBACK)
print(f"第一段：{len(story_ids)} 个 id，只取前 {TOP_N} 条")

# ===== 第二段：逐个 id 取详情 =====
titles, scores, links = [], [], []
for index, story_id in enumerate(story_ids[:TOP_N]):
    if index > 0:
        time.sleep(1)                  # 主动限速
    item_dict = get_json(ITEM_URL.format(id=story_id)) or FALLBACK.get(story_id)
    if not item_dict:
        print(f"  跳过 id {story_id}")
        continue
    titles.append(item_dict.get("title") or "(无标题)")
    scores.append(item_dict.get("score", 0))
    # ★ url 可能是 None，兜底成讨论页，保证每根柱子都有链接
    links.append(item_dict.get("url")
                 or f"https://news.ycombinator.com/item?id={story_id}")
    print(f"  {titles[-1]:<45}{scores[-1]:>5}")

# ===== 画图 =====
if titles:
    df = pd.DataFrame({"title": titles, "score": scores, "link": links})
    fig = px.bar(df, x="title", y="score", hover_name="title",
                 custom_data=["link"], title="Top HN Stories")
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Score: %{y:,}<br>"
                     "<a href='%{customdata[0]}'>Read</a><extra></extra>")
    fig.update_layout(xaxis_title=None, yaxis_title="Score",
                      title={"text": "Top HN Stories", "x": 0.5, "xanchor": "center"})
    fig.write_html("hn_top.html")
    print(f"\n已生成 hn_top.html（{len(titles)} 条）")
else:
    print("没有拿到可用数据，跳过画图")
