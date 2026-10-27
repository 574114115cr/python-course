# 单元 12：Pygame 起步与飞船驾驶

> 对应教材第 12 章「武装飞船」12.1–12.7 节
> 阶段 2 · 项目 1：外星人入侵（Pygame）
> 本单元目标：**用 Pygame 搭出一个真正的游戏窗口，并让飞船响应按键持续、平滑地移动**

---

## 一、学习目标

完成本单元后，你应该能够：

1. 说清「外星人入侵」为什么拆成 `alien_invasion.py` / `settings.py` / `ship.py` 三个文件，各自负责什么。
2. 独立写出 Pygame 的最小骨架：初始化、创建 800×600 窗口、填充背景色、响应用户关闭。
3. 讲明游戏主循环 `while True` 的四步职责，以及 `self.clock.tick(60)` 为什么能解决「不同电脑速度不同」的问题。
4. 用「前台接待」的类比解释事件驱动模型，区分 `pygame.event.get()`、事件队列、`KEYDOWN` 与 `QUIT`。
5. 创建 `Settings` 类，把会变的数值集中管理，并亲身体会一次「重构」是怎么回事。
6. 用布尔标志位实现飞船的持续移动，并用 `self.screen_rect` 把飞船限制在屏幕内。

---

## 二、核心知识点讲解

### 2.1 规划项目：为什么一个游戏要拆成三个文件

从这一单元开始，你要写第一个「大项目」：**外星人入侵**。敲第一行代码之前，教材先做了一步看起来很多余的事——**规划项目**。这不是仪式感，而是这个项目能写下去的关键。一个能玩的游戏至少包含四类东西：

```text
外星人入侵
├── 窗口和主循环      ← 谁来组织"一帧一帧"的节奏？
├── 一堆可调数值      ← 窗口多大？飞船多快？背景什么色？
├── 飞船              ← 位置、移动、绘制
└── （第 13 章还有）子弹、外星人、统计信息……
```

如果全塞进一个文件，写到 500 行时你会陷入「想改个速度要翻半天」的困境。所以教材把它拆成三份：

| 文件 | 角色 | 负责什么 | 类比 |
|---|---|---|---|
| `alien_invasion.py` | 主编 | 创建窗口、跑主循环、把活儿分派出去 | 餐厅店长：不亲自炒菜，但决定节奏 |
| `settings.py` | 设置簿 | 所有「以后可能会改」的数值 | 菜单：想换口味改菜单，不用换厨师 |
| `ship.py` | 船员 | 飞船这个对象的数据和行为 | 厨师：只关心自己这道菜 |

生活化类比：把游戏当成一家餐厅。店长（`alien_invasion.py`）招呼客人、决定什么时候上菜；菜单（`settings.py`）写着每道菜放多少盐——客人说太咸，你只改菜单，不用重新装修厨房；厨师（`ship.py`）只对自己的那道菜负责，换一个厨师，店照样开。

**这条分工原则是整个项目的地基**：主循环保持「薄」，逻辑下沉到各个类。第 13 章加入子弹和外星人时，只要新增 `bullet.py`、`alien.py`，主文件几乎不用动。

### 2.2 安装 Pygame 与一个重要的环境提醒

```bash
pip install pygame
```

- 教材用的是 `pygame`，装它就行。社区有个更新更勤的分支 `pygame-ce`，API 完全一致，任选其一。
- 验证安装：`python -c "import pygame; print(pygame.ver)"`，能打印版本号就没问题。

**环境提醒（重要，先看再跑代码）**：Pygame 要打开真正的操作系统窗口。在服务器、SSH 或某些虚拟环境里可能没有「显示设备」，直接运行会报 `pygame.error: No available video device`。两种应对办法：

1. 加一个虚拟视频驱动再运行（本讲义所有 Pygame 示例都用这种方式验证过）：

   ```bash
   # Windows(Git Bash) / macOS / Linux 通用
   SDL_VIDEODRIVER=dummy python alien_invasion.py
   ```

   窗口不显示，但游戏逻辑照常跑，适合验证代码不报错。
2. 调试阶段**先把窗口设小**：本讲义统一用 `(800, 600)`。教材默认 `(1200, 800)`，大窗口在笔记本上可能一屏放不下，反而看不清飞船有没有出界。

### 2.3 游戏主循环：`while True` 里的四步

普通程序「从头跑到尾就结束」；游戏要**一直待在原地响应你**。实现方式就是一个死循环，教材叫它**主循环**（main loop）：

```text
        while True:  ← 游戏的心脏，每秒跳动几十次
            ┌─────────────────────────────────────┐
            │ 1. 监听事件   pygame.event.get()      │  ← 用户按了什么？
            │ 2. 更新状态   ship.update()          │  ← 飞船该挪到哪？
            │ 3. 更新屏幕   fill + blit + flip     │  ← 把新画面画出来
            │ 4. 控制帧率   clock.tick(60)         │  ← 稳住节奏，别飙车
            └─────────────────────────────────────┘
```

每一步都不能省，省一个都会出症状：

