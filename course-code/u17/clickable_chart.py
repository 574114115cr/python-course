# clickable_chart.py —— 带缓存兜底的可点击仓库榜
# 跑完生成 clickable.html 和 github_repos.json，可以删掉
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests

CACHE = Path("github_repos.json")
HEADERS = {"Accept": "application/vnd.github+json"}
# 最后一行的 html_url 是空字符串（诱饵），用来验证链接点不动的情况
RAW = [("awesome-python", 220000, "vinta"), ("django", 78000, "django"),
       ("flask", 67000, "pallets"), ("诱饵仓库", 5000, "nobody")]
SAMPLE_ITEMS = [
    {"name": n, "stargazers_count": s, "owner": {"login": o}, "description": f"示例 {n}",
     "html_url": "" if n == "诱饵仓库" else f"https://github.com/{o}/{n}"}
    for n, s, o in RAW]


def fetch_top_repos(count=10):
    """调用 GitHub search API；失败返回 None（并打印原因）。"""
    params = {"q": "language:python", "sort": "stars", "per_page": count}
    try:
        response = requests.get("https://api.github.com/search/repositories",
                                headers=HEADERS, params=params, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"网络请求失败：{error}")
        return None
    if response.status_code != 200:
        print("状态码", response.status_code, "配额",
              response.headers.get("X-RateLimit-Remaining"))
        return None
    CACHE.write_text(response.text, encoding="utf-8")      # 存缓存供下次用
    return response.json()["items"]


def load_cache():
    """读缓存；文件不存在或内容坏了都返回 None。"""
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))["items"]
    except (OSError, ValueError, KeyError) as error:
        print(f"没有可用缓存（{type(error).__name__}）")
        return None


items = load_cache() or fetch_top_repos()      # 优先读缓存，没有再请求网络
if items is None:
    print("当前使用示例数据（没有网络）")
    items = SAMPLE_ITEMS

df = pd.DataFrame({"name": [r["name"] for r in items],
                   "stars": [r["stargazers_count"] for r in items],
                   "description": [r["description"] or "（没写简介）" for r in items],
                   "owner": [r["owner"]["login"] for r in items],
                   "html_url": [r["html_url"] for r in items]})

fig = px.bar(
    df, x="name", y="stars", hover_name="name",
    hover_data=["description", "owner"],
    custom_data=["html_url"],                     # ★ 把链接挂到柱子上
    color="owner",
    color_discrete_map={"vinta": "seagreen", "django": "green",
                        "pallets": "darkorange", "nobody": "gray"},
    text_auto=".2s",
    title="Most-Starred Python Repositories",
)
fig.update_traces(marker_line_width=1.5,
                  hovertemplate="<b>%{hovertext}</b><br>Stars: %{y:,}<br>"
                                "<a href='%{customdata[0]}'>Open in GitHub</a>"
                                "<extra></extra>")
fig.update_layout(
    title={"text": "Most-Starred Python Repositories", "x": 0.5, "xanchor": "center"},
    xaxis_title=None, yaxis_title="Stars")
fig.write_html("clickable.html")

print("已生成 clickable.html —— 「诱饵仓库」的 html_url 是空字符串，链接空白且点不动。")
print("解法：url 为空时兜底成讨论页，或不放 <a> 标签只显示纯文本。")
