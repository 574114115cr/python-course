# api_watchtower.py —— 状态码观测台
import requests

ACCEPT = {"Accept": "application/vnd.github+json"}
URLS = [("GitHub 搜索", "https://api.github.com/search/repositories?q=language:python&sort=stars", ACCEPT),
        ("不存在的路径", "https://api.github.com/not-a-real-endpoint-xyz", ACCEPT),
        ("HN 列表", "https://hacker-news.firebaseio.com/v0/topstories.json", None)]
DIAGNOSIS = {200: "成功，可以放心调 response.json()",
             403: "被拒绝：多半是速率限制超了，或需要认证",
             404: "网址或资源 ID 写错了",
             429: "请求太多被限流，等一会儿再来",
             500: "服务器内部错误，隔一会儿重试",
             -1: "网络没通：断网或超时"}


def probe(url, headers=None):
    """返回 (状态码, 剩余配额, 响应前 100 字)。网络异常返回 (-1, None, 原因)。"""
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
    except requests.exceptions.RequestException as error:
        return -1, None, f"{type(error).__name__}: {error}"
    return (response.status_code, response.headers.get("X-RateLimit-Remaining"),
            response.text[:100])


for label, url, headers in URLS:
    code, remaining, snippet = probe(url, headers)
    print(f"\n[{label}] 状态码={code} 剩余配额={remaining}")
    print("  诊断：", DIAGNOSIS.get(code, f"没见过的状态码 {code}"))
    print("  片段：", snippet.replace("\n", " ")[:100])

print("\n说明：未认证每小时 60 次；配额看响应头 X-RateLimit-Remaining。")
