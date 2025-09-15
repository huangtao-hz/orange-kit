# 项目：   标准库函数
# 模块：   数据库
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2019-01-18 19:30
# 修订：2019-03-16 21:21 增加 insertone 函数
# 修订：2021-07-11 09:15 增加 check 函数，增加 Loader 类
# 修订：2021-07-11 15:02 修订 fprint 函数，中文格式可以排列整齐的打印
# 修订：2022-07-07 10:05 db.fprint 函数，增加 sep 和 end 参数
# 修订：2022-09-04 13:56 新增 export 函数，支持将查询结果导入 excel 文件
# 修订：2025-09-06 15:06 强制类型优化，采用类的方式调用

import sqlite3
from contextlib import closing
from functools import wraps
from typing import Callable, Iterable, Optional, Union

from orange.shell import Path
from orange.utils.datetime_ import datetime
from orange.utils.htutil import tprint, wlen


def Values(count):
    """提供 sql 语句的占符  用法： f"insert into test(a,b,c) Values(3)" """
    return f"VALUES({','.join('?' * count)})"


def fix_db_name(database: Union[str, Path]) -> str:
    """修复数据库文件名"""
    ROOT = Path("~/.data")
    ROOT.ensure()
    file = str(database)
    if not file.startswith(":"):
        db = Path(database)
        if not db.root:
            db = ROOT / db
        file = str(db.with_suffix(".db"))
    return file


class LoadError(Exception):
    def __init__(self, path: Union[str, Path]):
        self.path =path

    def __str__(self):
        return f"{self.path} 已导入"


