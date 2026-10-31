# settings_json.py —— 用 JSON 做配置文件

import json
import os

FILENAME = "settings.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_size": 14,
    "autosave": True,
    "languages": ["python", "english"],
}


def load_settings(filename=FILENAME):
    """读取配置文件，不存在时返回默认配置。"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  {filename} 不存在，返回默认配置")
        return DEFAULT_SETTINGS.copy()
    except json.JSONDecodeError:
        print(f"  {filename} 内容不是合法 JSON，返回默认配置")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings, filename=FILENAME):
    """保存配置到文件。"""
    with open(filename, "w", encoding="utf-8") as f:
        # ensure_ascii=False 保证中文可读，indent=2 让人也能看
        json.dump(settings, f, ensure_ascii=False, indent=2)
    print(f"  已保存到 {filename}")


# ===== 主流程 =====
print("=== 1. 首次读取（文件不存在）===")
settings = load_settings()
print(f"  读取结果：{settings}")

print("\n=== 2. 修改并保存 ===")
settings["font_size"] = 16                    # 修改字号
settings["languages"].append("japanese")     # 往列表里追加语言
settings["last_modified"] = "2026-10-14"      # 新增一个键
save_settings(settings)

print("\n=== 3. 文件里的实际内容 ===")
with open(FILENAME, "r", encoding="utf-8") as f:
    print(f.read())

print("=== 4. 重新读取，验证修改已保存 ===")
settings2 = load_settings()
print(f"  font_size = {settings2['font_size']}")           # 16  修改生效了
print(f"  languages = {settings2['languages']}")            # 包含新加的 japanese
print(f"  last_modified = {settings2['last_modified']}")   # 新键也保存了

# ===== 两个必须记住的参数 =====
print("\n=== 为什么必须加这两个参数 ===")
demo = {"名称": "测试", "值": 1}
print("  不加 ensure_ascii=False：", json.dumps(demo))
print("  加了 ensure_ascii=False：", json.dumps(demo, ensure_ascii=False))
print("  => 不加的话中文变成 \\uXXXX，既不可读也占更多空间")
print()
print("  不加 indent：", json.dumps(demo, ensure_ascii=False))
print("  加了 indent=2：")
print(json.dumps(demo, ensure_ascii=False, indent=2))
print("  => indent 让文件内容人也能看懂，方便手动检查和修改")

if os.path.exists(FILENAME):
    os.remove(FILENAME)
