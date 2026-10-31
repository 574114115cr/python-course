# deploy_checklist.py —— 部署前自查：文件是否齐全、关键内容是否到位
from pathlib import Path

# (相对路径, 说明)
REQUIRED_FILES = [
    ("requirements.txt", "依赖清单"),
    ("requirements_remote.txt", "线上依赖（gunicorn/psycopg2）"),
    (".platform.app.yaml", "应用配置"),
    (".platform/routes.yaml", "路由配置"),
    (".platform/services.yaml", "数据库服务"),
    (".gitignore", "Git 忽略清单"),
    ("manage.py", "Django 入口"),
]


def check_files(root):
    results = []
    for rel, desc in REQUIRED_FILES:
        results.append(("✓" if (root / rel).exists() else "✗", f"{desc}：{rel}"))
    return results


def check_contents(root):
    """检查「文件在、但内容不对」的情况——这类问题更隐蔽。"""
    results = []
    gitignore = root / ".gitignore"
    if gitignore.exists():
        text = gitignore.read_text(encoding="utf-8")
        if "sqlite3" not in text:
            results.append(("✗", ".gitignore 没忽略 *.sqlite3，本地数据库会被传上云"))
    settings = root / "ll_project/settings.py"
    if settings.exists():
        text = settings.read_text(encoding="utf-8")
        if "platformsh.site" not in text:
            results.append(("✗", "settings.py 没放行 .platformsh.site，线上会 400"))
        if "DEBUG = False" not in text:
            results.append(("✗", "settings.py 没在云上关闭 DEBUG"))
    else:
        results.append(("✗", "找不到 ll_project/settings.py"))
    return results


def report(results):
    failed = 0
    for mark, desc in results:
        print(f"  [{mark}] {desc}")
        if mark == "✗":
            failed += 1
    print()
    print(f"有 {failed} 项未通过，修好再 push！" if failed else "全部通过，可以 platform push。")


if __name__ == "__main__":
    root = Path("data/checklist_demo")
    # 造一个「假项目」：该有的都有，唯独忘了 .gitignore
    for rel, content in [
        ("requirements.txt", "Django==4.2.10\n"),
        ("requirements_remote.txt", "# Requirements for live project.\ngunicorn\npsycopg2\n"),
        (".platform.app.yaml", "name: ll_project\nhooks:\n  build: python manage.py collectstatic --noinput\n"),
        (".platform/routes.yaml", '"https://{default}/":\n  type: upstream\n  upstream: "ll_project:http"\n'),
        (".platform/services.yaml", "db:\n  type: postgresql:16\n"),
        ("manage.py", "# Django 入口\n"),
        ("ll_project/settings.py", "ALLOWED_HOSTS = ['localhost']\nDEBUG = True\n"),
    ]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    report(check_files(root) + check_contents(root))
    # 跑完可以删掉 data/ 目录