| 步骤 | 如果删掉它 | 症状 |
|---|---|---|
| 监听事件 | 事件队列爆满 | Windows 会认为程序「未响应」，窗口标题变灰、点哪儿都没反应 |
| 更新状态 | 飞船不挪位置 | 按住方向键，飞船像钉在屏幕上 |
| 更新屏幕 | 画面不刷新 | 窗口一片花白，或者飞船「拖出残影」 |
| 控制帧率 | 循环跑满 CPU | 游戏速度快得失控，笔记本风扇狂转 |

### 2.4 帧率：为什么你的游戏在别人电脑上会「加速」

`while True` 有个隐藏问题：**它转多快，完全由电脑的 CPU 和显卡决定**。同一份代码，在你的游戏本上一秒能空转 2000 圈，在一台旧办公电脑上可能只能转 200 圈。如果每圈让飞船移动 1.5 像素，那两台电脑上的飞船速度能差 10 倍——这不是「优化问题」，是「游戏根本没法定制节奏」。

解决办法就是时钟对象：

```python
import pygame

# 在 AlienInvasion.__init__ 里创建一次
clock = pygame.time.Clock()

# 在 run_game 主循环的每一帧结尾调用：这一帧最多"睡"到 1/60 秒
clock.tick(60)
```

`tick(60)` 的意思是：这一圈的活儿 5 毫秒就干完了，就主动睡大约 11.67 毫秒，保证每圈总时长不低于 1/60 秒。生活化类比：**电影放映机**——胶片不是越快越好，而是每秒精确地过 24 帧；`tick(60)` 就是游戏的放映机快门。

★ 顺带把另一半说完：`tick(60)` 里那个 60 不是「最多 60 帧」，而是「**目标 60 帧，慢了就慢，快了就等**」。传 0 表示不设上限，主循环会跑满 CPU——这正是「同一份代码在两台电脑上速度不同」的根源：

```python
# （片段）—— 两种节奏控制，差的就是这一行；真项目里只在主循环末尾保留第一种
clock = pygame.time.Clock()

# ① 限速：每帧最多"睡"到 1/60 秒，速度与机器无关（教材写法）
clock.tick(60)

# ② 不限速：跑多快算多快，旧电脑慢、新电脑快（调试时才会临时这么写）
clock.tick(0)          # 等价于 # clock.tick()

# 想确认节奏对不对，把实测帧率打出来
print("实测 FPS：", clock.get_fps())      # 稳定在 60 附近才算对
```

### 2.5 事件驱动：游戏像一个前台接待

新手第一次接触「事件驱动」通常会很懵：我的代码明明在跑循环，怎么用户一按键盘它就有反应？

把它想成医院前台：

```text
   用户按了一下右方向键
            │
            ▼
   ┌─────────────────┐
   │  事件队列(event  │   按一下 = 往筐里放一张"访客登记表"
   │  queue)         │   按住不放 ≠ 一直放表，只放一张！
   └─────────────────┘
            │   pygame.event.get() 把筐里的表一次性全部取走
            ▼
   for event in pygame.event.get():   ← 前台一张一张处理登记表
       if event.type == pygame.QUIT:  sys.exit()
```

几个关键点：

- **`pygame.event.get()` 取的是「积压的所有事件」**，不是「刚刚发生的那一个」。你 1 秒没理它，筐里可能躺着十几张表，`get()` 会一次性全倒给你。
- **每张表有类型**：`event.type`。最常用的几种：

| 事件类型 | 什么时候触发 | 典型处理 |
|---|---|---|
| `pygame.QUIT` | 用户点窗口关闭按钮 | `sys.exit()` 退出游戏 |
| `pygame.KEYDOWN` | 按下一个键（瞬间一次） | 记下「这个键现在按下了」 |
| `pygame.KEYUP` | 松开一个键 | 记下「这个键松开了」 |

- **同一次按键，还带细节**：`event.key` 告诉你具体是哪个键，比如 `pygame.K_RIGHT`（右方向键）、`pygame.K_q`（字母 Q）。
- `QUIT` 和 `KEYDOWN` 的分工：`QUIT` 关心「窗口还在不在」，`KEYDOWN` 关心「键盘上谁被按了」。两者是并列的分支，用 `elif` 串起来即可。

### 2.6 `Settings` 类：把「会变的数值」集中管理

游戏里有一类数天生善变：窗口尺寸、背景色、飞船速度。如果把它们写成「散落各处的小数字」（术语叫**魔数**），调参会变成噩梦——改速度时你根本不知道有几处写死了 1.5。

教材的做法是建一个 `Settings` 类，把这些值全放进去：

```python
class Settings:
    """存储《外星人入侵》所有设置的类。"""

    def __init__(self):
        # 屏幕设置
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)   # RGB：浅灰色

        # 飞船设置
        self.ship_speed = 1.5
```

这就是你**第一次亲手做「重构」**——功能不变，结构变好。原来的背景色可能直接写在 `alien_invasion.py` 里：

```python
class AlienInvasion:
    """重构前：颜色硬编码在主文件里。"""

    def __init__(self):
        self.bg_color = (230, 230, 230)     # 想改颜色？来主文件里翻
```

```python
class AlienInvasion:
    """重构后：主文件只认 settings，颜色归 Settings 管。"""

    def __init__(self):
        self.settings = Settings()          # 数值都去 settings.py 里找
```

