# 项目：   数据定义类
# 模块：   数据定义
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2025-01-23 15:54

from dataclasses import dataclass
from operator import itemgetter
from typing import Callable, Iterable, Optional, Dict

from orange.shell import Path
from orange.utils.htutil import classproperty

from .sqlite import Connection
from .xlsx import Book, Header


def convdata(data: Iterable, convfunc: Callable[[list], list]) -> Iterable:
    """
    对制定的数据进行转换，参数说明：
    data: 格式为 [][]Any
    convfunc: 按行处理，
    """
    yield from filter(None, map(convfunc, data))


@dataclass
class Column:
    header: str = ""  # 标题，Excel 使用
    _type: str = "text"  # 数据类型，数据库定义
    is_pk: bool = False  # 是否主键，数据库定义
    width: float = 0  # 宽度，Excel 使用
    format: str = ""  # 格式，Excel 使用
    hidden: bool = False  # 是否隐藏，Excel 使用
    total_string: str = ""  # 汇总列，Excel 使用
    total_function: str = ""  # 汇总函数，Excel 使用
    formula: str = ""  # 公式，Excel使用
    has_index: bool = False  # 是否建立索引

    def field(self, name):
        "返回字段的数据库字段定义"
        _type = self._type + ","
        bz = f"-- {self.header}" if self.header else ""
        return f"    {name:15s}{_type:10s}  {bz}"

    @property
    def Header(self):
        "字段的Excel表头"
        return Header(
            self.header,
            self.width,
            self.format,
            hidden=self.hidden,
            total_string=self.total_string,
            total_function=self.total_function,
            formula=self.formula,
        )


class Table(object):
    tablename = ""  # 表名

    @classproperty
    def Columns(cls) -> Dict[str, Column]:
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, Column)}

    @classmethod
    def create_table(cls, db: Connection, print_sql: bool = False):
        "创建数据库表"
        if not (cls.tablename and isinstance(cls.tablename, str)):
            raise Exception("tablename 未定义")
        Columns = cls.Columns
        if not Columns:
            raise Exception("Columns 未定义")
        fields = [c.field(name) for name, c in Columns.items()]
        pks = [name for name, c in Columns.items() if c.is_pk]
        if not pks:
            fields[-1] = fields[-1].replace(",", "", 1)
        else:
            fields.append(f"    primary key({','.join(pks)})")
        sql = (
            f"create table if not exists {cls.tablename}(\n"
            + "\n".join(fields)
            + "\n);"
        )
        if print_sql:
            print(sql)
        if db:
            db.execute(sql)
        else:
            print("数据库未定义")
        # 创建索引
        for name, column in Columns.items():
            if column.has_index:
                db.execute(
                    f"create index if not exists {cls.tablename}_{name} on {cls.tablename}({name})"
                )

    @classmethod
    def load(
        cls,
        db: Connection,
        data: Iterable,
        convfunc: Optional[Callable[[list], list]] = None,
        path: Optional[Path] = None,
        method: str = "insert",
        loadcheck: bool = False,
        clear: bool = False,
        print_result: bool = True,
    ):
        "导入数据"

        with db:
            if loadcheck and path:
                db.lcheck(cls.tablename, path, path.mtime)
            if convfunc:
                data = convdata(data, convfunc)
            db.load(
                cls.tablename,
                len(cls.Columns),
                data,
                method=method,
                clear=clear,
                print_result=print_result,
            )

    @classmethod
    def export(
        cls,
        db: Connection,
        path: Optional[Path] = None,
        book: Optional[Book] = None,
        sheetname: Optional[str] = None,
        sql: Optional[str] = None,
        fields: Optional[str] = None,
        convfunc: Optional[Callable] = None,
        **kw,
    ):
        "导出数据"
        from .xlsx import write_excel

        if path is not None:
            with write_excel(path) as book:
                cls.export(
                    db=db,
                    book=book,
                    sheetname=sheetname,
                    sql=sql,
                    fields=fields,
                    convfunc=convfunc,
                    **kw,
                )
        else:
            if not sql:  # 生成默认的 sql 语句
                sql = f"select {fields or '*'} from {cls.tablename}"
            data = db.fetch(sql)
            if convfunc:
                data = convfunc(data)  # 如果送入转换函数，进行数据转换
            if not sheetname:
                sheetname = cls.tablename
            Columns = cls.Columns
            if fields:
                Headers = [Columns[f].Header for f in fields.split(",")]
            else:
                Headers = [f.Header for f in cls.Columns.values()]
            if book:
                book.add_table(sheet=sheetname, data=data, columns=Headers, **kw)


includer = itemgetter


def exculder(*items):
    "对数据处理，排除掉制定的列"

    def _(row):
        length = len(row)
        exclude_items = set(x if x >= 0 else x + length for x in items)
        return [item for i, item in enumerate(row) if i not in exclude_items]

    return _


def slicer(*args):
    """
    对数据进行切片，参数同 slice 函数，可以为：
    (stop) 或
    (start , stop [ , step ] )
    """
    s = slice(*args)

    def _(row):
        return row[s]

    return _
