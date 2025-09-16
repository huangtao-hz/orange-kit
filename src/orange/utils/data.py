# 项目：公共函数库
# 模块：数据处理模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2019-04-25 11:09
# 修改：2025-01-23 15:07 新增 convdata 函数

"""
本模块为数据转换模块，旨在提供一个数据转换工具和若干标准的转换程序
"""

from operator import itemgetter
from typing import Callable, Iterable

from .htutil import get_md5, limit, split, tprint


def convdata(data: Iterable, convfunc: Callable[[list], list]) -> Iterable:
    """数据转换函数，"""
    yield from filter(None, map(convfunc, data))


def filterer(func: Callable) -> Callable:
    """
    过滤器，参数中的函数为：func(row)->bool
    """

    def _(data):
        return filter(func, data)

    return _


def mapper(func: Callable):
    """
    映射器，可以把一个函数映射，函数原型为： func(row)->row
    """

    def _(data):
        return map(func, data)

    return _


def slicer(*args):
    """
    映射器，对数据进行切片，参数同 slice 函数，可以为：
    (stop) 或
    (start , stop [ , step ] )
    """
    s = slice(*args)

    def _(row):
        return row[s]

    return mapper(_)


def converter(converter):
    """
    转换器，支持两种格式
    1.整行转换，原型为: func(row)->row
    2.按列转换:
    {
        0:func(col)->col
        1:func(col)->col
    }
    """

    def _(row):
        for idx, conv in converter.items():
            row[idx] = conv(row[idx])
        return row

    return mapper(converter) if callable(converter) else mapper(_)


def includer(*columns: Iterable):
    """
    仅包含指定的列，使用方法：includer(0,-2)
    """

    def _(row):
        return [row[col] for col in columns]

    return mapper(_)


def excluder(*columns):
    """
    排除指定的列，使用方法：excluder(0,-2)
    """

    def _(row):
        length = len(row)
        exclude_columns = set(x if x >= 0 else x + length for x in columns)
        return [item for i, item in enumerate(row) if i not in exclude_columns]

    return mapper(_)


def _convert(converter: dict):
    """数据转换"""

    def _(row):
        for idx, conv in converter.items():
            row[idx] = conv(row[idx])
        return row

    return _


def hasher(*columns):
    """
    在行尾增加校验位，columns 指定需要校验的列，使用方法：
    hasher(-2,-1) # 对最后两列进行加密
    """

    def _(row):
        txt = "".join(row[x] for x in columns if row[x])
        return [*row, get_md5(txt)]

    return mapper(_)


def hashfilter(*columns):
    """
    判断设置校验位的数据是否被修改，columns 为需要校验的列，最后一列为校验位
    """
    hash_column = columns[-1]
    columns = columns[:-1]

    def _(row):
        txt = "".join(str(row[x]) for x in columns if row[x])
        return row[hash_column] != get_md5(txt)

    return filterer(_)


class Data:
    __slots__ = "_data", "_rows", "_limit"

    def __init__(self, data, *pipelines, header=None, rows=0, limit=0, **kw):
        self._data = iter(data)
        if header:
            self.header(header)
        for proc in pipelines:
            self._data = proc(self._data)
        for k, v in kw.items():
            getattr(self, k)(v)
        self._rows = rows
        self._limit = limit

    def header(self, header):
        for row in self._data:
            if all(x in row for x in header):
                self.columns([row.index(title) for title in header])
                if isinstance(header, dict):
                    self.converter(
                        {
                            idx: conv
                            for idx, conv in enumerate(header.values())
                            if conv
                        }
                    )
                break
        return self

    def exclude(self, columns):
        columns = set(columns)

        def _(row):
            return [col for i, col in enumerate(row) if i not in columns]

        self._data = map(_, self._data)

    def filter(self, filter_):
        self._data = filter(filter_, self._data)
        return self

    def converter(self, converter):
        if converter:
            if callable(converter):
                self._data = map(converter, self._data)
            else:
                self._data = map(_convert(converter), self._data)
        return self

    def include(self, columns):
        if columns:
            self._data = itemgetter(*columns)(self._data)
        return self

    columns = include

    def __iter__(self)->Iterable:
        if self._rows:
            self._data = split(self._data, self._rows)
        elif self._limit:
            self._data = limit(self._data, self._limit)
        return self._data

    def __next__(self):
        ...

    def split(self, count=10000):
        self._rows = count

    def print(self, format_spec, sep=" ", print_rows: bool = True):
        tprint(
            self._data, format_spec=format_spec, sep=sep, print_rows=print_rows
        )

    def groupby(self, key: Callable) -> Iterable:
        from collections import defaultdict

        data = defaultdict(lambda: [])
        for row in self._data:
            data[key[row]].append(row)
        return data.items()

    def show(self, limit=5):
        "打印指定行的数据"
        for _, row in zip(range(5), self):
            print(len(row), row)
