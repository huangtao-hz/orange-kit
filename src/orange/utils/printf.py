# 项目：自用函数库
# 模块：格式化打印函数，仿照
# 作者：黄涛
# 修订：2019-09-03 10:05 增加
#
import re
from typing import Any, Optional
from orange.utils.htutil import wlen

Pattern = re.compile(
    r"%(?P<flags>[+-0 ]?)((?P<width>\d+)(?P<thousands>,)?)?(\.(?P<precision>\d+))?(?P<type>[sdf%])"
)


def add_thousands(s: str, thousands: str) -> str:
    "为数字的整数部分增加千分节"
    parts = []
    while s:
        parts.append(s[-3:])
        s = s[:-3]
    return (thousands.join(reversed(parts))).replace("-,", "-", 1)


def format(
    value: Any,
    flags: Optional[str] = None,
    width: Optional[str] = None,
    thousands: Optional[str] = None,
    precision: Optional[str] = None,
    type: Optional[str] = None,
) -> str:
    result = str(value)
    if type == "f" and precision:
        pre_len = int(precision)
        parts = result.split(".")
        if len(parts) == 2:
            result = (
                (add_thousands(parts[0], thousands) if thousands else parts[0])
                + "."
                + (parts[1] + "0" * pre_len)[:pre_len]
            )
    if type == "d" and thousands == ",":
        result = add_thousands(result, thousands)
    length = wlen(result)
    if width:
        w = int(width)
        if type == "s":
            if length < w:
                result = (
                    result + " " * (w - length)
                    if flags == "-"
                    else " " * (w - length) + result
                )
        elif type in ("d", "f"):
            if flags == "+" and result[0] != "-":
                result = "+" + result
                length += 1
            f = "0" if flags == "0" else " "
            if length < w:
                result = f * (w - length) + result
    return result


def printf(fmt: str, *args):
    """
    打造一个兼容 golang 的 printf 函数，支持以下类型：
    整数： %d   %5d   %5,d
    字符串： %s  %-s
    浮点数： %5.2f
    """
    i = 0

    def conv(m: re.Match) -> str:
        nonlocal i
        match = m.groupdict()
        if match["type"] == "%":
            result = "%"
        else:
            result = format(args[i], **match)
            i += 1
        return result

    result = Pattern.sub(conv, fmt)
    if i == len(args):
        print(result, end="")
    else:
        raise Exception("error:参数个数错误")