好处立竿见影：想换黑色背景、想把飞船速度从 1.5 调到 3，只改 `settings.py` 一处，全游戏生效。这也是 12.6 节「调整飞船的速度」只动几行代码的原因。

生活化类比：`Settings` 就像空调遥控器——没有它，调温度得爬进墙里拨码盘；有了它，温度、模式、风速全在一块面板上。

### 2.7 `screen_rect`：让飞船知道自己「站在哪」

Pygame 里所有可见元素都用一个**矩形（rect）**描述位置和大小——可以把它理解成快递单：写着包裹在哪、有多大。屏幕自己也有一个 rect，叫 `screen_rect`：

```python
class Ship:
    """飞船如何描述自己的位置。"""

    def __init__(self, ai_game):
        # 屏幕自己也是一个矩形：拿到它，才知道"活动范围"有多大
        self.screen_rect = ai_game.screen.get_rect()
        # "底部正中间"不用自己算坐标，用锚点属性一句话搞定
        self.rect.midbottom = self.screen_rect.midbottom
```

`rect` 提供了一堆「锚点属性」，不用你自己算坐标：

| 属性 | 含义 | 常见用途 |
|---|---|---|
| `rect.midbottom` | 底边中点 | 飞船出生点（屏幕底部中间） |
| `rect.midtop` | 顶边中点 | 第 13 章子弹从飞船顶部射出 |
| `rect.right` / `rect.left` | 右 / 左边缘的 x 坐标 | 判断是否碰到屏幕左右边界 |
| `rect.x` / `rect.y` | 左上角坐标 | 精确控制位置 |
| `rect.centerx` / `rect.centery` | 中心点坐标 | 居中类操作 |

注意一个坑：`rect.x`、`rect.y` 以及四个边缘坐标**只能存整数**，赋小数会被取整（实测 pygame 2.6 按四舍五入处理）。而 `ship_speed = 1.5` 是小数，直接 `self.rect.x += 1.5` 会每帧都走 2 像素，比设定的速度更快。解决办法是自己维护一个浮点坐标 `self.x`——2.8 节细说。

### 2.8 驾驶飞船：`moving_right` 标志位与持续移动

新手最直觉的写法是：在 `KEYDOWN` 里直接 `self.rect.x += 1`。跑一下就会发现：**按住右方向键，飞船只挪一格就停了。**原因回到 2.5 节：**按住不放，事件队列里也只放了一张登记表**——`KEYDOWN` 是「按下的那一瞬间」触发一次，不是「按住的整个期间」持续触发。

解决办法是把「瞬时事件」翻译成「持续状态」——用一个布尔标志位：

```python
import pygame

# KEYDOWN 时：把开关打开（灯亮）
ship_moving_right = True

# KEYUP 时：把开关关上（灯灭）
ship_moving_right = False

# 每一帧都问一次开关状态（写在 Ship.update() 里）
if ship_moving_right:
    ship_x += 1.5
```

生活化类比：**电梯按钮**。`KEYDOWN` 是你按按钮的那一下（瞬间），`moving_right = True` 是按钮里那盏被点亮的灯（持续状态），电梯运行期间一直看的是灯，不是你按没按。手松开（`KEYUP`）灯灭了，电梯到这一帧才停。

这里有两个容易写错的细节：

1. **`KEYDOWN` 和 `KEYUP` 必须成对出现**。只置 `True` 不忘置 `False`，飞船会一直向右跑到屏幕外，再也回不来。
2. **向右和向左用两个独立的 `if`，不要用 `elif`**。这样两个键同时按下时互相抵消，飞船原地不动——这比「向右优先」更符合直觉。

**为什么用 `self.x` 浮点记账？** `pygame.Rect` 的坐标**只能存整数**，赋小数会被取整。把 `ship_speed` 设成 1.5 时，直接 `self.rect.x += 1.5` 实测每帧会走 2 像素，比设定的速度更快；先用浮点变量 `self.x` 记下真实位置、每帧再同步 `self.rect.x = self.x`，累积值就始终精确，只有显示时取整。这个技巧第 13 章处理子弹时会再用一次。

限制活动范围同样靠 `screen_rect`：

```python
class Ship:
    """加上边界检查后的 update()（项目 ship.py 中的片段）。"""

    def __init__(self, settings, screen_rect):
        self.settings = settings
        self.screen_rect = screen_rect
        self.x = 0.0
        self.moving_right = False
        self.moving_left = False

    def update(self):
        # 向右移动的条件：右边缘还没碰到屏幕右边缘
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        # 向左移动的条件：还没越过左边缘
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        # 把浮点坐标同步回矩形（Rect 会自动取整）
        self.rect.x = self.x
```

「向右移动」的条件是「还没到右边界」；「向左移动」的条件是「还没到左边界」。这样飞船永远在屏幕内。

按 `Q` 键退出是一个贴心设计（不用非得去点窗口右上角）：

```python
def _check_keydown_events(self, event):
    """响应按键。"""
    if event.key == pygame.K_RIGHT:
        self.ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        self.ship.moving_left = True
    elif event.key == pygame.K_q:
        sys.exit()
```

### 2.9 重构 `_check_events()` 和 `_update_screen()`：让主循环保持「薄」

写到 12.6 节，主循环里已经同时躺着事件处理、飞船更新、屏幕绘制三段代码。教材此时又做了一次重构，把两段代码分别搬进两个辅助方法：

