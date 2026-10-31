# api_pipeline.py —— 请求 → JSON → 取字段：全部拆成纯函数，离线也能测
import time

# ===== 一份"假 payload"，结构和 GitHub search API 的响应一模一样 =====
PAYLOAD_PAGE_1 = {
    "total_count": 4350000,
    "incomplete_results": False,
    "items": [
        {"name": "awesome-python", "stargazers_count": 220000,
         "html_url": "https://github.com/vinta/awesome-python",
         "description": "A curated list", "owner": {"login": "vinta"}},
        {"name": "free-python-games", "stargazers_count": 95000,
         "html_url": "https://github.com/tasnowak/free-python-games",
         "description": None, "owner": {"login": "tasnowak"}},
    ],
}
PAYLOAD_PAGE_2 = {
    "total_count": 4350000,
    "items": [
        {"name": "django", "stargazers_count": 78000,
         "html_url": "https://github.com/django/django",
         "description": "Web framework", "owner": {"login": "django"}},
        {"name": "awesome-python", "stargazers_count": 220000,   # ★ 跨页重复
         "html_url": "https://github.com/vinta/awesome-python",
         "description": "A curated list", "owner": {"login": "vinta"}},
    ],
}


def parse_items(payload):
    """★ 纯函数：输入一个 payload，输出五个平行列表。不碰网络、不碰文件。"""
    names, stars, urls, owners, descs = [], [], [], [], []
    for item in payload.get("items", []):
        names.append(item["name"])                       # 核心结构，缺了就报错
        stars.append(item.get("stargazers_count", 0))    # 可选字段用 .get
        urls.append(item.get("html_url", ""))
        owners.append(item.get("owner", {}).get("login", "未知"))
        descs.append(item.get("description") or "（没写简介）")
    return names, stars, urls, owners, descs


names, stars, urls, owners, descs = parse_items(PAYLOAD_PAGE_1)
print("=== 第一页解析结果 ===")
for row in zip(names, stars, owners, descs):
    print(f"  {row[0]:<18}{row[1]:>8,}  by {row[2]:<10}{row[3]}")

print("\n=== 分页循环：一个函数取多页，按名字去重 ===")


def collect(get_json, pages=2, per_page=2, pause=0.0):
    """参数是「取一页的函数」，所以换成假数据也能测。"""
    seen, merged = set(), []
    for page in range(1, pages + 1):
        if pause:
            time.sleep(pause)                            # 真项目里写 pause=1
        payload = get_json(page, per_page)
        if payload is None:
            print(f"  第 {page} 页失败，跳过")
            continue
        page_items = payload.get("items", [])
        for item in page_items:
            if item["name"] in seen:                     # ★ 跨页重复很常见
                print(f"  第 {page} 页发现重复：{item['name']}，丢弃")
                continue
            seen.add(item["name"])
            merged.append(item)
        print(f"  第 {page} 页：返回 {len(page_items)} 条，累计 {len(merged)} 条")
    return merged


FAKE_PAGES = {1: PAYLOAD_PAGE_1, 2: PAYLOAD_PAGE_2}


def fake_get_json(page, per_page):
    return FAKE_PAGES.get(page)


merged = collect(fake_get_json)
n, s, u, o, d = parse_items({"items": merged})
for name, star in sorted(zip(n, s), key=lambda pair: pair[1], reverse=True):
    print(f"  {name:<18}{star:>8,}")

print("\n=== 失败重试：同一个请求最多试 3 次 ===")


def get_json_with_retry(fetch, attempts=3):
    """fetch() 返回 None 表示失败；成功就立刻返回，别做无意义的等待。"""
    for attempt in range(1, attempts + 1):
        payload = fetch()
        if payload is not None:
            print(f"  第 {attempt} 次成功")
            return payload
        print(f"  第 {attempt} 次失败，{'重试' if attempt < attempts else '放弃'}")
    return None


calls = {"n": 0}


def flaky():
    """前两次装死，第三次才成功——模拟网络抖动。"""
    calls["n"] += 1
    return PAYLOAD_PAGE_2 if calls["n"] >= 3 else None


result = get_json_with_retry(flaky)
print("  最终拿到：", [item["name"] for item in result["items"]])
print("  说明：403 不要重试（配额已空，重试只会更糟），网络异常才重试。")
