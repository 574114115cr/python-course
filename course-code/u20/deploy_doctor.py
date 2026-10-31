# deploy_doctor.py —— 上线前跑一遍，把配置类问题一次性挑出来
def check_config(cfg, host, static_ready):
    """cfg 是 settings 里的关键项；返回 [(级别, 问题, 怎么改)]。"""
    issues = []
    if cfg.get("DEBUG"):
        issues.append(("严重", "DEBUG 还是 True，报错会连同密钥一起显示在页面上",
                       "线上改成 False"))
        # DEBUG=True 时 Django 自动放行 localhost / 127.0.0.1 / [::1]，
        # 所以本地怎么访问都不会 400——这个坑只有到了线上才暴露
        issues.append(("提示", "DEBUG=True 时 ALLOWED_HOSTS 被自动放行，本地试不出来",
                       "把 ALLOWED_HOSTS 的问题留到线上前单独确认"))
    elif not any(host == h or (h.startswith(".") and host.endswith(h[1:]))
                 for h in cfg.get("ALLOWED_HOSTS", [])):
        issues.append(("严重", f"ALLOWED_HOSTS 不含 {host}，访问会被 400 拦下",
                       f"ALLOWED_HOSTS.append('{host}')"))
    if not cfg.get("STATIC_ROOT"):
        issues.append(("警告", "没设 STATIC_ROOT，collectstatic 不知道往哪汇总",
                       "STATIC_ROOT = BASE_DIR / 'staticfiles'"))
    elif not static_ready:
        issues.append(("警告", "STATIC_ROOT 是空的，线上会变成没样式的白脸页面",
                       "python manage.py collectstatic --noinput"))
    if cfg.get("SECRET_KEY", "").startswith("django-insecure"):
        issues.append(("严重", "还在用开发用的 SECRET_KEY，会话和签名可被伪造",
                       "从环境变量读一个随机长字符串"))
    return issues


def report(issues):
    if not issues:
        print("配置体检通过：没发现致命项\n")
        return True
    for level, what, how in issues:
        print(f"[{level}] {what}\n      改法：{how}\n")
    return not any(lv == "严重" for lv, _, _ in issues)


# 三种典型现场
cases = [
    ("本地开发", {"DEBUG": True, "ALLOWED_HOSTS": [], "SECRET_KEY": "django-insecure-xxx"},
     "127.0.0.1:8000", False),
    ("刚推上线（忘了改配置）",
     {"DEBUG": True, "ALLOWED_HOSTS": [], "SECRET_KEY": "django-insecure-xxx"},
     "abc.us-3.platformsh.site", False),
    ("配置齐全", {"DEBUG": False, "ALLOWED_HOSTS": [".platformsh.site"],
                 "STATIC_ROOT": "/app/staticfiles", "SECRET_KEY": "a9f3...c21"},
     "abc.us-3.platformsh.site", True),
]
for name, cfg, host, ready in cases:
    print(f"── {name} ──")
    ok = report(check_config(cfg, host, ready))
    print(f"结论：{'可以上线' if ok else '先修完再上线'}\n")

print("★ 注意第二种：本地全绿，上线全红——差别只在于配置，不在代码。")
