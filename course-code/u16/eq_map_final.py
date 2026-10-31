# eq_map_final.py —— 可交互地震地图

import random

import plotly.express as px

random.seed(66)

# ===== 1. 生成 20 条模拟地震 =====
BELTS = [(-156.5, 19.3), (142.8, 37.5), (-74.3, -14.6), (-176.7, 51.8),
         (147.0, -6.0), (-118.2, 34.1)]

mags, lons, lats, eq_titles = [], [], [], []
for i in range(1, 21):
    lon0, lat0 = random.choice(BELTS)
    mag = round(random.uniform(1.0, 5.5), 1)
    mags.append(mag)
    lons.append(round(lon0 + random.uniform(-5, 5), 2))    # 经度
    lats.append(round(lat0 + random.uniform(-5, 5), 2))    # 纬度
    eq_titles.append(f"M {mag} - simulated quake #{i}")

# 真实项目里这三个列表从 geojson 文件提取：
# all_eq_dicts = json.loads(path.read_text(encoding="utf-8"))["features"]

# ===== 2. 画图 =====
fig = px.scatter_geo(
    lat=lats, lon=lons, size=mags,
    color=mags,
    color_continuous_scale="Inferno",     # 试试换成 "Blues" 对比效果
    labels={"color": "Magnitude"},
    projection="natural earth",
    hover_name=eq_titles,
)

fig.update_layout(title="Recent Global Earthquakes (M1+)")

fig.write_html("我的地震图.html")
print("已生成 我的地震图.html，浏览器打开后把鼠标悬停在点上看看")
