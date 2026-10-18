# Python 学习课程 · 安卓壳（Capacitor）

把现有静态课程站打包成安卓 APK。**内容零迁移**：`tools/build_android_www.py` 把
「3 个入口页 + web/」组装成 Capacitor 的 `webDir`，课节页 / 题库 / 关卡 / 课件播放器
全部原样进 App，离线可用，学习进度存在本机 localStorage。

## 目录

```
android/
  package.json          Capacitor 8 依赖（core/cli/android/app 同版本）
  capacitor.config.json appId=cn.pylearn.course，webDir=www
  assets/               图标/启动屏源图（build_app_assets.py 生成）
  www/                  生成物：webDir（build_android_www.py 组装，勿手改）
  android/              生成物：原生工程（CI 里 npx cap add android 现生成）
```

构建链：`build_app_assets.py`（图标源图）→ `build_android_www.py`（webDir）
→ `cap add android` → `cap sync` → `assets generate` → `gradlew assembleDebug`。

## 云构建（默认方式，本机零安装）

1. 仓库推到 GitHub（`git init` → commit → push，`.gitignore` 已配好）。
2. push 触及 `web/**` / 入口页 / `android/**` 等路径时，`.github/workflows/android.yml`
   自动跑构建；也可在 Actions 页手动 `workflow_dispatch`。
3. 构建完在当次 run 的 Artifacts 里下载 `python-course-debug-apk`
   （`app-debug.apk`，约 20–22MB），传到手机安装即可（需允许「未知来源」）。

环境由 CI 提供：Node 22 + JDK 21（temurin）+ ubuntu-latest 自带 Android SDK。
私有仓库每月有免费额度（以 GitHub 当时政策为准）。

## 本地构建（可选，需要自装环境）

需要 JDK 21 + Android SDK（cmdline-tools，platform 36），约 3–5GB：

```bash
python tools/build_app_assets.py     # 图标/启动屏源图
python tools/build_android_www.py    # 组装 android/www
cd android
npm install
npx cap add android                  # 仅首次；报已存在就 rm -rf android/android
npx cap sync android
npx @capacitor/assets generate --android
cd android && ./gradlew assembleDebug --no-daemon
# 产物：android/app/build/outputs/apk/debug/app-debug.apk
```

Windows 本地把 `./gradlew` 换成 `gradlew.bat`。两个 python 脚本请用项目惯用的 venv
解释器跑（见仓库根 MEMORY.md），不要用全局 python。

## 原生行为约定

| 行为 | 实现 |
|---|---|
| 返回键 | `@capacitor/app` 的 `backButton` 事件：能后退就 `history.back()`，不能退就 `exitApp()`（见下方「注入的脚本」） |
| 状态栏 | Capacitor 8 边缘到边布局，`app-chrome.css` 用 `--safe-area-inset-top` 把 sticky 顶栏往下推 |
| 进度存储 | WebView localStorage（origin 为 `https://localhost`），与浏览器 PWA 的各存各的，卸载 App 即丢失 |
| pptx 直链 | `build_android_www.py` 已改写为 HTML 播放器（App 内打不开 pptx） |

## App 注入了什么（`build_android_www.py` 的三件事）

1. **复制静态资源**：3 个入口页 + `web/` 全量；不带 `course/`、`exercises/`、
   `python-course-ppt/`（App 用不到，省约 4MB）。
2. **改写 pptx 直链**：`index.html` 里的大纲 pptx 下载链改为 HTML 播放器
   （App 内打不开 pptx；播放器内容与 pptx 一致）。
3. **每页注入两个文件**（相对路径按目录深度算）：
   - `app-chrome.css`：Capacitor 8 边缘到边布局下，用 `--safe-area-inset-top`
     把 sticky 顶栏（`.top`/`.nav`/`.pbar`）往下推，避开状态栏。
   - `app-native.js`：硬件返回键监听（`Capacitor.Plugins.App` 全局 API，
     无需打包器）。能后退就 `history.back()`，无路可退才 `exitApp()`。
     浏览器里没有原生桥，脚本自动跳过。

浏览器 PWA 用的 `sw.js`/`manifest.webmanifest` 也会进包，但 WebView 不支持
Service Worker，注册自动失败，无副作用。

## 更新内容后

改了课程内容（course/ 或 web/）→ 重跑站点构建链 → push → Actions 自动出新 APK。
SW 缓存版本（`sw.js` 的 `V`）只在浏览器 PWA 里有意义，App 不走 SW。

## 发版（不上架，仅侧载）

debug 包即可日常用。若要正式签名包：自备 keystore，在 `android/android` 里
`./gradlew assembleRelease` 并按 Gradle 签名配置接入；不要把 keystore 密码提交进仓库。
