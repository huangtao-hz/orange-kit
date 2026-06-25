from typing import List, Optional

from orange import Path, arg, connect
from orange.excel import read_excel

db = connect("gkzs")
db.executescript("""
create table if not exists gktk(
    -- 题目类型 题目序号 题 目 正确答案 选 项 说 明
    lx text, --类型
    xh text, -- 序号
    tm text, -- 题目
    zqda text, -- 正确答案
    xxa text, -- 选项A
    xxb text, -- 选项A
    xxc text, -- 选项A
    xxd text, -- 选项A
    sm text )
""")


@db.tran
def load():
    path = Path("~/Downloads").find("*“国库知识”答题题库*")
    if path:
        data = read_excel(path, sheets=0, usecols="A:I", skiprows=5)
        db.load("gktk", data, fields=9, clear=True, print_result=True)


@arg("-l", "--load", action="store_true", help="导入数据")
@arg("query", nargs="*", help="检索条件")
def main(**options):
    if options.get("load"):
        load()
    querys: Optional[List] = options.get("query")
    if querys:
        query = " and ".join(f'tm like "%{x}%"' for x in querys)
        for lx, tm, zqda, *das, sm in db.fetch(
            f"select lx,tm,zqda,xxa,xxb,xxc,xxd,sm from gktk where {query}"
        ):
            print(f"{lx}： {tm} ")
            print(f"正确答案： {zqda}")
            if any(das):
                print("选项：", "\t".join(f"{a}、{b}" for a, b in zip("ABCD", das)))
            print("说明：", sm)
            print()


if __name__ == "__main__":
    main()
