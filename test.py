from orange.utils.sqlite import connect
from orange.utils.table import Column, Table


class Test(Table):
    tablename='test'
    name=Column("姓名",_type='text',is_pk=True)
    bj=Column('班级',_type='text',has_index=True)

db=connect(':memory:')

Test.create_table(db)
