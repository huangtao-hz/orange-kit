# 项目：标准工具库
# 模块：正则表达式
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-09-30 17:18
# 修改：2019-01-29 15:19 采用 reduce 来更新参数


import re
from functools import reduce
from operator import attrgetter, or_

_FLAGS = "TILMSUXA"

__all__ = "R", "convert_cls_name", "extract"


class _R(type):
    """Regex类的元类，在使用R/pattern时被调用，调用生成R类。
    其中pattern可以是str，也可以是list或tuple。
    如pattern为list或tuple，则其格式为 pattern,flag。
    flag的格式可以是"AILUMSX"或是整数。"""

    __slots__ = ()

    def __truediv__(self, pattern):
        if not isinstance(pattern, (list, tuple)):
            pattern = (pattern,)
        return R(*pattern)


class R(metaclass=_R):
    """Regex类，主要有以下功能。
    1、生成
      r=R/pattern 或者 r=R/(pattern,flag)
    2、拆分
      for substr in R/pattern|str:
          print(substr)
    3、查找所有匹配记录
      for match in R/pattern//str:
          print(match.group())
    4、对Regex类进行操作
       可以使用match,search,findall,finditer函数进行操作。
       if (R/pattern).match(str):
          pass

    R/pattern 对象操作指南：
    1、判断是否匹配。
      if R/pattern/str:
         pass
    2、查询所有匹配记录。
      for substr in R/pattern/str:
         print(substr)
    3、批量替换
      s=R/pattern/str%repl
    """

    __slots__ = ("_regex",)

    def __init__(self, pattern, flag=0):
        """初始化，生成模板。"""
        if flag and isinstance(flag, str):
            flag = reduce(or_, attrgetter(*flag.upper())(re))
        self._regex = re.compile(pattern, flag)

    def __eq__(self, s):
        """是否完全匹配。"""
        return self._regex.fullmatch(s)

    def __mod__(self, s):
        """搜索匹配的记录"""
        return self._regex.search(s)

    def __truediv__(self, s):
        """返回正则表达式的操作对象"""
        return RegOperation(self._regex, s)

    def __or__(self, s):
        """对指定字符串进行拆分。"""
        return self._regex.split(s)

    def __floordiv__(self, s):
        """查找所有匹配的记录。"""
        yield from self._regex.finditer(s)

    def __getattr__(self, name):
        """对Regex对象进行操作，如match,search,findall,finditer等。"""
        return getattr(self._regex, name)

    def extract(self, s: str, group: int = 0) -> str:
        "从指定的字符串中提取符合条件的字符串，其中 group 为分组，默认提取全部"
        result = self.search(s)
        return result and result.group(group)


class RegOperation:
    """正则表达式操作对象，具有以下功能：
    1、判断是否匹配。
      if R/pattern/str:
         pass
    2、查询所有匹配记录。
      for substr in R/pattern/str:
         print(substr)
    3、批量替换
      s=R/pattern/str%repl
    """

    __slots__ = "_regex", "_search"

    def __init__(self, regex, search):
        """对象初始化，由R对象自动调用。"""
        self._regex = regex
        self._search = search

    def __bool__(self):
        """判断是否匹配。"""
        return bool(self._regex.search(self._search))

    def __iter__(self):
        """查找所有匹配项。"""
        yield from self._regex.findall(self._search)

    def __mod__(self, repl):
        """字符串替换。"""
        if isinstance(repl, (list, tuple)):
            repl, count = repl
        else:
            count = 0
        return self._regex.sub(repl, self._search, count)


# 将类名由 TestCase 格式转换为 test_case
def convert_cls_name(name):
    return "_".join([x.lower() for x in R / "[A-Z][a-z0-9]*" / name])


def extract(s, pattern, group=0):
    if isinstance(pattern, str):
        pattern = R / pattern
    result = pattern.search(s)
    return result and result.group(group)
