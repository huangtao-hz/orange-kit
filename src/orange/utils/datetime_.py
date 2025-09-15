# 项目：标准库函数
# 模块：时间模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2015-09-17 13:24
# 修改：2016-03-12 18:53
# 修改：2016-09-06 增加 ONEDAY,ONESECOND
# 修改：2016-11-19 将datetime 修改为按类实现
# 修改：2019-04-08 13:43 支持 YYYYMMDD 格式的日期
# 修订：2022-03-19 21:08 新增 date 函数，支持将日期格式转换为 YYYY-MM-DD 格式字符串


import datetime as dt
import time as _time

from orange.utils.regex import R

__all__ = (
    "UTC",
    "LOCAL",
    "now",
    "datetime",
    "FixedOffset",
    "ONEDAY",
    "ONESECOND",
    "date_add",
    "LTZ",
)
ZERO = dt.timedelta(0)
ONEDAY = dt.timedelta(days=1)
ONESECOND = dt.timedelta(seconds=1)
_Pattern = R / r"%."
_MONTHS = " ,一,二,三,四,五,六,七,八,九,十,十一,十二".split(",")

# A class building tzinfo objects for fixed-offset time zones.
# Note that FixedOffset(0, "UTC") is a different way to build a
# UTC tzinfo object.


class FixedOffset(dt.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = dt.timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        timezone = self.__offset.total_seconds() // 60
        return "UTC%+i:%02i" % (divmod(timezone, 60)) if timezone else "UTC"


UTC = FixedOffset(0, "UTC")

# A class capturing the platform's idea of local time.

STDOFFSET = dt.timedelta(seconds=-_time.timezone)
if _time.daylight:
    DSTOFFSET = dt.timedelta(seconds=-_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(dt.tzinfo):
    __slots__ = ()

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.weekday(),
            0,
            0,
        )
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

    def __repr__(self):
        offset = STDOFFSET.total_seconds() // 60
        return "UTC%+i:%02i" % (divmod(offset, 60))


LTZ = LocalTimezone()
LOCAL = LTZ


class datetime(dt.datetime):
    __slots__ = ()
    """日期类，支持从字符串转换"""

    def __new__(
        cls,
        year,
        month=0,
        day=0,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    ):
        tzinfo = tzinfo or LTZ
        if all([year, month, day]):
            return super().__new__(
                cls, year, month, day, hour, minute, second, microsecond, tzinfo
            )
        else:
            if isinstance(year, datetime):
                return year
            elif isinstance(year, (dt.datetime, dt.time)):
                """
                如果是DATETIME或TIME类型，检查是否有TZINFO信息，
                如无，则设为LTZ，否则直接返回
                """
                args = list(year.timetuple()[:6])
                if year.tzinfo:
                    tzinfo = year.tzinfo
                args.extend([year.microsecond, tzinfo])
            elif isinstance(year, str):
                """将字符串转换为DATETIME类型"""
                if R / r"\d{8}" == year:
                    args = [int(x) for x in (year[:4], year[4:6], year[6:])]
                else:
                    args = [int(x) for x in R / r"\d+" / year]
            elif isinstance(year, (int, float)):
                """将整数或浮点数转换成日期类型
                如果小于100000，则按EXCEL的格式转换；
                否则按UNIX TIMESTAMP 来转换"""
                if year < 100000:
                    from xlrd3.xldate import xldate_as_datetime

                    dd = cls(xldate_as_datetime(year, None))
                else:
                    dd = cls.fromtimestamp(year)
                return dd
            if len(args) == 8:
                tzinfo = args.pop(7)
        return super().__new__(cls, *args, tzinfo=tzinfo)

    def add(self, years=0, months=0, **kw):
        """增加日期，返回一个新的日期实例"""
        year, month = self.timetuple()[:2]
        year, month = divmod((year + years) * 12 + month + months - 1, 12)
        try:
            date = self.replace(year=year, month=month + 1)
        except Exception:
            # 加上年或月之后，如果没有对应的日，则以最后一天为准
            date = self.replace(year=year, month=month + 2, day=1) - 1
        return date + dt.timedelta(**kw)

    def __add__(self, days):
        """增加日期，支持整数型"""
        if isinstance(days, int):
            days = dt.timedelta(days=days)
        return datetime(super().__add__(days))

    def __sub__(self, days):
        """减少日期，支持整数类型"""
        if isinstance(days, (dt.datetime, dt.time)):
            return super().__sub__(days)
        return self.__add__(-days)

    @property
    def first_day_of_year(self):
        return datetime(self.year, 1, 1, tzinfo=LTZ)

    @property
    def last_day_of_year(self):
        return datetime(self.year, 12, 31, tzinfo=LTZ)

    @property
    def first_day_of_quartor(self):
        month = (self.quartor - 1) * 3 + 1
        return datetime(self.year, month, 1, tzinfo=LTZ)

    @property
    def last_day_of_quartor(self):
        return self.first_day_of_quartor.add(months=3) - 1

    @property
    def first_day_of_month(self):
        """当月第一天"""
        return self.replace(day=1)

    @property
    def last_day_of_month(self):
        """当月最后一天"""
        return self.add(months=1).first_day_of_month - 1

    @property
    def is_weekend(self):
        """是否为周末"""
        return self.weekday() > 4

    @property
    def quartor(self):
        """当前的季度，从1开始"""
        return (self.month - 1) // 3 + 1

    def format(self, fmt):
        """格式化"""
        d = {
            "%q": str(self.quartor),
            "%Q": f"{self.year}-{self.quartor}",
            "%x": f"{self.year}年{self.month}月{self.day}日",
            "%a": "星期" + "一二三四五六日"[self.weekday()],
            "%b": _MONTHS[self.month] + "月",
            "%B": _MONTHS[self.month] + "月份",
            "%k": "0一二三四"[self.quartor] + "季度",
            "%K": f"{self.year}年{self.quartor}季度",
        }
        keys = set(_Pattern / fmt) - set(d.keys())
        values = super().strftime(" ".join(keys)).split()
        d.update(zip(keys, values))
        for k, v in d.items():
            fmt = fmt.replace(k, v)
        return fmt

    # 使用date%'%Y-%m-%d'的语法来格式化日期
    __mod__ = strftime = format

    def iter(self, end, step={"days": 1}, fmt=None):
        """遍历日期，如果days 为整数，则遍历days 指定的天数,
        若days 为非整数，则days 应为终止的日期,
        fmt 为返回格式：如为字符串，则格式化日期；若为可调用对象，则调用该日期"""
        if isinstance(fmt, str):

            def _fmt(d):
                return d % fmt
        elif callable(fmt):
            _fmt = fmt
        else:
            _fmt = None

        if isinstance(end, dict):
            p, a = {}, {}
            for k, v in end.items():
                if k in set(["year", "month", "day"]):
                    p[k] = v
                else:
                    a[k] = v
            end_day = self.add(**a) if a else self
            if a:
                end_day = end_day.replace(**p)
        else:
            end_day = datetime(end)
        while self < end_day:
            yield _fmt(self) if _fmt else self
            self = self.add(**step)


def date_add(dt, *args, **kw):
    """日期及时间的加减,
    支持的参数有：years,months,days,hours,minutes,seconds"""
    return datetime(dt).add(*args, **kw)


def now(tz=LTZ):
    return datetime(dt.datetime.now(tz))


def date(d: str) -> str:
    "将任意格式的日期转换成 YYYY-MM-DD 格式"
    try:
        return datetime(d) % "%F"
    except Exception:
        return d


def today() -> str:
    return now() % "%F"