```python
def run_game(self):
    while True:
        self._check_events()      # 所有事件相关，都进这里
        self.ship.update()        # 状态更新
        self._update_screen()     # 所有绘制相关，都进这里
        self.clock.tick(60)       # 帧率
```

为什么值得再折腾一次？因为**主循环是每帧都要读一遍的代码，可读性优先级最高**。四行主循环一眼就能看出游戏骨架；事件处理和绘制各有几十行，塞在里面只会互相干扰。

类比还是餐厅：店长不用知道每道菜怎么炒，他只管四点名——「听客人点单、让厨师做菜、上菜、控制上菜节奏」。等第 13 章加入子弹和外星人，主循环里要加的无非是 `self._update_bullets()` 和 `self._update_aliens()` 两行，依然是四五行。

---

## 三、可运行代码示例

> 以下示例都可以直接运行。Pygame 示例在无显示环境里请加前缀 `SDL_VIDEODRIVER=dummy`；窗口类示例会打开 800×600 的窗口，按关闭按钮或 `Q` 键退出。

### 示例 1：settings.py——把会变的数值集中管理

```python
# settings.py —— 《外星人入侵》的设置簿
# 直接运行本文件会打印所有设置，方便确认改动是否生效


class Settings:
    """存储游戏《外星人入侵》所有设置的类。"""

    def __init__(self):
        """初始化游戏的静态设置。"""
        # —— 屏幕设置 ——
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)      # RGB 三元组：浅灰色

        # —— 飞船设置 ——
        self.ship_speed = 1.5                # 每帧移动的像素数

    def describe(self):
        """返回一段人类可读的设置描述。"""
        return (
            f"窗口: {self.screen_width}x{self.screen_height}\n"
            f"背景色: {self.bg_color}\n"
            f"飞船速度: {self.ship_speed} 像素/帧"
        )


if __name__ == "__main__":
    # 直接运行本文件时的演示：打印当前设置
    settings = Settings()
    print(settings.describe())

    # 体验"集中管理"的便利：改一行，全游戏生效
    settings.bg_color = (0, 0, 0)
    settings.ship_speed = 3.0
    print("\n—— 调整之后 ——")
    print(settings.describe())
```

运行结果：

```text
窗口: 800x600
背景色: (230, 230, 230)
飞船速度: 1.5 像素/帧

—— 调整之后 ——
窗口: 800x600
背景色: (0, 0, 0)
飞船速度: 3.0 像素/帧
```

### 示例 2：alien_invasion.py——最小窗口骨架

```python
# alien_invasion.py —— 《外星人入侵》最小骨架：能开窗、能关闭、有背景色
# 运行：SDL_VIDEODRIVER=dummy python alien_invasion.py（有桌面环境可去掉前缀）
import sys

import pygame


class Settings:
    """简化版设置类（真实项目里这一整块搬去 settings.py）。"""

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)


class AlienInvasion:
    """管理游戏资源和行为的类。"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()

        # 创建 800x600 的窗口，并设置标题
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

    def run_game(self):
        """开始游戏的主循环。"""
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """响应按键和鼠标事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕。"""
        self.screen.fill(self.settings.bg_color)   # 每帧重刷背景
        pygame.display.flip()                      # 让最近绘制的屏幕可见


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
```

这个文件虽然还什么都不能玩，但已经「麻雀虽小五脏俱全」。以后你写的每个 Pygame 游戏，骨架都和它一模一样。

### 示例 3：event_observer.py——亲眼看看「事件队列」里有什么

事件驱动最反直觉的地方是「看不见摸不着」。这个程序把取出来的每个事件打印出来，让队列现形；8 秒后自动退出，方便在无显示环境跑。

```python
# event_observer.py —— 事件观察器：打印 pygame 取到的每一个事件
# 运行：SDL_VIDEODRIVER=dummy python event_observer.py
import sys
import time

import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("事件观察器")
clock = pygame.time.Clock()

start = time.perf_counter()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("收到 QUIT：用户点了关闭按钮")
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # event.key 是键的编号，用 pygame.key.name() 翻译成人类可读的名字
            print(f"收到 KEYDOWN：按下了 {pygame.key.name(event.key)}")
        elif event.type == pygame.KEYUP:
            print(f"收到 KEYUP：松开了 {pygame.key.name(event.key)}")

    # 8 秒后自动退出，避免无显示环境里死循环跑不完
    if time.perf_counter() - start > 8:
        print("演示时间到，自动退出。")
        break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

运行结果（在真实桌面环境里按了几下右方向键和 `q`）：

```text
收到 KEYDOWN：按下了 right
收到 KEYUP：松开了 right
收到 KEYDOWN：按下了 q
收到 KEYUP：松开了 q
收到 QUIT：用户点了关闭按钮
```

`KEYDOWN` 和 `KEYUP` 成双成对出现，正好对应 2.5 节说的「灯亮」和「灯灭」。

### 示例 4：ship.py——飞船类（12.6 节完成时）

这是 `ship.py` 的完整样子：加载图像、放在屏幕底部中央、根据标志位移动、限制在屏幕内。把它和示例 1 的 `settings.py`、示例 5 的 `alien_invasion.py` 放在同一目录，就能得到能驾驶的飞船。

```python
# ship.py —— 管理飞船的类（12.6 节完成时）
import pygame


