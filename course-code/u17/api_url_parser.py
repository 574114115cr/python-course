# api_url_parser.py —— 拆解网址 + 解剖响应字典（不发网络请求）
import requests

GITHUB_SEARCH = "https://api.github.com/search/repositories?q=language:python&sort=stars"


def split_query(url):
    """返回 (路径, {参数名: 参数值})；没有问号时参数为空字典。"""
    if "?" not in url:
        return url, {}
    path, _, query = url.partition("?")
    params = {}
    for pair in query.split("&"):
        key, _, value = pair.partition("=")
        params[key] = value
    return path, params


path, params = split_query(GITHUB_SEARCH)
print("路径：", path, "| 参数：", params)   # q = 语言条件，sort = 按 star 排序
print("用 params 拼网址：",
      requests.Request("GET", "https://api.github.com/search/repositories",
                       params=params | {"per_page": 5}).prepare().url)

# ===== 响应字典解剖（离线）=====
# 故意造两种脏数据：免费游戏那个 description 为 None，flask 缺 forks_count
RAW = [("awesome-python", 220000, "vinta", "A curated list", 23000),
       ("free-python-games", 95000, "tasnowak", None, 7000),
       ("django", 78000, "django", "Web framework", 31000),
       ("flask", 67000, "pallets", "Micro framework", None)]
items = [{"name": n, "stargazers_count": s, "owner": {"login": o},
          "html_url": f"https://github.com/{o}/{n}", "description": d,
          **({"forks_count": f} if f is not None else {})} for n, s, o, d, f in RAW]
print("\ntotal_count：4200000（总命中数，不是返回条数）")

names, stars, logins, descs, forks, urls = [], [], [], [], [], []
for r in items:
    names.append(r["name"])
    stars.append(r["stargazers_count"])
    urls.append(r["html_url"])
    logins.append(r["owner"]["login"])
    descs.append(r["description"] or "（作者很懒，没写简介）")
    forks.append(r.get("forks_count", 0))           # 字段可能不存在

for row in zip(names, stars, logins, forks, descs):
    print(f"{row[0]:<18}{row[1]:>9,}  by {row[2]:<10}fork={row[3]:>7,}  {row[4]}")
for rank, i in enumerate(sorted(range(len(stars)),
                                key=lambda i: stars[i], reverse=True), 1):
    print(f"{rank}. {names[i]:<18}{stars[i]:>9,}  {urls[i]}")

assert len(names) == len(stars) == len(logins) == len(descs) == len(forks) == len(urls)
print("\n六个列表等长：True；没有 None：", all(d is not None for d in descs))
