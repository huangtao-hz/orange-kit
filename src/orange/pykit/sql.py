#!/usr/bin/env python3
# 项目：标准库
# 模块：执行 sql 命令
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2015-05-20 15:32
# 修订：2016-9-6 将其迁移至orange 库，并移除对stdlib 的依赖

from orange import arg
from orange.sqlite import connect


@arg("-d", "--db", dest="db", default=":memory:", nargs="?", help="连接的数据库")
@arg("-l", "--list", action="store_true", help="显示数据库表列表")
@arg(
    "-s",
    "--show",
    dest="tables",
    metavar="table",
    nargs="*",
    help="显示创建语句",
)
@arg("sql", nargs="*", help="执行的 sql 语句")
def execsql(db: str, list: bool, tables: list[str], sql: str):
    _db = connect(db)
    if sql:
        sql = " ".join(sql)
        with _db:
            _db.print(sql)
    elif list:
        _db.print('select type,name from sqlite_master where type in ("table","view")')
    elif tables:
        for table in tables:
            _db.print("select sql from sqlite_master where name=?", [table])