class Ship:
    """管理飞船的类。"""

    def __init__(self, ai_game):
        """初始化飞船并设置其起始位置。"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        # 教材使用 images/ship.bmp；加载失败时画一张占位图，保证代码可运行
        try:
            self.image = pygame.image.load("images/ship.bmp")
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((60, 48))
            self.image.fill((70, 130, 180))
        self.rect = self.image.get_rect()

        # 每艘新飞船都放在屏幕底部的中央
        self.rect.midbottom = self.screen_rect.midbottom

        # 浮点坐标：rect.x 只存整数，直接加 1.5 会被取整，所以单独记一份小数
        self.x = float(self.rect.x)

        # 移动标志：刚创建时两个都是 False，飞船不动
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """根据移动标志调整飞船的位置，并限制在屏幕内。"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 把浮点坐标同步回矩形（Rect 会自动取整）
        self.rect.x = self.x

    def blitme(self):
        """在指定位置绘制飞船。"""
        self.screen.blit(self.image, self.rect)
```

三个文件的分工在这一刻彻底清晰了：

```text
alien_invasion.py   ← 示例 5：主循环，只负责"点名"
    ├── settings.py ← 示例 1：所有会变的数值
    └── ship.py     ← 示例 4：飞船自己的数据和行为
```

### 示例 5：alien_invasion.py——完整版（可驾驶的飞船）

这是 12.6 节结束时项目主文件的样子。配合示例 1 和示例 4 的两个文件即可运行：

```bash
SDL_VIDEODRIVER=dummy python alien_invasion.py
```

```python
# alien_invasion.py —— 《外星人入侵》主文件（12.6 节完成时）
# 依赖同目录下的 settings.py 和 ship.py
import sys

import pygame
from settings import Settings
from ship import Ship


class AlienInvasion:
    """管理游戏资源和行为的类。"""

    def __init__(self):
        """初始化游戏并创建资源。"""
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

        # 创建飞船（传入 self，飞船就能拿到 screen 和 settings）
        self.ship = Ship(self)

    def run_game(self):
        """开始游戏的主循环。"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_screen()
            self.clock.tick(60)

    # —— 事件处理 ——

    def _check_events(self):
        """响应按键和鼠标事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """响应按键。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        """响应松键。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    # —— 画面更新 ——

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕。"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        pygame.display.flip()


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
```

12.7 节的「简单回顾」说的就是这三个文件：`alien_invasion.py` 组织主循环，`settings.py` 存放设置，`ship.py` 管理飞船。到第 13 章加入子弹和外星人时，你只需要新增 `bullet.py` 和 `alien.py`，再把 `_update_bullets()`、`_update_aliens()` 两行加进主循环——主文件的主体结构一个字都不用改。

### 示例 6：frame_rate_demo.py——不打开窗口，看懂帧率

帧率是个纯节奏问题，用纯 Python 就能演示，顺便告诉你「不控制帧率会怎样」。

```python
# frame_rate_demo.py —— 用纯 Python 演示帧率控制
# 运行：python frame_rate_demo.py（不需要 pygame）
import time


def run_loop(fps_limit, seconds):
    """模拟主循环：每圈干一点活，可选限制帧率。"""
    frames = 0
    start = time.perf_counter()
    while True:
        frames += 1
        # 每圈"干的活"：模拟真实游戏一帧的计算量
        _ = sum(range(50000))
        if time.perf_counter() - start >= seconds:
            break
        if fps_limit:
            time.sleep(1 / fps_limit)
    return frames


SECONDS = 2
unlimited = run_loop(None, SECONDS)
limited = run_loop(60, SECONDS)

