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
# 修订：2025-11-19 19:49 调整为两个类

from functools import partial
from pkgutil import get_data
from typing import Dict, Optional, Union, Any, Iterable
from orange import Path
from orange.sqlite import Connection

from toml import loads
from xlsxwriter import Workbook
from xlsxwriter.worksheet import (
    Format,
    Worksheet,
)


def colname_to_col(col_str: str) -> int:
    "将列名转换为坐标"
    expn, col = 0, 0
    for char in reversed(col_str):
        col += (ord(char) - ord("A") + 1) * (26**expn)
        expn += 1
    return col - 1


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

# 样式属性的别名
sytle_alias = {
    "num_fmt": "num_format",
    "halign": "align",
    "wrap_text": "text_wrap",
}
# 预置数字样式
num_formats = {
    "Number": "#,##0",
    "Currency": "#,##0.00",
    "Percent": "0.00%",
    "Time": "hh:mm:ss",
    "Date": "yyyy-mm-dd",
}


class Sheet(Worksheet):
    "工作表的类"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.cur_row = 0
        self.workbook: Optional[Book] = None

    def set_columns(
        self,
        columns: str,
        width: Optional[float] = None,
        cell_format: Union[str, Format, None] = None,
        options: Optional[Dict] = None,
    ):
        """设置当前工作表的列属性，允许同时设置多个，使用方法如下：
        book.set_columns('A:C,E:D,G:H',width=12)
        """
        options = options or {}
        if cell_format is not None and isinstance(cell_format, str):
            cell_format = self.get_format(cell_format)
        for column in columns.split(","):
            cols = list(map(colname_to_col, column.split(":")))
            assert 1 <= len(cols) <= 2
            # self.col_info[col] = [width, cell_format, hidden, level, collapsed, False]
            for col in range(cols[0], cols[-1] + 1):
                colproperty = self.col_info.get(col, None)
                if colproperty:
                    if width:
                        colproperty[0] = width
                    if cell_format:
                        colproperty[1] = cell_format
                    if "hidden" in options:
                        colproperty[2] = options.get("hidden")
                else:
                    self.set_column(col, col, width, cell_format, options)

    def set_widths(self, widths: Dict[str, float]):
        '设置列宽，widths :dict[columns,width],其中，columns是： "A:B,C:D,G"'
        for columns, width in widths.items():
            self.set_columns(columns, width=width)

    def set_formats(self, formats: Dict[str, str]):
        "设置列样式"
        for columns, fmt in formats.items():
            self.set_columns(columns, cell_format=fmt)

    def set_hidden(self, columns: str):
        "设置隐藏列"
        options = {"hidden": True}
        self.set_columns(columns, options=options)

    def get_format(self, cell_format: Union[str, Format, None]) -> Optional[Format]:
        "根据名称获取样式"
        assert self.workbook is not None
        if isinstance(cell_format, str):
            cell_format = self.workbook.get_format(cell_format)
        return cell_format

    def addRow(
        self,
        col: str,
        row_data: Iterable[Any],
        cell_format: Union[str, Format, None] = None,
    ):
        "添加一行数据"
        assert self.workbook is not None
        self.write_row(
            self.cur_row, colname_to_col(col), row_data, self.get_format(cell_format)
        )
        self.cur_row += 1

    def addHeader(self, col: str, header: Union[Iterable[str], str]):
        "添加一个小标题"
        if isinstance(header, str):
            header = header.split(",")
        self.addRow(col, header, "Header")

    def addTable(self, start_col: str, data: Iterable[Any], **kwargs):
        "添加表格"
        first_row, first_col = self.cur_row, colname_to_col(start_col)
        total_row = False
        columns = kwargs.get("columns")
        if not columns and "header" in kwargs:
            columns = [Header(header) for header in kwargs.pop("header").split(",")]
        if not columns:
            raise Exception("添加表格，必须包含 header 或 columns ")
        for i in range(len(columns)):
            column = columns[i]
            if "header_format" not in column:
                column["header_format"] = "Header"
            for fmt in ("format", "header_format", "total_format"):
                if fmt in column:
                    column[fmt] = self.get_format(column[fmt])
            if not total_row or any(
                t in columns for t in ("total_string", "total_function")
            ):
                total_row = True
        kwargs["columns"] = columns
        last_col = first_col + len(columns) - 1
        if not isinstance(data, (tuple, list)):
            data = tuple(data)
        last_row = first_row + len(data)
        if total_row:
            kwargs["total_row"] = True
            last_row += 1
        kwargs["data"] = data
        print(kwargs)
        super().add_table(first_row, first_col, last_row, last_col, kwargs)
        self.cur_row += last_row + 2


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
        self._formats: Dict[str, Format] = {}
        if formats:
            self.add_formats(formats)
        self.add_pkg_formats("orange", "xlwt/styles.toml")

    def get_format(self, name: str) -> Optional[Format]:
        "根据名称获取样式"
        return self._formats.get(name, None)

    def add_named_format(self, properties, name=None):
        "添加带名字的样式"
        for k, v in sytle_alias.items():
            if k in properties:
                properties[v] = properties.pop(k)
        num_format = properties.get("num_format", None)
        if num_format:
            properties["num_format"] = num_formats.get(num_format, num_format)
        if "valign" in properties and properties["valign"] not in ("top", "bottom"):
            properties["valign"] = f"v{properties['valign']}"
        _format = super().add_format(properties)
        if name:
            self._formats[name] = _format
        return _format

    def add_formats(self, properties):
        "添加多种样式"
        for name, property in properties.items():
            self.add_named_format(property, name)

    def add_pkg_formats(self, pkg: str, resource: str):
        "添加包资源中的样式表"
        s = get_data(pkg, resource)
        if s:
            styles = loads(s.decode())
            if styles:
                for style in styles["style"]:
                    name = style.pop("name", None)
                    self.add_named_format(style, name)

    def add_sheet(self, name: str) -> Sheet:
        """添加工作表"""
        worksheet = self.sheetnames.get(name, None)
        if not worksheet:
            worksheet = self.add_worksheet(name, Sheet)
            assert isinstance(worksheet, Sheet)
            worksheet.workbook = self
        return worksheet


def export_xlsx(db: Connection, table: str, xlsx_file: str):
    """
    for file in files.split(","):
        b = get_data(pkg, file)
        if b:
            d = loads(b.decode())
            print(d)
    """
    book = Book(str(Path(xlsx_file)))
    x = loads(table)
    sheet = book.add_sheet(x.pop("sheet"))
    if "widths" in x:
        sheet.set_widths(x["widths"])
    if "formats" in x:
        for col, fmt in x["formats"].items():
            sheet.set_columns(col, cell_format=fmt)
    data = db.fetch(x.pop("query"))
    sheet.addTable(start_col=x["start_col"], data=data, header=x["header"])
    print(x)
    book.close()
    print(f"保存文件：{xlsx_file} 成功")
