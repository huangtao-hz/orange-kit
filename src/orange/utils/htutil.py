# 项目：标准库函数
# 模块：运行库
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-04-13 20:46
# 修改：2018-09-09 新增 tprint 功能
# 修改：2018-09-12 10:19 新增 shell、cformat、tprint 功能
# 修订：2021-06-14 17:25 新增 get_md5 函数

import os
import uuid
import warnings
from functools import wraps
from hashlib import md5
from itertools import islice
from typing import Iterable

from .datetime_ import datetime
from .regex import R


def get_id():
    return uuid.uuid1().hex.upper()


def suppress(func):
    @wraps(func)
    def _(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)

    return _


def get_md5(s: str) -> str:
    "获取指定字符串的md5编码"
    md = md5(s.encode("utf8"))
    return md.hexdigest()


def timeit(func):
    @wraps(func)
    def _(*args, **kw):
        start_time = datetime.now()
        print("开始时间：", start_time % ("%T.%f"))
        result = func(*args, **kw)
        print("耗时    ：", datetime.now() - start_time)
        return result

    return _


def first(iterable):
    return next(iter(iterable))


def last(iterable):
    for item in iterable:
        pass
    return item


def _any(func, iterable):
    return any(map(func, iterable))


def _all(func, iterable):
    return all(map(func, iterable))


def deprecate(func):
    """进行废弃声明，使用方法：

    @deprecate(new_func)
    def depr_func(*arg,**kw):
        pass
    """
    func = func.__name__ if hasattr(func, "__name__") else func

    def _(fn):
        @wraps(fn)
        def new_func(*args, **kw):
            warnings.warn(
                "%s will be deprecated, Please use %s replaced!"
                % (fn.__name__, func),
                DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kw)

        return new_func

    return _


def deprecation(func, replace=""):
    """DeprecationWarning"""
    message = "%s 已被弃用" % (func)
    if replace:
        message += "，请使用 %s 替代" % (replace)
    warnings.warn(message, DeprecationWarning, stacklevel=2)


_Digit = R / r"\d+"


def cformat(value, format_spec=""):
    """对字符串进行格式化，
    解决设定宽度后，汉字无法对齐的问题"""
    if isinstance(value, str) and _Digit / format_spec:
        d = int(tuple(_Digit / format_spec)[0]) - sum(
            1 for x in value if ord(x) > 127
        )
        format_spec = _Digit / format_spec % str(d)
    return format(value, format_spec)


@deprecate("cformat")
def cstr(arg, width=None, align="left"):
    """
    用于转换成字符串，增加如下功能：
    width:总宽度
    align:left:左对齐，right:右对齐，center:居中
    """
    s = str(arg)
    if width:
        align = align.lower()
        s = s.strip()
        x = width - wlen(s)
        if x > 0:
            if align == "right":
                s = " " * x + s
            elif align == "left":
                s += " " * x
            else:
                left = x // 2
                right = x - left
                s = " " * left + s + " " * right
    return s


def tprint(data, format_spec={}, sep=" ", print_rows: bool = True):
    """按行格式化打印，可以指定每列的宽度和对齐方式。
    其中格式为： <23，前面是对齐方式，右边是宽度。中间用,隔开，如"^23,>19"
    左对齐：     <
    居中对齐：   ^
    右对齐：     > 可省略
    """
    count = 0
    if isinstance(format_spec, (tuple, list)):
        for row in data:
            x = sep.join(cformat(k, f) for k, f in zip(row, format_spec))
            count += 1
            print(x)
    elif isinstance(format_spec, dict):
        for row in data:
            x = sep.join(
                cformat(k, format_spec.get(i, "")) for i, k in enumerate(row)
            )
            count += 1
            print(x)
    elif isinstance(format_spec, str):
        import re

        pattern = re.compile(r"\{(\d+)?(?:\:(.*?))?\}")
        for row in data:
            i = 0

            def repl(m):
                nonlocal i
                idx = int(m.group(1)) if m.group(1) else i
                i += 1
                if fmt := m.group(2):
                    return cformat(row[idx], fmt)
                else:
                    return str(row[idx])

            count += 1
            print(pattern.sub(repl, format_spec))
    if print_rows:
        print(f"共 {count:,d} 行")


