# 项目：Excel写入模块封装
# 模块：xlsxwriter的封装
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-10-12 08:24
# 修订：2018-05-25 修改add_table的参数格式
# 修订：2019-03-16 21:38 新增 Header 函数
# 修订：2019-12-29 22:00 为 add_table 新增默认值
# 修订：2021-08-15 15:27 新增 Style class
# 修改：2023-05-31 11:26 Header 增加 formula 参数的说明


from dataclasses import dataclass
from functools import partial
from typing import Optional, Union

from xlsxwriter import Workbook
from xlsxwriter.worksheet import (
    CellBlankTuple,
    Worksheet,
    convert_range_args,
    xl_col_to_name,
)

from orange import Path, R

Pattern = R / r"([A-Z]{1,2})(\d*)([:_]([A-Z]{1,2})(\d*))?"
Row = R / r"(\{([+-]?\d+)\})"


@dataclass
class Style:
    font_name: Optional[str] = None  # 字体名称
    font_size: Optional[float] = None  # 字号
    bold: bool = False  # 加粗
    italic: bool = False  # 斜体
    underline: bool = False  # 下划线
    fg_color: Optional[str] = None  # 前景色
    num_format: Optional[str] = None  # 数字格式
    align: Optional[str] = None  # 水平对齐方式，left,center,right
    valign: Optional[str] = None  # 简直对齐方式，top,vcenter,bottom
    text_wrap: bool = False  # 文本换行

    @property
    def style(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def copy(self):
        return Style(**self.style)


DefaultFormat = (
    ("currency", {"num_format": "#,##0.00"}),
    ("rate", {"num_format": "0.0000%"}),
    ("title", {"font_name": "黑体", "font_size": 16, "align": "center"}),
    ("h2", {"font_name": "黑体", "font_size": 12, "align": "center"}),
    (
        "mh2",
        {
            "font_name": "黑体",
            "font_size": 12,
            "text_wrap": True,
            "align": "center",
            "valign": "vcenter",
        },
    ),
    ("percent", {"num_format": "0.00%"}),
    ("date", {"num_format": "yyyy-mm-dd"}),
    ("normal", {"text_wrap": True, "valign": "vcenter"}),
    (
        "cnormal",
        {
            "text_wrap": True,
            "valign": "vcenter",
            "align": "center",
        },
    ),
    ("time", {"num_format": "hh:mm:ss"}),
    ("number", {"num_format": "#,##0"}),
    ("header", {"font_name": "黑体", "font_size": 12, "align": "center"}),
    ("datetime", {"num_format": "yyyy-mm-dd hh:mm:ss"}),
    ("timestamp", {"num_format": "yyyy-mm-dd hh:mm:ss.0"}),
)


def Header(
    header: str,
    width: Optional[float] = None,
    format: Optional[str] = None,
    **kw,
):
    """设置 Excel 表头
    Params:
        header:表头
        width:列宽
        format:行样式
        hidden:是否隐藏列
        total_string:汇总行字符串
        total_function:汇总行函数，支持:sum,count,avg
        formula:公式，示例： formula='[ColumnA]/[ColumnB]'
    """
    kw["header"] = header
    if width:
        kw["width"] = width
    if format:
        kw["format"] = format
    return kw


Account = partial(Header, width=25)
AcName = partial(Header, width=52)
Date = partial(Header, width=14)
Balance = partial(Header, width=18, format="currency")


class Book(Workbook):
    """对Xlsxwriter模块进一步进行封装"""

    def __init__(
        self,
        filename: Union[Path, str, None] = None,
        formats: Optional[dict] = {},
        **kw,
    ):
        if isinstance(filename, (Path, str)):
            filename = str(Path(filename))
        super().__init__(filename, **kw)
        self._worksheet: Optional[Worksheet] = None  # 设置当前的工作表为空
        self._worksheets = {}  # 设置当前的工作表清单为空
        self._formats = {}
        self._sheets = 0  # 默认sheet名
        if formats:
            self.add_formats(formats)

        for name, val in DefaultFormat:
            self.add_format(val, name)

    def add_format(self, properties, name=None):
        if isinstance(properties, Style):
            properties = properties.style
        _format = super().add_format(properties)
        if name:
            self._formats[name] = _format
            _format.name = name
            _format.properties = properties
        return _format

    def add_formats(self, properties):
        for name, property in properties.items():
            self.add_format(property, name)

    def set_widths(self, widths):
        "设置单元格的宽度，其实 widths 为字典"
        [self.set_columns(col, width=width) for col, width in widths.items()]

    def set_row(self, row, height):
        "设置单元格的高度"
        if self.worksheet:
            self.worksheet.set_row(row, height)

    def set_columns(self, *columns, width=None, cell_format=None, options=None):
        """设置当前工作表的列属性，允许同时设置多个，使用方法如下：
        book.set_columns('A:C','E:D','G:H',width=12)
        """
        options = options or {}
        if self.worksheet:
            for column in columns:
                self.worksheet.set_column(column, width, cell_format, options)

    def newline(self):
        """换行"""
        return self + 1

    @property
    def worksheet(self):
        """当前工作表"""
        return self._worksheet

    @worksheet.setter
    def worksheet(self, name: str):
        """切换当前工作表"""
        if not name:
            self._sheets += 1
            worksheet = f"Sheet{self._sheets}"
        worksheet = self._worksheets.get(name, None)
        if not worksheet:
            worksheet = self.add_worksheet(name)
            worksheet.row = 1
            self._worksheets[name] = worksheet
        self._worksheet = worksheet

    @convert_range_args
    def write(
        self,
        first_row,
        first_col,
        last_row=None,
        last_col=None,
        value=None,
        cell_format=None,
    ):
        if isinstance(cell_format, str):
            cell_format = self._formats.get(cell_format)
        if (last_row is None) or (first_row == last_row and first_col == last_col):
            if self.worksheet and isinstance(value, (tuple, list)):
                self.worksheet.write_row(first_row, first_col, value, cell_format)
            else:
                if self.worksheet and isinstance(value, str) and value.startswith("="):
                    value = Row / value % self._convert  # 使用正则表达式替换
                self.worksheet.write(first_row, first_col, value, cell_format)
        else:
            self.worksheet.merge_range(
                first_row, first_col, last_row, last_col, value, cell_format
            )

    def _write(self, range, value, format=None):
        """写入单元格，这个函数将被放弃，由write替代"""
        if isinstance(format, str):  # 格式代码检查
            format = self._formats.get(format)
        if ":" in range and not isinstance(value, (dict, tuple, list)):
            self.worksheet.merge_range(range, value, format)
        if ":" not in range:
            if isinstance(value, (list, tuple)):
                self.worksheet.write_row(range, value, format)
            else:
                if isinstance(value, str) and value.startswith("="):
                    value = Row / value % self._convert  # 使用正则表达式替换
                self.worksheet.write(range, value, format)

    def _convert(self, match):
        return str(int(match.groups()[1]) + self.row)

    def __add__(self, val):
        """向前移动当前行"""
        self.worksheet.row += val
        return self

    def __sub__(self, val):
        """向后移动当前行"""
        self.worksheet.row -= val
        return self

    @property
    def row(self):
        """获取当前工作表的行"""
        return self.worksheet.row

    @row.setter
    def row(self, currow):
        """设置当前工作表的行"""
        self.worksheet.row = currow

    def __setitem__(self, name, val):
        """向指定行写入数据"""
        if not isinstance(val, tuple):
            val = (val,)
        if isinstance(name, str):
            match = Pattern.fullmatch(name)
            if match:
                r = list(match.groups())
                if not r[1]:
                    r[1] = str(self.row)
                rg = "".join(r[:2])
                if r[3]:
                    if not r[4]:
                        r[4] = str(self.row)
                    rg = "%s:%s%s" % (rg, r[3], r[4])
                self.write(rg, *val)
            else:
                raise Exception("单元格格式不正确")
        elif isinstance(name, int):
            self.write(self.row - 1, name, None, None, *val)
        elif isinstance(name, tuple):
            args = list(name)
            args.extend([None] * 4)
            self.write(*args[:4], *val)

    def __setattr__(self, name, val):
        """向指定行写入数据"""
        if Pattern == name:
            self[name] = val
        else:
            super().__setattr__(name, val)

    def iter_rows(self, *datas, step=1):
        """按行写入数据"""
        for d in zip(*datas):
            yield d
            self += step

    @property
    def table(self):
        return self.worksheet.table

    @convert_range_args
    def set_border(
        self,
        first_row,
        first_col,
        last_row,
        last_col,
        left=None,
        right=None,
        bottom=None,
        top=None,
        border=2,
        inner=1,
    ):
        self.worksheet._check_dimensions(first_row, first_col)
        self.worksheet._check_dimensions(last_row, last_col)
        if border:
            left = left or border
            right = right or border
            bottom = bottom or border
            top = top or border
        table = self.table

        def _replace(r, c, **kw):
            row = table[r]
            cell = row.get(c, CellBlankTuple(None))
            fmt = cell.format
            kw["top"] = top if r == first_row else inner
            kw["bottom"] = bottom if r == last_row else inner
            kw["left"] = left if c == first_col else inner
            kw["right"] = right if c == last_col else inner
            name = "".join([str(kw[name]) for name in "left top right bottom".split()])
            if fmt and hasattr(fmt, "name"):
                name = name + "-" + fmt.name
            if name not in self._formats:
                if fmt and hasattr(fmt, "properties"):
                    a = fmt.properties.copy()
                    a.update(kw)
                else:
                    a = kw
                new_fmt = self.add_format(a, name)
            else:
                new_fmt = self._formats.get(name)
            row[c] = cell._replace(format=new_fmt)

        [
            _replace(r, c)
            for r in range(first_row, last_row + 1)
            for c in range(first_col, last_col + 1)
        ]

    def add_table(self, pos="A1", sheet=None, worksheet=None, data=None, **kw):
        pos = pos.upper()
        worksheet = sheet or worksheet
        self._add_table(pos, worksheet=worksheet, data=data, **kw)

    @convert_range_args
    def _add_table(
        self,
        first_row,
        first_col,
        last_row,
        last_col,
        worksheet=None,
        header_format="header",
        data=None,
        **kwargs,
    ):
        """添加图表，如sheet为空，则使用默认的工作表"""
        self.worksheet = worksheet
        columns = kwargs.get("columns")
        if isinstance(columns, str):
            columns = columns.split(",")  # columns 支持以,分割的字符串
        if columns:
            new_columns = []
            for idx, column in enumerate(columns):
                if isinstance(column, str):
                    column = Header(column)
                elif isinstance(column, int):
                    column = Header(f"Column{column}")
                new_column = column.copy()
                width = new_column.pop("width", None)
                hidden = new_column.pop("hidden", None)
                if width or hidden:
                    self.set_columns(
                        "{0}:{0}".format(xl_col_to_name(idx + first_col)),
                        width=width,
                        options={"hidden": hidden},
                    )
                if format := new_column.get("format"):
                    if isinstance(format, str):
                        new_column["format"] = self._formats.get(format)
                if hformat := new_column.get("header_format"):
                    if isinstance(hformat, str):
                        new_column["header_format"] = self._formats.get(hformat)
                new_columns.append(new_column)
            if header_format:
                if isinstance(header_format, str):
                    header_format = self._formats.get(header_format)
                for column in new_columns:
                    column["header_format"] = header_format
            kwargs["columns"] = new_columns
            last_col = first_col + len(columns) - 1
        if data:
            if not isinstance(data, (tuple, list)):
                data = tuple(data)
            last_row = first_row + len(data)
            if kwargs.get("total_row", False):
                last_row += 1
            kwargs["data"] = data
        self.worksheet.add_table(first_row, first_col, last_row, last_col, kwargs)


def write_excel(
    filename: str | Path | None = None, formats: Optional[dict] = {}, **kw
) -> Book:
    return Book(filename, formats, **kw)


if __name__ == "__main__":
    with Book("test.xlsx") as book:
        book.worksheet = "test1"
        columns = [
            {"header": "title", "format": "currency", "width": 12},
            {"header": "name", "format": "percent"},
        ]
        data = [("a", "b"), (1, 2)]
        book.add_table("A1", data=data, columns=columns)
