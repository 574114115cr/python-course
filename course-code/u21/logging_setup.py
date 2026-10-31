# logging_setup.py —— 项目通用的日志配置模板
# 用法：from logging_setup import setup_logging
import logging
import logging.handlers
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-12s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(name="my_project", level="INFO", log_file="data/app.log"):
    """配置并返回一个 logger。

    装两个 handler：① RotatingFileHandler 写文件，单文件超 1MB 就轮换、最多留 3 份，
    防止日志把磁盘写满；② StreamHandler 让终端也能看到，方便开发。
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()      # 重复调用时先清空，否则日志会打印好几遍
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False     # 不冒泡到 root，避免重复输出
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    for handler in (logging.handlers.RotatingFileHandler(
                        path, maxBytes=1_000_000, backupCount=3,
                        encoding="utf-8"),
                    logging.StreamHandler()):
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def main():
    """最小可跑演示：建 logger → 记三条不同级别的日志。"""
    logger = setup_logging(name="demo", log_file="data/app.log")
    logger.info("程序启动")
    logger.warning("这是一条警告：磁盘占用偏高")
    logger.error("这是一条错误：连不上数据库")
    logger.info("程序正常结束，日志已写入 data/app.log")
    # 跑完可以删掉 data/ 目录


if __name__ == "__main__":
    main()
