from typing import Optional

from orange import Path


def conv(row:list)->Optional[list]:
    row=list(row)
    row[0]=row[0]+'hello'
    if row[0]<'8100':
        return row

path=Path('~/Documents').find('*新柜面存量交易迁移*.xls?')
print(path)
if path:
    data=path.read_sheet(sheet='全量表',start_row=1)
    print(*data,sep='\n')
