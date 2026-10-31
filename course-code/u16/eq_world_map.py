# eq_world_map.py —— plotly 散点地图

import json
import random
from pathlib import Path

import plotly.express as px

random.seed(16)

# ===== 1. 生成 12 条模拟地震（结构和 USGS GeoJSON 一致）=====
# 真实项目里把这一步换成 path.read_text() 读下载的 geojson 文件
# 地震带中心（经度, 纬度）：夏威夷、日本、秘鲁、阿拉斯加、巴新
BELTS = [(-156.5, 19.3), (142.8, 37.5), (-74.3, -14.6), (-176.7, 51.8), (147.0, -6.0)]

features = []
for i in range(1, 13):
    lon0, lat0 = random.choice(BELTS)
    mag = round(random.uniform(1.0, 5.8), 1)
    features.append({
        "type": "Feature",
        "properties": {"mag": mag, "title": f"M {mag} - simulated quake #{i}"},
        "geometry": {"type": "Point",
                     "coordinates": [round(lon0 + random.uniform(-4, 4), 2),
                                     round(lat0 + random.uniform(-4, 4), 2),
                                     round(random.uniform(5, 60), 1)]},
        "id": f"sim{i}",
    })

eq_data = {"type": "FeatureCollection",
           "metadata": {"title": "Simulated M1+ Earthquakes, Past 30 Days", "count": 12},
           "features": features}

path = Path("eq_data_30_day_m1.geojson")
path.write_text(json.dumps(eq_data, ensure_ascii=False, indent=2), encoding="utf-8")

# ===== 2. 提取三个列表 =====
all_eq_dicts = json.loads(path.read_text(encoding="utf-8"))["features"]

mags, lons, lats, eq_titles = [], [], [], []
for eq_dict in all_eq_dicts:
    mags.append(eq_dict["properties"]["mag"])
    lons.append(eq_dict["geometry"]["coordinates"][0])   # 经度
    lats.append(eq_dict["geometry"]["coordinates"][1])   # 纬度
    eq_titles.append(eq_dict["properties"]["title"])

# ===== 3. 画图 =====
title = "Global Earthquakes"
fig = px.scatter_geo(
    lat=lats, lon=lons, size=mags, title=title,
    color=mags,
    color_continuous_scale="Viridis",
    labels={"color": "Magnitude"},
    projection="natural earth",
    hover_name=eq_titles,
)

fig.write_html("全球地震散点图.html")
print("已生成 全球地震散点图.html，用浏览器打开即可交互查看")

path.unlink()        # 清理