class Connection(sqlite3.Connection):
    def __init__(self, database: Union[str, Path], **kw):
        database = str(fix_db_name(database))
        super().__init__(database, **kw)

    def executefile(self, pkg: str, filename: str):
        """
        执行程序中附带的资源文件
        pkg         : 所在包的名称
        filename    : 相关于包的文件名，包括路径
        """
        from pkgutil import get_data

        data = get_data(pkg, filename)
        if data:
            return self.executescript(data.decode())

    def fetch(self, sql: str, params: list = [], multi=True):
        "执行一条 sql 语句，并取出所以查询结果"
        cur = self.execute(sql, params)
        with closing(cur):
            return cur.fetchall() if multi else cur.fetchone()

    def export(
        self, path: Union[str, Path], querysql: str, params: list = [], **kwargs
    ):
        """将查询结果导入到 Excel 文件中"""
        from orange.xlsx import write_excel

        if data := self.fetch(querysql, params):
            with write_excel(path) as book:
                book.add_table(data=data, **kwargs)

    def fetchone(self, sql: str, params: list = []):
        "执行一条 sql 语句， 并取出第一条记录"
        return self.fetch(sql, params, multi=False)

    def fetchvalue(self, sql: str, params: list = []):
        "执行一条 sql 语句，并取出第一行第一列的值"
        row = self.fetchone(sql, params)
        return row and row[0]

    def attach(self, filename: Union[str, Path], name: str):
        """附加数据库"""
        file = fix_db_name(filename)
        return self.execute(f'attach database "{file}" as {name}')

    def detach(self, name: str):
        """分离数据库"""
        return self.execute(f"detach database {name}")

    def fprint(self, sql: str, params: list = [], sep=" ", end="\n"):
        "打印查询结果"
        for row in self.fetch(sql, params):
            print(*row, sep=sep, end=end)

    print = fprint

    def printlist(self, sql: str, params: list = []):
        "以列表形式打印查询结果"
        print(*self.fetch(sql, params), sep="\n")

    def count(self, sql: str, params: list = []):
        "统计指定 sql 语句的行数"
        return self.fetchvalue(f"select count(*)from ({sql})")

    def print_count(self, sql: str, params: list = []):
        "打印指定 sql 语句的数量"
        return self.printf(
            "影响行数：{:,d}", f"select count(*)from ({sql})", print_rows=False
        )

    def print_row(self, header: Union[Iterable[str], str], sql: str, params: list = []):
        if isinstance(header, str):
            header = header.split(",")
        length = max(map(wlen, header))
        if one := self.fetchone(sql, params):
            tprint(
                zip(header, one),
                format_spec={0: f">{length}"},
                sep="    ",
                print_rows=False,
            )

    def get_ver(self, name: str):
        "获取数据的指定导入的文件的版本"
        sql = "select ver from LoadFile where name=?"
        return self.fetchvalue(sql, [name])

    def print_ver(self, name):
        "打印数据的指定导入的文件的版本"
        if ver := self.get_ver(name):
            print("数据版本", ver, sep="：")

    def fprintf(self, fmt: str, sql: str, params: list = [], print_rows: bool = True):
        tprint(self.fetch(sql, params), format_spec=fmt, print_rows=print_rows)

    printf = fprintf

    def lcheck(
        self,
        name: str,
        path: Union[str, Path],
        mtime: Union[datetime, str, Iterable, None] = None,
        ver: Optional[str] = None,
    ):
        """
        检查文件是否重复导入，一般应与load函数或 Loader.load 放在同一个事务内执行
        """
        fmt = "%F %H:%M:%S"
        if isinstance(mtime, (tuple, list)):
            mtime = datetime(*mtime) % fmt
        else:
            mtime = datetime(mtime) % fmt
        checkSQL = (
            "select count(name) from loadfile where name=? and path=? and mtime>=?"
        )
        doneSQL = "insert or replace into loadfile values(?,?,?,?)"
        try:
            if self.fetchvalue(checkSQL, [name, str(path), mtime]):
                raise LoadError(path)
        except sqlite3.OperationalError:
            self.executescript(
                "create table if not exists loadfile("
                "name	text,"
                "path	text,"
                "mtime	text,"
                "ver		text,"
                "primary key(name,path)"
                ");"
            )
        self.execute(doneSQL, [name, str(path), mtime, ver])

    def load(
        self,
        table: str,
        fields: Union[list, int, str],
        data: Iterable[list],
        method: str = "insert",
        clear: bool = True,
        print_result: bool = False,
    ) -> sqlite3.Cursor:
        """
        将入数据导入数据库
        table:  表名
        fields: 导入字段列表，格式为：用逗号分割的字符串；tuple 或 list ；或者为字段数量
        data:   装入的数据
        method: 装入方式，可以为:insert、replace or ignore
        clear:  是否清空数据库表
        """
        if clear:
            self.execute(f"delete from {table}")
        if method == "replace":
            method = "insert or replace"
        elif method == "ignore":
            method = "insert or ignore"
        if isinstance(fields, int):
            sql = f"{method} into {table} {Values(fields)}"
        elif isinstance(fields, str):
            fieldcount = len(fields.split(","))
            sql = f"{method} into {table}({fields}) {Values(fieldcount)}"
        elif isinstance(fields, (tuple, list)):
            sql = f"{method} into {table}({','.join(fields)}) {Values(len(fields))}"
        else:
            raise Exception("param fields is wrong")
        result = self.executemany(sql, data)
        if print_result:
            print(f"导入数量：{result.rowcount:,d}")
        return result

    def update(
        self,
        table: str,
        keys: Union[str,Iterable[str]],
        values: Union[str,Iterable[str]],
        data: Iterable,
        print_result: bool = False,
    ) -> int:
        """
        更新数据库表，参数说明：
        table :数据库表
        kes:    键值
        values: 数据列表，应与 data 每一行的列数一致
        data:   需要更新的数据
        print_result: 打印更新的数量
        """

        def conv(fields: Union[str,Iterable[str]]) -> Iterable[str]:
            if isinstance(fields, str):
                _fields = fields.split(",")
                if _fields:
                    return _fields
            return fields

        keys = conv(keys)
        values = conv(values)
        upvalues = ",".join(f"{x}=:{x}" for x in set(values) - set(keys))
        keys = " and ".join(f"{x}=:{x}" for x in keys)
        sql = f"update {table} set {upvalues} where {keys}"
        count = 0
        for row in data:
            r = self.execute(sql, dict(zip(values, row)))
            count += r.rowcount
        if print_result:
            print(f"更新数据：{count:,d} 条")
        return count

    def tran(self, func:Callable):
        """装饰器，将一下函数里所有的操作封装成一个事务。使用方法如下：
        @db.tran
        def abc():
            execute(sql1)
            execute(sql2)
        """

        @wraps(func)
        def _(*args, **kw):
            with self:
                func(*args, **kw)

        return _


def connect(db: Union[str, Path], **kw) -> Connection:
    return Connection(db, **kw)
