# 项目：标准库函数
# 模块：调试模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-03-12 17:25

import logging
from functools import wraps

from orange.shell import is_dev

__all__ = (
    "decorator",
    "trace",
    "config_log",
    "ensure",
    "info",
    "fprint",
    "verbose",
    "debug",
)

info = logging.info
debug = logging.debug


def decorator(decorator):
    def _decorator(func):
        @wraps(func)
        def __decorator(*args, **kwargs):
            return decorator(func, *args, **kwargs)

        return __decorator

    return _decorator


@decorator
def trace(func, *args, **kwargs):
    print("The function %s is called" % (func.__name__))
    print("With arguments %s %s" % (args, kwargs))
    result = func(*args, **kwargs)
    print("The result is %s" % (result))
    return result


def verbose():
    config_log(format="%(message)s", level=20)


def config_log(**kwargs):
    kwargs.setdefault("datefmt", "%Y-%m-%d %H:%M:%S")
    kwargs.setdefault("format", "%(levelname)-9s %(message)s")
    kwargs.setdefault("level", 10 if is_dev() else 30)
    logging.basicConfig(**kwargs)


def ensure(cond, msg, level="error"):
    if not cond:
        getattr(logging, level)(msg)
        if level in ("error", "critical", "fatal"):
            raise Exception(msg)


def fprint(*args, sep=" ", end="\n", **kw):
    """force print, used in Windows,解决打印GBK问题
    其中replace是遇无法打印字符的替代字符"""
    try:
        print(*args, sep=sep, end=end, **kw)
    except UnicodeEncodeError:
        s = sep.join(str(x) for x in args)
        s = s.encode("gbk", "ignore").decode("gbk")
        print(s, end=end, **kw)
