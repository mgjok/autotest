"""统一日志：控制台 + 文件双输出，按 name 单例复用。

用法：
    from common.logger import get_logger
    log = get_logger(__name__)
    log.info("打开搜索页")
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOGGERS: dict[str, logging.Logger] = {}

FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str = "autotest",
    level: int = logging.INFO,
    log_dir: str | Path = "logs",
) -> logging.Logger:
    """拿 logger（同名复用，不重复加 handler）。

    :param name:  logger 名，建议传 __name__。
    :param level:  控制台和文件统一级别。
    :param log_dir: 日志目录，默认 logs/，自动创建。
    :return: 配好双输出的 logger，文件固定写 log_dir/autotest.log。
    """
    if name in _LOGGERS:
        return _LOGGERS[name]
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 不往 root 冒，避免 pytest log_cli 重复打印
    if not logger.handlers:
        fmt = logging.Formatter(FMT, DATEFMT)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        d = Path(log_dir)
        d.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(d / "autotest.log", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    _LOGGERS[name] = logger
    return logger
