# 项目：   数独程序
# 模块：   数独
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2025-03-19 08:41
from typing import List


class Item(object):
    def __init__(self, master, pos, value=None):
        self.master = master
        self.pos = pos
        self.value = value or None

    @property
    def Row(self):
        return self.pos // 9

    @property
    def Column(self):
        return self.pos % 9

    def iter_related(self, dir="row"):
        result = []
        if dir == "row" or dir == "all":
            result.extend(range(self.Row * 9, (self.Row + 1) * 9))
        if dir == "column" or dir == "all":
            result.extend(range(self.Column, 81, 9))
        if dir == "grid" or dir == "all":
            br, bc = self.Row // 3 * 3, self.Column // 3 * 3
            result.extend([(br + r) * 9 + bc + c for r in range(3) for c in range(3)])
        if dir == "all":
            result = list(sorted(set(result)))
        result.remove(self.pos)
        return result

    def SetValue(self, value):
        self.value = value
        self.available = None
        for i in self.iter_related("all"):
            item = self.master.items[i]
            if item.available:
                item.available = item.available - {value}
        print(f"第{self.Row + 1}行，第{self.Column + 1}列,设置为：{self.value}")


class SuDoku:
    items: List[Item] = []

    def __init__(self, values):
        items = []
        i = 0
        for line in filter(None, values.splitlines()):
            for k in map(int, line):
                items.append(Item(self, i, k))
                i += 1
        self.items = items
        self.init()

    def print(self):
        for k in range(9):
            for i in range(9):
                print(self.items[k * 9 + i].value or " ", end="  ")
            print()

    def init(self):
        for i in range(81):
            item = self.items[i]
            if item.value:
                item.available = set()
            else:
                item.available = set(range(1, 10)) - set(
                    self.items[x].value
                    for x in item.iter_related("all")
                    if self.items[x].value
                )

    def print_aval(self):
        for item in self.items:
            if not item.value:
                print(item.Row + 1, item.Column + 1, item.available)

    def Process(self):
        complete_flag = True
        continue_flag = False
        for i in range(81):
            item = self.items[i]
            if not item.value:
                complete_flag = False
                if len(item.available) == 1:
                    print("avail:", end="\t")
                    item.SetValue(list(item.available)[0])
                    continue_flag = True
                else:
                    # 按表格处理
                    for d in ("row", "column", "grid"):
                        a = item.available.copy()
                        for x in item.iter_related(d):
                            if not self.items[x].value:
                                a = a - self.items[x].available
                        if len(a) == 1:
                            print(f"{d}:", end="\t")
                            item.SetValue(list(a)[0])
                            continue_flag = True
                            break

        if continue_flag:
            self.Process()
        if complete_flag:
            print("已完成，结果如下：")
            self.print()
        else:
            print("逻辑推理已完成，结果如下：")
            self.print()
            for i in range(81):
                item = self.items[i]
                if not item.value:
                    item.SetValue(list(item.available)[0])
                    self.Process()
                    exit()


s = """
200300800
061200403
009740020
004026000
396078000
780003609
920010587
078000014
010007300
"""


def main():
    sudoku = SuDoku(s)
    sudoku.print()
    sudoku.Process()
    # item = sudoku.items[10]
    # sudoku.print_aval()


if __name__ == "__main__":
    main()
    print("This is a test")