print(f"不限制帧率：{SECONDS} 秒跑了 {unlimited} 帧")
print(f"限制 60 FPS：{SECONDS} 秒跑了 {limited} 帧")
print(f"差距约 {unlimited / limited:.0f} 倍 —— 这就是别人电脑上游戏'加速'的原因")
```

运行结果（数字因机器而异，但量级关系不变）：

```text
不限制帧率：2 秒跑了 3903 帧
限制 60 FPS：2 秒跑了 120 帧
差距约 33 倍 —— 这就是别人电脑上游戏'加速'的原因
```

如果飞船每帧固定移动 1.5 像素，那么在「不限制帧率」的电脑上，飞船速度是 60 FPS 电脑上的 11 倍——根本没法玩。`clock.tick(60)` 就是把这两行输出掰成一致的那只手。

## 四、动手练习

### 基础档

**练习 12-1【给 Settings 增加两组设置】**

在示例 1 的 `Settings` 类里增加两组设置：子弹设置（`bullet_speed = 2.0`、`bullet_width = 3`、`bullet_height = 15`、`bullet_color = (60, 60, 60)`）和外星人设置（`alien_speed = 1.0`、`fleet_direction = 1`），并把它们加进 `describe()` 的输出。

验收点：`python settings.py` 输出包含全部 9 个设置项，分组注释清晰。

**练习 12-2【按键切换背景色】**

修改示例 2 的最小骨架：按 `1` 背景变浅灰 `(230, 230, 230)`，按 `2` 变黑 `(0, 0, 0)`，按 `3` 变深蓝 `(20, 40, 80)`。提示：用 `event.key == pygame.K_1` 判断数字键。

验收点：运行后按数字键背景色立即切换，按关闭按钮能正常退出。

**练习 12-3【飞船撞墙就停】**

写一个小程序：一开始就按住右方向键，飞船走到右边界就停住（可以直接使用示例 4 的 `Ship` 类）。要求：到边界后继续按右键位置不再变化；控制台只打印一次「已到达右边界」；5 秒后自动退出并打印最终 `rect.x`。

验收点：最终 `rect.x` 等于 `800 - 60 = 740`（用自己的图片时等于 `800 - 图片宽度`）。

### 进阶档

**练习 12-4【让飞船也能上下移动】（教材未涉及，补充说明）**

教材只做了左右移动。现在给飞船加上 `moving_up` / `moving_down` 两个标志位，让它能上下移动，同样受屏幕上下边界限制。上边界参考 `self.rect.top > 0`，下边界参考 `self.rect.bottom < self.screen_rect.bottom`；为了处理竖直方向的小数速度，需要再维护一个 `self.y`。

验收点：飞船在屏幕内自由移动，四个边界都撞不出去；四个标志位的 `if` 相互独立。

**练习 12-5【写一个帧率观察器】**

在示例 2 的基础上，每秒在控制台输出一行 `当前帧率: XX FPS`。提示：`self.clock.get_fps()` 可以拿到时钟对象估算的帧率。

验收点：输出稳定在 60 附近（±3）；把 `self.clock.tick(60)` 注释掉后再跑，帧率明显飙升——用这个实验证明帧率控制的作用。

**练习 12-6【把臃肿的主循环重构成两个辅助方法】**

下面这段代码把所有逻辑都塞在 `run_game` 里，请重构成 `_check_events()` 和 `_update_screen()` 两个方法：

```python
# INTENTIONALLY-BROKEN 演示用：结构糟糕但能跑，重构成 _check_events/_update_screen
import sys

import pygame


class MessyGame:
    def __init__(self):
        pygame.init()
        self.settings_bg = (230, 230, 230)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        sys.exit()
            self.screen.fill(self.settings_bg)
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    MessyGame().run_game()
```

验收点：重构后 `run_game` 方法体只有 4 行；事件处理和屏幕绘制各自独立成方法；行为与原版一致。

---

## 五、参考答案

### 参考答案 12-1

```python
# settings.py —— 增加子弹和外星人两组设置后的完整版
class Settings:
    """存储游戏《外星人入侵》所有设置的类。"""

    def __init__(self):
        # —— 屏幕设置 ——
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # —— 飞船设置 ——
        self.ship_speed = 1.5

        # —— 子弹设置 ——
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)

        # —— 外星人设置 ——
        self.alien_speed = 1.0
        self.fleet_direction = 1        # 1 表示向右移，-1 表示向左移

    def describe(self):
        return (
            f"窗口: {self.screen_width}x{self.screen_height}\n"
            f"背景色: {self.bg_color}\n"
            f"飞船速度: {self.ship_speed}\n"
            f"子弹: 速度{self.bullet_speed} "
            f"{self.bullet_width}x{self.bullet_height} {self.bullet_color}\n"
            f"外星人: 速度{self.alien_speed} 方向{self.fleet_direction}"
        )


if __name__ == "__main__":
    print(Settings().describe())
```

这两组设置现在虽然还没被用到，但第 13 章会原样接手——这就是提前规划的回报。

### 参考答案 12-2

```python
# alien_invasion.py —— 支持数字键切换背景色
import sys

import pygame


class Settings:
    """带三套候选背景色的设置类。"""

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)
        # 有哪些颜色，归 Settings 管，不写在事件处理里
        self.bg_options = {
            pygame.K_1: (230, 230, 230),
            pygame.K_2: (0, 0, 0),
            pygame.K_3: (20, 40, 80),
        }


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit()
        elif event.key in self.settings.bg_options:
            self.settings.bg_color = self.settings.bg_options[event.key]
            print(f"背景色切换为: {self.settings.bg_color}")

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        pygame.display.flip()


if __name__ == "__main__":
    AlienInvasion().run_game()
```

`event.key in self.settings.bg_options` 比写三个 `elif` 更短，也把「有哪些颜色」留在了 `Settings` 里。

### 参考答案 12-3

```python
# ship_demo.py —— 飞船撞右边界就停（复用示例 4 的 Ship）
import sys
import time

import pygame

from ship import Ship


class ShipDemo:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("撞墙就停")
        self.bg_color = (230, 230, 230)

        # 准备一个"假游戏"对象喂给 Ship（Ship 只用 screen 和 settings）
        class StubSettings:
            ship_speed = 2

        class FakeGame:
            screen = self.screen
            settings = StubSettings()

        self.ship = Ship(FakeGame())
        self.ship.moving_right = True     # 相当于一开始就按住右方向键
        self.reported = False

    def run(self):
        start = time.perf_counter()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return

            # 到边界时报告一次（Ship.update 已保证位置不再变化）
            if not self.reported and self.ship.rect.right >= 800:
                print("已到达右边界")
                self.reported = True

            self.ship.update()
            self.screen.fill(self.bg_color)
            self.ship.blitme()
            pygame.display.flip()
            self.clock.tick(60)

            if time.perf_counter() - start > 5:
                print("最终 rect.x =", self.ship.rect.x)
                return


