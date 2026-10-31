# bar_chart.py —— 悬停提示 + 固定配色 + 可点击链接
# 跑完生成 bar_chart.html，用浏览器打开悬停并点击；看完可以删掉
import pandas as pd
import plotly.express as px

# 把平行列表装进 DataFrame，px 的列名写法（custom_data=["url"]）才可用
NAMES = ["awesome-python", "django", "flask"]
OWNERS = ["vinta", "django", "pallets"]
df = pd.DataFrame({"name": NAMES, "stars": [220000, 78000, 67000],
                   "description": ["Python 资源大全", "重量级 Web 框架", "轻量级 Web 框架"],
                   "owner": OWNERS,
                   "html_url": [f"https://github.com/{o}/{n}"
                                for o, n in zip(OWNERS, NAMES)]})

fig = px.bar(
    df, x="name", y="stars",
    hover_name="name",                            # 加粗主标题
    hover_data=["description", "owner"],          # 额外悬停信息
    custom_data=["html_url"],                     # ★ 把 URL 挂到柱子上
    color="owner",                                # 按作者分组上色
    color_discrete_map={"vinta": "seagreen", "django": "green",
                        "pallets": "darkorange"},  # 固定配色，风格稳定
    text_auto=".2s",                                # 柱子上标数值（219k 这种）
    title="Most-Starred Python Repositories",
)
fig.update_traces(
    marker_line_width=1.5, marker_line_color="gray",    # 柱子描边
    opacity=0.9,
    hovertemplate="<b>%{hovertext}</b><br>Stars: %{y:,}<br>"
                   "<a href='%{customdata[0]}'>Open in GitHub</a><extra></extra>",
)
fig.update_layout(
    title={"text": "Most-Starred Python Repositories", "x": 0.5, "xanchor": "center",
           "font": {"size": 20}},
    xaxis_title=None, yaxis_title="Stars")
fig.write_html("bar_chart.html")
print("已生成 bar_chart.html —— 悬停柱子，点 Open in GitHub 试试")

for trace in fig.data:      # 验证 customdata 到底装了什么
    print("柱子", list(trace.x), "的 customdata:", [list(r) for r in trace.customdata])
