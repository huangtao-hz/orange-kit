"""
from orange.sqlite import connect
from orange.table import Column, Table


class Test(Table):
    tablename='test'
    name=Column("姓名",_type='text',is_pk=True)
    bj=Column('班级',_type='text',has_index=True)

db=connect(':memory:')

#Test.create_table(db)
"""

from os import open


def hello():
    with open("a.txt") as f:
        f.write("hello")
        print("hello world.")