if __name__ == "__main__":
    ShipDemo().run()
    pygame.quit()
```

运行结果：

```text
已到达右边界
最终 rect.x = 740
```

`740 = 800 - 60`，正是飞船右边缘贴住屏幕右边缘的位置。

### 参考答案 12-4

```python
# ship.py —— 支持四方向移动的飞船类
import pygame


class Ship:
    """管理飞船的类（四方向版）。"""

    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        try:
            self.image = pygame.image.load("images/ship.bmp")
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((60, 48))
            self.image.fill((70, 130, 180))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        # 两个方向各记一份浮点坐标
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # 四个移动标志，全部独立
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """根据移动标志调整位置，四个边界都限制住。"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed

        self.rect.x = self.x
        self.rect.y = self.y

    def blitme(self):
        self.screen.blit(self.image, self.rect)
```

主文件里补上方向键的上下分支（`KEYDOWN` 和 `KEYUP` 各补两个 `elif`，写法与左右完全对称）：

```python
class KeyHandler:
    """只贴出新增的两个分支，其余与示例 5 相同。"""

    def _check_keydown_events(self, event):
        if event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True

    def _check_keyup_events(self, event):
        if event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False
```

四个 `if` 保持独立是有意的：同时按「右」和「下」，飞船沿对角线走，两个方向互不干扰。

### 参考答案 12-5

在示例 2 的骨架上加一个 `_report_fps()` 方法，并在主循环里调用它：

```python
# alien_invasion.py —— 只贴出与帧率显示相关的部分
import pygame


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.last_report = pygame.time.get_ticks()   # 上次报告帧率的时刻

    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)
            self._report_fps()          # 新增：报告帧率

    def _report_fps(self):
        """每秒打印一次实际帧率。"""
        now = pygame.time.get_ticks()
        if now - self.last_report >= 1000:
            print(f"当前帧率: {self.clock.get_fps():.1f} FPS")
            self.last_report = now
```

运行结果（前几行）：

```text
当前帧率: 60.0 FPS
当前帧率: 60.0 FPS
```

**建议亲手做的实验**：把 `self.clock.tick(60)` 注释掉再跑，帧率会冲到几百上千——这正是示例 6 用纯 Python 演示过的现象，这次你亲眼看到了。

### 参考答案 12-6

```python
# alien_invasion.py —— 重构后：主循环只剩四行
import sys

import pygame


class CleanGame:
    def __init__(self):
        pygame.init()
        self.settings_bg = (230, 230, 230)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))

    def run_game(self):
        """主循环保持'薄'：只负责按顺序点名。"""
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """所有事件相关的逻辑都下沉到这里。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()

    def _update_screen(self):
        """所有绘制相关的逻辑都下沉到这里。"""
        self.screen.fill(self.settings_bg)
        pygame.display.flip()


if __name__ == "__main__":
    CleanGame().run_game()
```

重构前后行为完全一致，但 `run_game` 从 11 行瘦到 4 行，四个步骤各是什么一目了然。等第 13 章加入子弹和外星人，这个主循环只会多两行——这就是「薄主循环」的复利。

---

## 六、常见错误清单

### 错误 1：★ 忘了 `import sys` 就调用 `sys.exit()`

```python
# INTENTIONALLY-BROKEN 演示用：NameError: name 'sys' is not defined
import pygame

pygame.init()
pygame.display.set_mode((800, 600))
sys.exit()
```

**症状**：点关闭按钮时程序崩溃并甩出 `NameError`，而不是干净退出。**处方**：文件开头补上 `import sys`。

### 错误 2：忘了调用 `pygame.event.get()`

**症状**：窗口打开后整个界面卡住，标题栏写着「未响应」，鼠标转圈。原因：不取事件，队列就会积压爆满，操作系统认为你的程序「装死」。**处方**：主循环第一步永远是 `for event in pygame.event.get():`，哪怕什么都不处理，也要把事件取走。

### 错误 3：在 `KEYDOWN` 里直接改位置，而不是置标志位

```python
# INTENTIONALLY-BROKEN 演示用：按住方向键，飞船只挪一格
import sys

import pygame

ship_x = 0
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            ship_x += 2      # 错：KEYDOWN 只在按下瞬间触发一次
```

**症状**：按住右方向键，飞船「跳」一格就停。**处方**：`KEYDOWN` 里只置 `moving_right = True`，移动写在每帧都执行的 `update()` 里。**这是本单元最重要的知识点。**

### 错误 4：`rect.x` 是整数，小数速度被取整

```python
# INTENTIONALLY-BROKEN 演示用：speed = 1.5，实际每帧走 2 像素
import pygame

rect = pygame.Rect(0, 0, 60, 48)
rect.x += 1.5
print("rect.x =", rect.x)      # 输出 2 —— 1.5 被四舍五入成 2，速度失真
```

**处方**：自己维护浮点坐标 `self.x = float(self.rect.x)`，每帧 `self.rect.x = self.x` 同步回矩形——累积值保持精确，只有显示时取整。

### 错误 5：忘了在 `KEYUP` 里把标志位置回 `False`

```python
# INTENTIONALLY-BROKEN 演示用：只开不关，飞船飞出屏幕
import sys

