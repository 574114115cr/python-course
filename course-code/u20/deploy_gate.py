# deploy_gate.py —— 上线前 8 道闸门 + 静态文件清单，全用标准库
import os
import re
from pathlib import Path

ROOT = Path("data/ll_project")


def make_demo_project(root=ROOT):
    """造一个「差两项」的假项目，这样能同时看到 ✓ 和 ✗。"""
    files = {
        "requirements.txt": "asgiref==3.7.2\nDjango==4.2.10\ndjango-bootstrap5==23.4\n",
        "requirements_remote.txt": "# 线上专用\ngunicorn==21.2.0\npsycopg2==2.9.9\n",
        ".platform.app.yaml": 'name: "ll_project"\nrelationships:\n    database: "db:postgresql"\n'
                              'hooks:\n    build: python manage.py collectstatic --noinput\n',
        ".platform/routes.yaml": '"https://{default}/":\n    upstream: "ll_project:http"\n',
        ".platform/services.yaml": "db:\n    type: postgresql:16\n",
        ".gitignore": "ll_env/\n__pycache__/\n*.sqlite3\n",
        "ll_project/settings.py": "ALLOWED_HOSTS = ['localhost', '.platformsh.site']\n"
                                  "DEBUG = False\n",
        "learning_logs/static/css/styles.css": ".jumbotron { padding: 2rem; }\n",
        "accounts/static/css/login.css": ".form-label { font-weight: bold; }\n",
        "templates/404.html": "404\n",
        # ★ 故意不写 templates/500.html，看第 7 项能不能抓出来
    }
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def unpinned(text):
    return [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.startswith("#") and "==" not in ln]


def checks(root=ROOT, env=None):
    """八道闸门，每项返回 (是否通过, 说明)。顺序就是踩坑频率的顺序。"""
    env = os.environ if env is None else env
    app_yaml = read(root / ".platform.app.yaml")
    routes = read(root / ".platform/routes.yaml")
    services = read(root / ".platform/services.yaml")
    settings = read(root / "ll_project/settings.py")
    gitignore = read(root / ".gitignore")
    app_name = re.search(r'name:\s*"([^"]+)"', app_yaml)
    upstream = re.search(r'upstream:\s*"([^":]+)', routes)
    return [
        ("依赖清单锁版本", not unpinned(read(root / "requirements.txt"))
         and (root / "requirements.txt").exists()),
        ("线上依赖齐全", all(pkg in read(root / "requirements_remote.txt")
                            for pkg in ("gunicorn", "psycopg2"))),
        ("路由暗号对齐", bool(app_name and upstream)
         and app_name.group(1) == upstream.group(1)),
        ("数据库服务存在", "postgresql" in services and "db:" in services),
        ("忽略清单到位", "*.sqlite3" in gitignore and "ll_env/" in gitignore),
        ("云上放行域名且关调试", ".platformsh.site" in settings and "DEBUG = False" in settings),
        ("错误页成对", (root / "templates/404.html").exists()
         and (root / "templates/500.html").exists()),
        ("静态文件已收集", "collectstatic" in app_yaml),
    ]


def static_inventory(root=ROOT):
    """pathlib 遍历：collectstatic 到底会把哪些文件搬到 STATIC_ROOT。"""
    found = []
    for app_dir in sorted(root.iterdir()):
        static = app_dir / "static"
        if static.is_dir():
            for file in sorted(static.rglob("*")):
                if file.is_file():
                    found.append(str(file.relative_to(root)).replace("\\", "/"))
    return found


def allowed_hosts_from_env(env):
    """ALLOWED_HOSTS 不该写死：线上域名从环境变量来，本地给默认值。"""
    raw = env.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
    return [host.strip() for host in raw.split(",") if host.strip()]


make_demo_project()
results = checks()
print("=== 部署前自查（8 项）===")
for index, (label, ok) in enumerate(results, 1):
    print(f"  [{index}] [{'✓' if ok else '✗'}] {label}")
failed = [label for label, ok in results if not ok]
passed = len(results) - len(failed)
if failed:
    print(f"\n通过 {passed}/{len(results)} 项；未通过：{'、'.join(failed)}")
else:
    print(f"\n通过 {passed}/{len(results)} 项，可以 platform push。")

print("\n=== 静态文件清单（collectstatic 的搬运目标）===")
for rel in static_inventory():
    print("  ", rel)
print(f"  共 {len(static_inventory())} 个文件 -> STATIC_ROOT")

print("\n=== ALLOWED_HOSTS 从环境变量来，不写死 ===")
print("  本地：", allowed_hosts_from_env({}))
print("  线上：", allowed_hosts_from_env(
    {"DJANGO_ALLOWED_HOSTS": "learning-log-abc.us-3.platformsh.site,.platformsh.site"}))

import shutil
shutil.rmtree("data", ignore_errors=True)      # 演示完删掉
