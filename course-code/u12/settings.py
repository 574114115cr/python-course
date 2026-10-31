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
