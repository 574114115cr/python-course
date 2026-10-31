# api_basics.py —— 先看清网址结构，再发一个真实请求（离线有兜底）
import requests

GITHUB_SEARCH = "https://api.github.com/search/repositories?q=language:python&sort=stars"
print("--- 网址里的参数 ---")
for pair in GITHUB_SEARCH.split("?", 1)[1].split("&"):
    key, _, value = pair.partition("=")
    print(f"  {key:10} = {value}")

# ===== 发一个真实请求；离线兜底数据结构和真实响应一致 =====
FALLBACK = {"total_count": 4350000, "incomplete_results": False,
            "items": [{"name": "awesome-python", "stargazers_count": 220000,
                       "owner": {"login": "vinta"}, "description": "A list",
                       "html_url": "https://github.com/vinta/awesome-python"}]}

try:
    response = requests.get(GITHUB_SEARCH + "&per_page=3",
                            headers={"Accept": "application/vnd.github+json"},
                            timeout=10)
except requests.exceptions.RequestException as error:
    print("网络请求失败：", error)
    response_dict = FALLBACK
else:
    print("状态码：", response.status_code,
          "剩余配额：", response.headers.get("X-RateLimit-Remaining", "不适用"))
    if response.status_code != 200:
        print("响应片段：", response.text[:200])      # 失败也要打印，别静默跳过
        response_dict = FALLBACK
    else:
        response_dict = response.json()

print("\ntotal_count:", response_dict["total_count"],
      "本次返回 items:", len(response_dict["items"]))
print("items[0] 的键:", list(response_dict["items"][0].keys()))
