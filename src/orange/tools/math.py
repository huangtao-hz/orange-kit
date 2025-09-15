# 项目：生成算数表
# 作者：黄涛
# 创建：2018-9-17

from random import randint
from orange import arg


def create_tiku(type_='+', limit=100):
    if '+' in type_ or '-' in type_:
        return [(a, b)for a in range(limit)for b in range(limit+1-a)]
    elif '*' in type_ or '/' in type_:
        return [(a, b) for a in range(1, limit+1) for b in range(a, limit+1)]


@arg('-t', '--type', dest='type_', nargs='?', help='题目类型')
@arg('-l', '--limit', nargs='?', help='限值')
@arg('-c', '--count', nargs='?', help='题目数量')
def main(type_='+', limit=100, count=88):
    type_ = type_ or "+-"
    limit = limit and int(limit) or 100
    count = count and int(count) or 88
    tiku = create_tiku(type_, limit=limit)
    total = len(tiku)
    if count > total:
        raise Exception('题目总数大于题库总数')

    result = set()
    tk_count = len(tiku)-1
    while len(result) < count:
        k = randint(0, tk_count)
        result.add(tiku[k])

    if type_ == '+-':
        for a, b in result:
            opt = randint(0, 1)
            if opt:
                print(f'{a+b:2d} - {b:2d} =')
            else:
                print(f'{a:2d} + {b:2d} =')
    elif type_ == '*/':
        for a,b in result:
            opt=randint(2,3)
            if opt==2:
                print(f'{a:2d} * {b:2d} =')
            else:
                print(f'{a*b:2d} / {b:2d} =')

