# 项目：python 开发工具包
# 模块：Excel 数据读取程序
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2025-08-01 19:27

from contextlib import suppress
from itertools import chain
from operator import itemgetter
from typing import Callable, Iterable, Literal, Optional, Union

from xlrd3 import Book, open_workbook, xldate_as_tuple

from orange import Path


def conv_date(d, fmt: Literal["date", "time", "datetime"] = "date"):
    with suppress(Exception):
        dt = xldate_as_tuple(d, 0)
        if fmt == "date":
            return "{0:4d}-{1:02d}-{2:02d}".format(*dt)
        elif fmt == "time":
            return "{3:02d}:{4:02d}".format(*dt)
        else:
            return "{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}".format(*dt)
    return d


def colname2idx(col_str: str) -> int:
    "将列名转换成序号"
    col_str = col_str.upper()
    expn, col = 0, 0
    for char in reversed(col_str):
        col += (ord(char) - ord("A") + 1) * (26**expn)
        expn += 1
    return col - 1


def IterCols(col_str: str) -> Iterable:
    "将列名表达式转换成列序号"
    for col in col_str.split(","):
        if ":" in col:
            a, b = col.split(":")
            yield from range(colname2idx(a), colname2idx(b) + 1)
        else:
            yield colname2idx(col)


def proc_data(
    data: list,  # 原始数据
    usecols: str = "",  # 选取列
    converter: Optional[Callable[[list], Optional[list]]] = None,  # 按行转换程序
    skiprows: int = 0,  # 跳过行
    nrows: int = 0,  # 读取行数
) -> Iterable:
    "对数据进行整理"
    if skiprows:
        data = data[skiprows:]
    rdata = iter(data)
    if usecols:
        rdata = map(itemgetter(*IterCols(usecols)), rdata)
    if converter:
        rdata = filter(None, map(converter, rdata))
    if nrows:
        return (d for i, d in zip(range(nrows), rdata))
    else:
        return rdata


def read_excel(
    io: Union[str, Path, Book, None] = None,  # Excel 文件
    file_contents: Optional[bytes] = None,  # 文件内容
    sheets: Union[str, int, list, None] = None,  # 工作表名
    usecols: str = "",  # 选取列
    converter: Optional[Callable[[list], list]] = None,  # 按行转换程序
    skiprows: int = 0,  # 跳过行
    nrows: int = 0,  # 读取行数
) -> Iterable:
    if file_contents is not None:
        with open_workbook(file_contents=file_contents) as book:
            return read_excel(
                book,
                sheets=sheets,
                usecols=usecols,
                converter=converter,
                skiprows=skiprows,
                nrows=nrows,
            )
    elif isinstance(io, (str, Path)):
        with open_workbook(Path(io)) as book:
            return read_excel(
                book,
                sheets=sheets,
                usecols=usecols,
                converter=converter,
                skiprows=skiprows,
                nrows=nrows,
            )
    elif isinstance(io, Book):
        if isinstance(sheets, int):
            sheet = io.sheet_by_index(sheets)
            data = sheet._cell_values
            return proc_data(data, usecols, converter, skiprows, nrows)
        elif isinstance(sheets, str):
            sheet = io.sheet_by_name(sheets)
            data = sheet._cell_values
            return proc_data(data, usecols, converter, skiprows, nrows)
        elif isinstance(sheets, Iterable):
            return chain(
                *(
                    read_excel(
                        io,
                        sheets=sheet,
                        usecols=usecols,
                        converter=converter,
                        skiprows=skiprows,
                        nrows=nrows,
                    )
                    for sheet in sheets
                )
            )
        elif sheets is None:
            return chain(
                *(
                    proc_data(sheet._cell_values, usecols, converter, skiprows, nrows)
                    for sheet in io.sheets()
                )
            )
    else:
        raise Exception("参数有误")
