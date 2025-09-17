#!/usr/bin/env python3
# 项目：自用函数库
# 模块：校验位计算模块
# 作者：黄涛
# 修订：2019-09-03 10:05 增加

from itertools import cycle
from typing import Iterable


def checksum(s: Iterable, calc, Key: Iterable, Sum: list | str) -> str:
    "计算校验位"
    return Sum[sum(calc(c, k) for c, k in zip(s, Key)) % len(Sum)]


def id_card(card_no: str) -> str | None:
    """修正居民身份证的校验位"""
    Key = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    Sum = "10X98765432"
    length = len(card_no)
    if 15 == length:
        card_no = "19".join([card_no[:6], card_no[6:]])
        length += 2
    if 18 >= length >= 17:
        return card_no[:17] + checksum(card_no[:17], lambda x, y: int(x) * y, Key, Sum)


def org_code(code_no: str) -> str:
    """修正组织机构代码证校验位"""
    key = (3, 7, 9, 10, 5, 8, 4, 2)
    Sum = "0X987654321"
    code_no = code_no[:8].upper()

    def calc(c, k):
        if "0" <= c <= "9":
            return int(c) * k
        elif "A" <= c <= "Z":
            return (ord(c) - 0x37) * k
        else:
            return 0

    return "-".join([code_no, checksum(code_no, calc, key, Sum)])


def bank_card(card_no: str) -> str | None:
    """修正银行卡校验位"""
    Sum = "0987654321"
    if len(card_no) in (16, 17, 19):
        card_no = card_no[:-1]
        return card_no + checksum(
            reversed(card_no),
            lambda x, y: sum(divmod(int(x) * y, 10)),
            cycle([2, 1]),
            Sum,
        )


def credit_code(code: str) -> str | None:
    """修正信用代码证校验位"""
    Base = "0123456789ABCDEFGHJKLMNPQRTUWXY"
    wi = 1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28
    if len(code) >= 17:
        check = sum(Base.index(k) * w for k, w in zip(code, wi)) % 31
        if check:
            check = 31 - check
        return "%s%s" % (code[:17], Base[check])
