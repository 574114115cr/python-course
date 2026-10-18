# -*- coding: utf-8 -*-
"""组装 Capacitor 的 webDir（android/www）。

站点本身是纯静态包，安卓壳直接复用：
  1. 复制 3 个根入口页 + 整个 web/（课件/题库/关卡/搜索索引全在里面）
  2. index.html 的 pptx 直链改成 HTML 播放器（App 内打不开 pptx）
  3. 每个 HTML 注入 app-chrome.css（Capacitor 8 边缘到边缘，避开状态栏）
  4. 不带 course/ exercises/ python-course-ppt/（App 用不到，省 4MB）

产出：android/www/（约 20MB）。cap sync 前必须先生成。

运行：venv python tools/build_android_www.py
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID = os.path.join(ROOT, "android")
WWW = os.path.join(ANDROID, "www")

ENTRY_PAGES = ["index.html", "python-course-syllabus.html",
               "python-learning-roadmap.html"]

# PWA 附属文件一并进包：页面里有 manifest 链接，缺文件会在 App 内 404
# （WebView 不支持 Service Worker，sw.js 注册会静默失败，带上只为免 404）
PWA_FILES = ["manifest.webmanifest", "sw.js",
             "icon-192.png", "icon-512.png",
             "icon-maskable-192.png", "icon-maskable-512.png"]

# pptx 直链 → App 内改用 HTML 播放器
PPTX_RE = re.compile(r'href="python-course-ppt/[^"]*\.pptx"')
PPTX_TO = 'href="web/ppt/index.html"'

# 课件页的「下载 .pptx」按钮：webDir 里没有 python-course-ppt/，
# App 内点了必然 404，且 Capacitor WebView 没有 DownloadListener，
# 塞 pptx 进包也存不下来 → 换成禁用态提示，引导去网页版/便携版
PPTX_BTN_RE = re.compile(
    r'<a class="btn primary" href="[^"]*\.pptx" download>下载 \.pptx</a>')
PPTX_BTN_TO = ('<span class="btn" style="opacity:.55;cursor:default" '
               'title=".pptx 文件请在网页版或便携版课程包中下载">'
               '.pptx 仅网页版提供</span>')

# Capacitor 8 注入 --safe-area-inset-top；边缘到边布局下 sticky 顶栏会被状态栏压住
APP_CSS = """/* 安卓壳专用（仅随 App 分发，不影响桌面站点）：
   Capacitor 8 边缘到边布局，sticky 顶栏让出状态栏高度 */
.top{padding-top:var(--safe-area-inset-top,env(safe-area-inset-top,0px))}
.nav{padding-top:var(--safe-area-inset-top,env(safe-area-inset-top,0px))}
.pbar{top:calc(58px + var(--safe-area-inset-top,env(safe-area-inset-top,0px)))}
"""

# 硬件返回键 → 历史后退；无路可退再退出。浏览器里无原生桥，自动跳过
APP_JS = """/* 安卓壳专用（仅随 App 分发）：硬件返回键走 WebView 历史栈 */
(function () {
  var P = window.Capacitor && window.Capacitor.Plugins;
  if (!P || !P.App || !P.App.addListener) return;
  P.App.addListener('backButton', function (e) {
    if (e && e.canGoBack) { window.history.back(); }
    else if (P.App.exitApp) { P.App.exitApp(); }
  });
})();
"""


def inject(path):
    """注入 app-chrome.css（</head> 前）与 app-native.js（</body> 前）。
    相对路径按文件所在目录深度算（relpath 的目标必须是绝对路径，
    写相对名会相对 CWD 解析，层级全错）。"""
    base = os.path.dirname(path)
    rel_css = os.path.relpath(os.path.join(WWW, "app-chrome.css"), base).replace("\\", "/")
    rel_js = os.path.relpath(os.path.join(WWW, "app-native.js"), base).replace("\\", "/")
    s = open(path, encoding="utf-8").read()
    if "app-chrome.css" in s:
        return False
    if "</head>" not in s:
        return False
    s = s.replace("</head>", f'<link rel="stylesheet" href="{rel_css}">\n</head>', 1)
    if "</body>" in s:
        s = s.replace("</body>", f'<script src="{rel_js}" defer></script>\n</body>', 1)
    open(path, "w", encoding="utf-8").write(s)
    return True


def main():
    if os.path.isdir(WWW):
        shutil.rmtree(WWW)
    os.makedirs(WWW)

    n_html = 0
    # 1) 根入口页 + PWA 附属文件
    for f in ENTRY_PAGES + PWA_FILES:
        src = os.path.join(ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(WWW, f))
            if f.endswith(".html"):
                n_html += 1
    # 2) web/ 整棵树（课件 webp 10MB 是大头，但离线必需）
    shutil.copytree(os.path.join(ROOT, "web"), os.path.join(WWW, "web"))
    for cur, _dirs, files in os.walk(os.path.join(WWW, "web")):
        n_html += sum(1 for f in files if f.endswith(".html"))

    # 3) pptx 直链改写
    idx = os.path.join(WWW, "index.html")
    s = open(idx, encoding="utf-8").read()
    s2 = PPTX_RE.sub(PPTX_TO, s)
    open(idx, "w", encoding="utf-8").write(s2)
    n_pptx = len(PPTX_RE.findall(s))

    # 3b) 课件页「下载 .pptx」按钮中性化（App 内没有 pptx 文件可下）
    n_btn = 0
    ppt_pages = [os.path.join(WWW, "web", "ppt", "index.html")]
    u_dir = os.path.join(WWW, "web", "ppt", "u")
    if os.path.isdir(u_dir):
        ppt_pages += [os.path.join(u_dir, f) for f in sorted(os.listdir(u_dir))
                      if f.endswith(".html")]
    for p in ppt_pages:
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        s2, k = PPTX_BTN_RE.subn(PPTX_BTN_TO, s)
        if k:
            open(p, "w", encoding="utf-8").write(s2)
            n_btn += k

    # 4) app-chrome.css / app-native.js + 逐页注入
    with open(os.path.join(WWW, "app-chrome.css"), "w", encoding="utf-8") as fh:
        fh.write(APP_CSS)
    with open(os.path.join(WWW, "app-native.js"), "w", encoding="utf-8") as fh:
        fh.write(APP_JS)
    injected = 0
    for cur, _dirs, files in os.walk(WWW):
        for f in files:
            if f.endswith(".html"):
                if inject(os.path.join(cur, f)):
                    injected += 1

    total = sum(
        os.path.getsize(os.path.join(cur, f))
        for cur, _d, fs in os.walk(WWW) for f in fs)
    print(f"webDir 就绪：{WWW}")
    print(f"  HTML {n_html} 页（注入 app-chrome.css + app-native.js {injected} 页）")
    print(f"  pptx 直链改写 {n_pptx} 处；下载按钮中性化 {n_btn} 处")
    print(f"  总体积 {total / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
