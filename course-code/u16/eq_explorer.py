# eq_explorer.py —— 地震数据探索

import random

random.seed(16)

# ===== 1. 生成 10 条模拟地震（结构和 USGS GeoJSON 一致）=====
# 地震带中心（经度, 纬度）：夏威夷、日本、秘鲁、阿拉斯加、巴新
BELTS = [(-156.5, 19.3), (142.8, 37.5), (-74.3, -14.6), (-176.7, 51.8), (147.0, -6.0)]

features = []
for i in range(1, 11):
    lon0, lat0 = random.choice(BELTS)
    mag = round(random.uniform(0.5, 5.5), 1)
    features.append({
        "type": "Feature",
        "properties": {"mag": mag, "title": f"M {mag} - simulated quake #{i}"},
        "geometry": {"type": "Point",
                     "coordinates": [round(lon0 + random.uniform(-4, 4), 2),
                                     round(lat0 + random.uniform(-4, 4), 2),
                                     round(random.uniform(5, 30), 1)]},
        "id": f"sim{i}",
    })

# 真实项目里是：all_eq_dicts = json.loads(path.read_text())["features"]
all_eq_dicts = features

# ===== 2. 提取数据 =====
quakes = []
for eq_dict in all_eq_dicts:
    quakes.append({
        "mag": eq_dict["properties"]["mag"],
        "title": eq_dict["properties"]["title"],
        "lon": eq_dict["geometry"]["coordinates"][0],
        "lat": eq_dict["geometry"]["coordinates"][1],
    })

# ===== 3. 震级最大的 3 次 =====
print("--- 震级最大的 3 次地震 ---")
top3 = sorted(quakes, key=lambda q: q["mag"], reverse=True)[:3]
for i, quake in enumerate(top3, 1):
    print(f"{i}. {quake['title']} (M {quake['mag']})")

# ===== 4. 按震级分组统计 =====
below_1 = len([q for q in quakes if q["mag"] < 1.0])
mid = len([q for q in quakes if 1.0 <= q["mag"] < 3.0])
above_3 = len([q for q in quakes if q["mag"] >= 3.0])
print(f"\nM1 以下: {below_1} 次")
print(f"M1（含）~M3: {mid} 次")
print(f"M3（含）以上: {above_3} 次")
print(f"合计: {below_1 + mid + above_3} 次")

# ===== 5. 坐标自检 =====
print("\n--- 坐标自检 ---")
for quake in quakes:
    lon, lat = quake["lon"], quake["lat"]
    if -180 <= lon <= 180 and -90 <= lat <= 90:
        status = "合法"
    else:
        status = "坐标可疑！"
    print(f"{quake['title']}: lon={lon}, lat={lat}  {status}")
