# env_switch.py —— 不装 platformshconfig，纯 os.environ 模拟双环境配置
import os

def build_settings():
    """模拟 settings.py：同一份逻辑，两套配置。

    platformshconfig 的 is_valid_platform() 底层就是在查
    PLATFORM_APPLICATION：Platform.sh 运行应用时一定会注入它，
    本地没有——所以「变量存在与否」就是「我在哪」的判据。
    """
    on_platform = os.environ.get("PLATFORM_APPLICATION") == "1"
    return {
        "DEBUG": not on_platform,
        "数据库": "PostgreSQL（credentials('database')）" if on_platform else "SQLite（db.sqlite3）",
        "ALLOWED_HOSTS": ["localhost", ".platformsh.site"] if on_platform else ["localhost"],
        "STATIC_ROOT": "/app/static" if on_platform else None,
        "SECRET_KEY": "config.projectEntropy" if on_platform else "settings.py 里的字符串",
        "错误页面": "定制 404/500" if on_platform else "Django 调试页（DEBUG=True）",
    }


if __name__ == "__main__":
    label = "Platform.sh 云环境" if os.environ.get("PLATFORM_APPLICATION") else "本地开发"
    print(f"=== 当前环境：{label} ===")
    for key, value in build_settings().items():
        print(f"  {key:<14} = {value}")