import pygame

ship_moving_right = False
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            ship_moving_right = True      # 开了灯
    # 漏掉了对应的 KEYUP 处理：找不到关灯的地方，标志位永远是 True
```

**症状**：按一下右方向键，飞船径直飞出屏幕外。**处方**：`KEYDOWN` 和 `KEYUP` 必须成对处理。

### 错误 6：`moving_right` 和 `moving_left` 写成 `elif`

```python
# INTENTIONALLY-BROKEN 演示用：同时按左右键，"向左"永远抢不到
import sys

import pygame

moving_right = False
moving_left = False
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            moving_right = True
        elif event.key == pygame.K_LEFT:      # 同一时刻只有一个分支能进
            moving_left = True
```

**处方**：左右（以及上下）的判断各自独立，用并列的 `if`，同时按下时互相抵消。

---

## 七、本单元验收自测

**1. 简答题**：外星人入侵为什么拆成三个文件？主循环的四步分别是什么？

> **要点**：为了「一个文件一个职责」——`alien_invasion.py` 组织主循环并分派任务，`settings.py` 集中管理会变的数值，`ship.py` 管飞船自己的行为。四步：① `pygame.event.get()` 监听事件；② `ship.update()` 更新状态；③ `fill` + `blitme` + `flip()` 更新屏幕；④ `clock.tick(60)` 控制帧率。

**2. 判断题**：`while True` 转得越快游戏越流畅，所以不需要 `clock.tick(60)`。

> **要点**：错。帧率不固定，游戏速度就随电脑性能变化——同一份代码在快电脑上飞船飞快，在慢电脑上慢如蜗牛；空转还会吃满 CPU。`tick(60)` 是「能玩」和「不能玩」的分水岭。

**3. 选择题**：用户按住右方向键 3 秒，`KEYDOWN` 事件会发生几次？

> A. 1 次　B. 3 次　C. 60 次　D. 每秒 1 次
>
> **要点**：选 A。`KEYDOWN` 是「按下的瞬间」触发一次；Pygame 默认不开启操作系统的按键重复，所以持续按住也只收到一个 `KEYDOWN`。这就是必须用标志位把「瞬间」翻译成「持续状态」的原因。

**4. 改错题**：下面代码想让飞船向右移动，但按住键时飞船完全不动，请指出问题。

```python
# INTENTIONALLY-BROKEN 演示用：飞船不动（缺标志位、缺主循环调用）
import pygame


class Ship:
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.rect = pygame.Rect(0, 0, 60, 48)
        self.rect.midbottom = self.screen_rect.midbottom

    def update(self):
        self.rect.x += 1.5      # 问题一：没有"是否向右"的状态可依循
```

> **要点**：① 没有任何地方设置「要向右移动」的状态，主循环里也没调用 `self.ship.update()`；应加 `moving_right` 标志位，`KEYDOWN` 置 `True`、`KEYUP` 置 `False`，`update()` 里 `if self.moving_right: self.x += self.settings.ship_speed`。② `rect.x` 只能存整数，`+= 1.5` 会被取整成 2，速度失真；应改用浮点坐标 `self.x`，再同步 `self.rect.x = self.x`。

**5. 简答题**：`self.screen_rect` 是干什么用的？限制飞船活动范围靠哪两个条件？

> **要点**：`screen_rect` 是屏幕的矩形，通过 `ai_game.screen.get_rect()` 获得，用来描述「活动范围」有多大。向右时要求 `self.rect.right < self.screen_rect.right`，向左时要求 `self.rect.left > 0`。

**6. 简答题**：`Settings` 类体现了什么思想？12.6 节「调整飞船的速度」为什么只改了几行？

> **要点**：体现了「集中管理可变数值」的重构思想——把魔数收进一个类，改一处全游戏生效。因为速度值只存在于 `Settings` 一处，调整时只需改 `settings.py` 里的 `ship_speed`，主文件和飞船类都不用动。

---

## 本单元小结与产出检查

- [ ] 能画出三个文件的分工图，说清各自负责什么
- [ ] 能默写游戏主循环的四步，并解释 `clock.tick(60)` 的作用
- [ ] 能用「前台接待」类比讲清事件队列、`pygame.event.get()`、`KEYDOWN` / `KEYUP` / `QUIT`
- [ ] 已创建 `Settings` 类，把窗口尺寸、背景色、飞船速度都收拢进去
- [ ] 已用 `moving_right` / `moving_left` 标志位实现持续移动，并用 `screen_rect` 限制活动范围
- [ ] 已把主循环重构成 `_check_events()` + `_update_screen()` 的薄结构
- [ ] 练习 12-1、12-2、12-3 已跑通；练习 12-4（四方向移动）已跑通

**下一单元预告**：单元 13 进入第 12 章后半段和第 13 章——先给飞船装上子弹（`Bullet` 类和编组 `Group`），再创建一整支外星舰队，让它们整体移动、被子弹击落，最后给游戏加上「结束条件」。你会第一次接触到 Pygame 的「编组」这个核心工具，以及碰撞检测。