def desensitize(
    s: str, start: int = 0, stop: int = 0, width: int = 0, chr: str = "*"
) -> str:
    """对指定的数据进行脱敏处理'
    s:     需要脱敏的字符串
    start: 脱敏的起始位置，可以为负数
    stop:  脱敏的终止位置，可以为负数
    width: 脱敏字符串的长度，stop 未设置时使用
    chr:   替代字符，脱敏时替代的安符
    """
    parts = []
    if start:
        parts.append(s[:start])
    if not stop and width:
        stop = start + width
    if stop:
        parts.extend([chr * len(s[start:stop]), s[stop:]])
    else:
        parts.append(chr * len(s[start:]))
    return "".join(parts)


class classproperty:
    """类属性，用法：
    class A:
        @classproperty
        def name(cls):
              return cls.__name__

    A.name
    A().name
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, kclass):
        return self.getter(kclass)


class cachedproperty:
    """类属性，用法：
    class A:
        @classproperty
        def name(cls):
              return cls.__name__

    A.name
    A().name
    """

    def __init__(self, getter):
        self.getter = getter
        self.cache = {}

    def __get__(self, instance, kclass):
        if kclass not in self.cache:
            self.cache[kclass] = self.getter(kclass)
        return self.cache[kclass]


class _Shell:
    """执行系统命令，
    使用方法：
    1.直接在终端上执行命令，并显示结果。
      shell > 'dir'
      注： result = shell >'dir'
          result 为系统返回的结果，一般 0 为正确执行
    2.获取执行结果。
      result = shell('dir')
      这里返回的是 dir 执行的输出
    """

    def __gt__(self, cmd):
        return os.system(cmd)

    def __call__(self, cmd, input=None):
        mode = "w" if input else "r"
        with os.popen(cmd, mode) as f:
            if input:
                if isinstance(input, (tuple, list)):
                    input = "\n".join(input)
                f.write(input)
            else:
                return f.read().splitlines()


shell = _Shell()


def run_cmd(cmd, *args, **options):
    """
    执行 cmd 命令，并带 params 以及 options 参数
    """
    params = []
    for k, v in options.items():
        if len(k) == 1:
            params.append(f"-{k}")
        else:
            params.append(f"--{k}")
        if v:
            params.append(v)
    params = [cmd, *args, *params]
    cmd = " ".join([f'"{x}"' if " " in x else str(x) for x in params])
    return shell > cmd


@deprecate("shell")
def read_shell(cmd):
    """
    执行系统命令，并将执行命令的结果通过管道读取。
    """
    with os.popen(cmd) as fn:
        k = fn.read()
    return k.splitlines()


@deprecate("shell")
def write_shell(cmd, lines):
    """
    执行系统命令，将指定的文通过管道向该程序输入。
    """
    with os.popen(cmd, "w") as fn:
        if isinstance(lines, str):
            fn.write(lines)
        elif isinstance(lines, (tuple, list)):
            [fn.write("%s\n" % (x)) for x in lines]


@deprecate("shell")
def exec_shell(cmd):
    """
    执行系统命令。
    """
    # deprecation('exec_shell', 'shell')
    return os.system(cmd)


def wlen(s):
    """
    用于统计字符串的显示宽度，一个汉字或双字节的标点占两个位，
    单字节的字符占一个字节。
    """
    return len(s.encode("gbk", errors="ignore"))


_des = None


def __get_des():
    from .pyDes import PAD_PKCS5, des

    global _des
    if _des is None:
        _des = des(key="huangtao", padmode=PAD_PKCS5)
    return _des


def encrypt(pwd):
    """
    可逆加密程序。
    """
    b = __get_des().encrypt(pwd)
    return "".join(["%02X" % (x) for x in b])


def decrypt(code):
    """
    解密程序。
    """
    b = __get_des().decrypt(bytes.fromhex(code))
    return b.decode("utf8")


generator = type(x for x in "hello world.")


def limit(data: Iterable, count: int = 100):
    return islice(data, count)


def split(data: Iterable, size: int = 1000) -> Iterable:
    """拆分数据，其中datas应为list,size为每批数据的数量"""
    data = iter(data)
    while row := list(islice(data, size)):
        yield row


def groupby(data: Iterable, key) -> Iterable:
    "对数据进行分组，key 可以为列数，也可以是函数"
    from collections import defaultdict

    result = defaultdict(lambda: [])
    if callable(key):
        for row in data:
            result[key(row)].append(row)
    elif isinstance(key, int):
        for row in data:
            result[row[key]].append(row)

    return result.items()
