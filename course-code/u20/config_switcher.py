# config_switcher.py —— 演示「同一份代码，在本地和云上行为不同」

def build_settings(env):
    """根据环境变量决定配置。

    这就是 settings.py 双环境切换的核心思想：代码只有一份，
    行为由环境决定。platformshconfig 的 is_valid_platform()
    底层就是在查 PLATFORM_APPLICATION 这个变量。
    """
    on_platform = env.get("PLATFORM_APPLICATION") == "1"
    return {
        "DEBUG": False if on_platform else True,
        "数据库引擎": "postgresql" if on_platform else "sqlite3",
        "ALLOWED_HOSTS": [".platformsh.site"] if on_platform else ["localhost"],
        "SECRET_KEY 来源": "projectEntropy" if on_platform else "写死在 settings.py",
    }


def show(title, env):
    print(f"--- {title} ---")
    for key, value in build_settings(env).items():
        print(f"  {key} = {value}")
    print()


if __name__ == "__main__":
    show("本地开发（没有 PLATFORM_APPLICATION）", {})
    show("Platform.sh 云上（PLATFORM_APPLICATION=1）", {"PLATFORM_APPLICATION": "1"})
