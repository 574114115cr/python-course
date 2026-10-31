# parse_response.py —— 把响应字典变成 Plotly 需要的平行列表（完全离线）
RAW = [("awesome-python", 220000, "vinta", "A list of awesome-python"),
       ("free-python-games", 95000, "tasnowak", None),      # ★ 故意留空，测兜底
       ("django", 78000, "django", "The web framework")]
items = [{"name": n, "stargazers_count": s, "owner": {"login": o},
          "description": d, "html_url": f"https://github.com/{o}/{n}"}
         for n, s, o, d in RAW]

repo_names, stars, repo_urls, descriptions, owners = [], [], [], [], []
for repo_dict in items:
    repo_names.append(repo_dict["name"])
    stars.append(repo_dict["stargazers_count"])
    repo_urls.append(repo_dict["html_url"])
    descriptions.append(repo_dict["description"] or "（作者很懒，没写简介）")
    owners.append(repo_dict["owner"]["login"])

print("--- 提取结果 ---")
for name, star_count, owner in zip(repo_names, stars, owners):
    print(f"{name:<20}{star_count:>9,}  by {owner}")

# .get() 演示「字段可能不存在」
print("\nforks_count 用 .get 取默认值：", items[0].get("forks_count", 0))

# 按 star 从多到少排序；再断言五个列表等长，否则画图一定出错
for i in sorted(range(len(stars)), key=lambda i: stars[i], reverse=True):
    print(f"{repo_names[i]:<20}{stars[i]:>9,}")
assert len(repo_names) == len(stars) == len(repo_urls) == len(descriptions) == len(owners)
print("五个列表等长：True（共", len(repo_names), "条）")
