# static_collector.py —— 用 30 行代码看懂 collectstatic 的核心动作
from pathlib import Path
import shutil


def collect_static(app_names, project_root, static_root):
    """模拟 python manage.py collectstatic：
    把每个应用的 static/ 目录，原样汇总到 STATIC_ROOT。
    """
    if static_root.exists():
        shutil.rmtree(static_root)
    static_root.mkdir(parents=True)
    copied = []
    for app_name in app_names:
        source = project_root / app_name / "static"
        if not source.exists():
            continue
        for file in sorted(source.rglob("*")):
            if file.is_file():
                dest = static_root / file.relative_to(source)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
                copied.append(dest)
    return copied


if __name__ == "__main__":
    root = Path("data/learning_log")
    # 造两个应用，各带自己的 static/ 目录
    (root / "learning_logs/static/css").mkdir(parents=True, exist_ok=True)
    (root / "accounts/static/css").mkdir(parents=True, exist_ok=True)
    (root / "learning_logs/static/css/styles.css").write_text(
        ".jumbotron { padding: 2rem; }", encoding="utf-8")
    (root / "accounts/static/css/login.css").write_text(
        ".form-label { font-weight: bold; }", encoding="utf-8")

    copied = collect_static(["learning_logs", "accounts"], root, root / "static")
    print(f"共收集 {len(copied)} 个静态文件到 STATIC_ROOT：")
    for path in copied:
        print("  static/" + str(path.relative_to(root / "static")).replace("\\", "/"))
    # 跑完可以删掉 data/ 目录
