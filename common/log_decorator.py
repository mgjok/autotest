"""用例日志装饰器：@log_class / @log_test，记录开始、结果与耗时。

pytest.skip() 会直接透出（仅记录开始）。
"""
from __future__ import annotations

import functools
import time

from common.logger import get_logger


def log_test(func):
    """函数装饰器：记单条用例的开始/通过/失败和耗时。"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log = get_logger(func.__module__)
        name = func.__qualname__
        log.info("开始用例: %s", name)
        t0 = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            log.exception("用例失败: %s 耗时%.2fs", name, time.perf_counter() - t0)
            raise
        log.info("用例通过: %s 耗时%.2fs", name, time.perf_counter() - t0)
        return result

    return wrapper


def log_class(cls):
    """类装饰器：给类里所有 test_* 方法套上 @log_test。"""
    count = 0
    for attr, member in vars(cls).items():
        if attr.startswith("test_") and callable(member):
            setattr(cls, attr, log_test(member))
            count += 1
    get_logger(cls.__module__).info("加载测试类: %s（%d 条用例）", cls.__qualname__, count)
    return cls
