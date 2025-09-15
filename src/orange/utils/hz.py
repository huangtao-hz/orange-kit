# 项目：标准库
# 模块：序数
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2019-01-23 08:54

ORDINALNUMBER = '零一二三四五六七八九'


class Ordinal(object):
    def __init__(self, start=1, prefix='', suffix='', capital=False, step=1):
        self._xh = start
        self.prefix = prefix
        self.suffix = suffix
        self._capital = capital
        self._step = step

    def __call__(self):
        s = str(self)
        self._xh += self._step
        return s

    def __iter__(self):
        return self

    __next__ = __call__

    @property
    def xh(self):
        return str(self)

    @property
    def capital(self):
        bw, sw, gw = map(int, '%03d' % self._xh)
        b, g = ORDINALNUMBER[bw] + \
            '百' if bw else "", ORDINALNUMBER[gw]if gw else ""
        if sw:
            s = "十" if bw == 0 and sw == 1 else ORDINALNUMBER[sw]+"十"
        else:
            s = "零" if bw and gw else ""
        return "".join((b, s, g))

    def __str__(self):
        return "".join([self.prefix, self.capital if self._capital else str(self._xh), self.suffix])
