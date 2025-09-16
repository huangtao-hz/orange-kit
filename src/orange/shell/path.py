# 项目：standard python lib
# 模块：path and file
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-03-11 12:21
# 修改：2016-04-13 21:01
# 修改：2016-08-13 新增__iter__ 和 extractall功能
# 修订：2016-11-19
# 修订：2018-05-25 增加write_tables功能
# 修订：2018-09-12 为 Path 增加 verinfo 功能
# 修改：2018-09-16 09:00 增加 link_to  功能 以及 >> 和 << 操作符
# 修订：2018-09-18 20:04 修正 __iter__ 的bug.
# 修改：2019-02-23 13:42 增加音乐文件的 metadata 及 tags 功能
# 修改：2019-03-04 14:21 增加修复网络下载文件名的功能
# 修改：2019-03-15 09:10 Path.iter_csv 增加 columns 参数
# 修订：2019-03-19 14:00 优化 Path.pack、Path.zip 功能
# 修订：2020-01-27 14:24 增加 size 属性，read_data 函数新增 quote 功能
# 修订：2021-09-14 21:30 将 mtime、ctime 修改为输出字符串
# 修订：2022-05-08 19:41 修改 pack 函数，支持对目录下的文件进行压缩
# 修订：2022-09-04 13:55 write_xlsx 不在支持  force 参数

import os
import pathlib
import re
import sys
from codecs import BOM_BE, BOM_LE, BOM_UTF8
from contextlib import contextmanager, suppress
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Optional

from packaging.version import Version

from orange.utils import Data, arg, command

from .shell import POSIX, sh


class TempDir(TemporaryDirectory):
    __slots__ = ()

    def __enter__(self):
        return Path(self.name)


tempdir = TempDir

_UrlPattern = re.compile(r"\%[0-9A-E]{2}")

OldVersion = sys.version_info <= (3, 12)


@contextmanager
def tempfile(data=None, writer=None, **kw):
    if data:
        kw["mode"] = "wb" if isinstance(data, bytes) else "w"
    kw["delete"] = False
    try:
        with NamedTemporaryFile(**kw) as f:
            if data:
                f.write(data)
            if callable(writer):
                writer(f)
            tmp = Path(f.name)
        yield tmp
    finally:
        tmp.unlink()


BOM_CODE = {
    BOM_UTF8: "utf_8",
    BOM_LE: "utf_16_le",
    BOM_BE: "utf_16_be",
}

DEFAULT_CODES = "utf8", "gbk", "utf16", "big5"


def is_installed(file_name: str) -> bool:
    """
    确认指定的文件是否已被安装。
    """
    if file_name:
        """
        from sysconfig import get_path
        paths = [
            str(Path(get_path(name)).resolve())
            for name in ('platlib', 'scripts')
        ]
        if POSIX:
            paths.append('/usr')
            """
        filename = Path(file_name).resolve()
        return any(x in filename.parts for x in ("bin", "Scripts"))
    else:
        return False


def is_dev(cmd: Optional[str] = None) -> bool:
    cmd = cmd or sys.argv[0]
    if "wsgi" in cmd:
        return False
    return "test" in cmd or (not is_installed(cmd))


def decode(d: bytes) -> str:
    """
    对指定的二进制，进行智能解码，适配适当的编码。按行返回字符串。
    """
    for k in BOM_CODE:
        if k == d[: len(k)]:
            return d[len(k) :].decode(BOM_CODE[k])
    for encoding in DEFAULT_CODES:
        with suppress(UnicodeDecodeError):
            return d.decode(encoding)
    raise Exception("解码失败！")


def unquote(s: str, quote: str = '"') -> str:
    "删除字符串的引号"
    return s[1:-1] if s.startswith(quote) and s.endswith(quote) else s


_Parent = pathlib.WindowsPath if os.name == "nt" else pathlib.PosixPath


def fdate(t: float) -> str:
    from datetime import datetime as dt

    date = dt.fromtimestamp(int(t))
    return str(date)


class Path(_Parent):
    __slots__ = ()

    def __bool__(self):
        """判断文件是否存在"""
        return self.exists()

    @classmethod
    def tempdir(cls, *args, **kw):
        return TempDir(*args, **kw)

    @classmethod
    def tempfile(cls, data=None, writer=None, suffix=None, **kw):
        return tempfile(data=data, writer=writer, suffix=suffix, **kw)

    def __new__(cls, *args, **kwargs):
        """Construct a PurePath from one or several strings and or existing
        PurePath objects.  The strings and path objects are combined so as
        to yield a canonicalized path, which is incorporated into the
        new PurePath object.
        """
        if OldVersion:
            if args and isinstance(args[0], str):
                path = args[0]
                if path.startswith("~"):  # 支持用户目录开头
                    path = os.path.expanduser(path)
                elif path[0] in ("%", "$"):  # 支持环境变量转义
                    path = os.path.expandvars(path)
                args = [path, *args[1:]]
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args):
        "3.12以后的版本使用本程序来初始化"
        if not OldVersion:
            if args:
                path = args[0]
                if isinstance(path, str):
                    if path.startswith("~"):  # 支持用户目录开头
                        path = os.path.expanduser(path)
                    elif path[0] in ("%", "$"):  # 支持环境变量转义
                        path = os.path.expandvars(path)
                    args = [path, *args[1:]]
                super().__init__(*args)

    def read(self, *args, **kwargs):
        """以指定的参数读取文件"""
        with self.open(*args, **kwargs) as fn:
            return fn.read()

    def ensure(self, parents: bool = True):
        """确保目录存在，如果目录不存在则直接创建"""
        if not self.exists():
            self.mkdir(parents=parents)

    @property
    def text(self):
        """读取文件，并返回字符串"""
        return decode(self.read("rb"))

    @text.setter
    def text(self, text: str):
        """写入文本文件"""
        self.write(text=text)

    @property
    def lines(self):
        """按行读取文件"""
        return self.text.splitlines()

    @lines.setter
    def lines(self, lines):
        """按行写入文件"""
        self.write(lines)

    def write(
        self,
        content=None,
        text=None,
        data=None,
        encoding="utf8",
        errors=None,
        parents=False,
    ):
        """写文件"""
        if parents:
            self.parent.ensure()
        data = content or text or data
        if isinstance(content, (tuple, list)):
            data = "\n".join(content)
        if isinstance(data, str):
            self.write_text(data, encoding, errors)
        elif isinstance(data, bytes):
            self.write_bytes(data)

    @property
    def worksheets(self):
        import xlrd3 as xlrd

        with xlrd.open_workbook(filename=str(self)) as book:
            return book.sheets()

    def sheets(self, index=None, *pipelines, header=None):
        """提供读取指定worksheet的功能，其中index可以为序号，
        也可以为表的名称。"""
        import xlrd3 as xlrd

        book = xlrd.open_workbook(filename=str(self))
        if isinstance(index, int):
            sheet = book.sheet_by_index(index)
        elif isinstance(index, str):
            sheet = book.sheet_by_name(index)
        if sheet:
            data = sheet._cell_values
            if pipelines or header:
                data = Data(data, *pipelines, header=header)
            return data

    def iter_sheets(self):
        """如果指定的文件为excel文件，则可以迭代读取本文件的数据。
        返回：表的索引、表名、数据"""
        import xlrd3 as xlrd

        book = xlrd.open_workbook(filename=str(self))
        for index, sheet in enumerate(book.sheets()):
            yield index, sheet.name, sheet._cell_values

    def iter_csv(
        self,
        *pipelines,
        encoding=None,
        errors=None,
        columns=None,
        dialect="excel",
        rows=0,
        _filter=None,
        filter=None,
        converter=None,
        **kw,
    ) -> Data:
        """读取 csv 数据
        encoding :  指定文件的编码
        errors:     指定编码解码错误时的处理策略
        _filter:    过滤器，过滤指定数据，默认过滤空行
        columns:    指定返回的列，如（1，2，4）
        rows:       0,逐行返回数据，>0 按 rows 指定的行数返回数据
        dialet:     csv 处理方式，默认为 excel
        kw:         其他 csv.reader 所需参数
        """
        import csv

        def reader():
            with self.open(encoding=encoding, errors=errors) as f:
                yield from f

        filter = filter or _filter
        data = csv.reader(reader() if encoding else self.lines, dialect=dialect, **kw)
        if any([columns, pipelines, filter, rows, converter]):
            data = Data(
                data,
                *pipelines,
                rows=rows,
                filter=filter,
                converter=converter,
                columns=columns,
            )
        return data

    @property
    def xmlroot(self):
        """如果指定的文件为xml文件，则返回本文件的根元素"""
        from xml.etree.ElementTree import fromstring

        return fromstring(self.text)

    def __iter__(self):
        """根据文件的不同，迭代返回不同的内容。支持如下文件：
        1、文本文件，按行返回文本
        2、Excel文件，返回表索引、表名及表中数据
        3、目录，则返回本目录下所有文件
        4、del文件，按行返回数据。
        5、csv文件，按行返回数据。
        """
        if self.is_dir():
            yield from self.iterdir()
        suffix = self.lsuffix
        if suffix.startswith(".xls"):
            yield from self.iter_sheets()
        elif suffix == ".xml":
            yield from self.xmlroot
        elif suffix in (".del", ".csv"):
            yield from self.iter_csv()

    def extractall(self, path=".", password: str = "", members=None):
        def conv_members(members, sep="/"):
            if members:
                repl_sep = "\\" if sep == "/" else "/"
                return tuple(map(lambda x: x.replace(repl_sep, sep), members))

        name = self.name.lower()
        if name.endswith(".rar"):
            members = conv_members(members, "/" if POSIX else "\\")
            members = " ".join(members) if members else ""
            cmd = f"unrar x -p{password}" if password else "unrar x"
            sh > f"{cmd} {self} {members} {path}"
        elif any(map(name.endswith, (".tar.gz", ".tgz", ".gz"))):
            import tarfile

            with tarfile.open(str(self), "r") as f:
                members = conv_members(members, "/")
                members = (
                    tuple(map(f.getmember, members)) if members else f.getmembers()
                )
                f.extractall(path, members)
        elif name.endswith(".zip"):
            import zipfile

            with zipfile.ZipFile(str(self)) as f:
                members = conv_members(members, "/")
                for fileinfo in f.filelist:
                    if not (fileinfo.flag_bits & 0x0800):
                        fileinfo.filename = fileinfo.filename.encode("cp437").decode(
                            "gbk"
                        )
                        f.NameToInfo[fileinfo.filename] = fileinfo
                f.extractall(path, members)

    def pack(self, dest: str, passwd: str = ""):
        """
        把当前目录打包，按子目录打包
        """
        _path = Path(dest)
        _path.ensure()
        for path in self:
            path.rar(_path, passwd=passwd)

    def zip(self, zipfilename: str) -> None:
        """
        把当前文件或目录内所有的文件压缩成 zip文件
        """
        import zipfile

        with zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED, 5) as z:
            if self.is_dir():  # 如为目录则打包整个文件夹
                for file in self.rglob("*.*"):
                    z.write(file, file - self)
            else:  # 如为文件则只打包当前文件
                z.write(self, self.name)

    @property
    def lsuffix(self) -> str:
        """返回小写的扩展名"""
        return self.suffix.lower()

    @property
    def pname(self) -> str:
        """返回不带扩展名的文件名"""
        return self.with_suffix("").name

    def rmtree(self):
        """删除整个目录"""
        import shutil

        shutil.rmtree(str(self))

    deltree = rmtree

    def chdir(self):
        if self.is_dir():
            os.chdir(str(self))

    def __sub__(self, other):
        return self.relative_to(other)

    def write_xlsx(
        self, *args, force: bool = False, formats: dict = {}, writer=None, **kw
    ):
        if self and not force:
            ...
        #    s = input('%s 已存在，请确认是否覆盖，Y or N?\n' % self.name)
        #    if s.upper() != 'Y':
        #        return
        from orange.xlsx import Book

        if callable(writer):
            with Book(str(self), formats=formats) as book:
                writer(book, *args, **kw)
        else:
            return Book(str(self), formats=formats, **kw)

    @property
    def mtime(self) -> str:
        """文件修改时间"""
        return fdate(self.lstat().st_mtime)

    @property
    def ctime(self) -> str:
        """文件创建时间"""
        return fdate(self.lstat().st_ctime)

    @property
    def size(self) -> int:
        return self.lstat().st_size

    @property
    def uri(self) -> str:
        """统一网址"""
        ur = self.resolve().as_uri()
        return ur if POSIX else ur.lower()

    @property
    def fullname(self) -> str:
        path = str(self.absolute())
        return path if POSIX else path.lower()

    def link_to(self, target: "Path") -> None:
        """
        创建文件或目录连接
        由 self 连接到 target
        如果 self 指向的文件已存在：是 target 则自动忽略，否则重新建立连接。
        """
        if self.is_symlink():
            if self.resolve() == target.resolve():  # 连接已存在，则忽略
                return
            self.unlink()
        if self:
            return
        return self.symlink_to(target, target.is_dir())

    def __rshift__(self, target: "Path"):
        """
        Path('a.txt') >> Path('b.txt')
        把 a.txt 连接到 b.txt 上
        """
        return self.link_to(Path(target))

    def __lshift__(self, target: "Path"):
        """
        Path('a.txt') << Path('b.txt')
        把 b.txt 连接到 a.txt 上
        """
        Path(target).link_to(self)

    @property
    def verinfo(self):
        if self.match("*.tar.gz"):
            type_ = "Source"
            d = self.name[:-7].split("-")
            version = Version(d[-1])
            name = "_".join(d[:-1])
            return name, version, type_
        elif self.match("*.zip"):
            type_ = "Source"
            d = self.name[:-4].split("-")
            version = Version(d[-1])
            name = "_".join(d[:-1])
            return name, version, type_
        elif self.match("*.whl"):
            type_ = "Wheel"
            d = self.pname.split("-")
            attrs = dict(zip(("version", "abi", "platform"), d[-3:]))
            version = Version(d[-4])
            name = "_".join(d[:-4])
            return name, version, type_, attrs

    @property
    def atime(self):
        """文件访问时间"""
        return int(self.lstat().st_atime)

    def write_tables(self, *tables, **kw):
        """
        写入多张表格，支持以下参数：
        formats:预设格式
        tables:为列表，每个table为字典，参数值如下：
        pos:位置
        columns:表格格式
        data:数据
        sheet:表格名称
        """

        def writer(book, *tables):
            for table in tables:
                pos = table.pop("pos", "A1")
                book.add_table(pos, **table)

        self.write_xlsx(writer=writer, *tables, **kw)

    def match(self, *patterns) -> bool:
        return any(map(super().match, patterns))

    def find(self, pattern: str, key=None, reverse: bool = True):
        result = tuple(sorted(self.rglob(pattern), key=key, reverse=reverse))
        if result:
            return result[0]

    @property
    def music_tag(self):
        from orange.utils.musictag import MusicTag

        return MusicTag(self)

    def repare_name(self):
        """修复网络下载的乱字符文件名"""
        name = self.name
        if _UrlPattern.search(name):
            import urllib

            name = urllib.parse.unquote_plus(name)
        else:
            if POSIX:
                from unicodedata import normalize

                name = normalize("NFC", name)
            with suppress(UnicodeEncodeError):
                name = decode(name.encode("latin1"))
        if name != self.name:
            print(self.name, "->", name)
            self.rename(self.with_name(name))

    def read_sheet(self, *args, sheet: str = "", start_row: int = 0, **kwargs):
        """
        读取 Excel 文件
        其中，*args,**kwargs 为 Data 类的参数
        sheet：读取 Excel 文件的表名或序号，如果为 None 读取所有表格，也可以为 list 或 tuple
        start_row:单元格的起始行
        """
        assert self.lsuffix.startswith(".xls")
        from .excel import WorkBook

        data = WorkBook(self).read_sheet(sheet, start_row=start_row)
        yield from Data(data, *args, **kwargs)

    def read_data(
        self,
        *args,  # 其他 Data 支持的位置参数
        encoding="GBK",  # 数据的编码格式
        errors="strict",  # 解码过程中出现错误的解决方式
        skip_header=True,  # 是否跳过标题行
        offsets=None,  # 按位置拆分，格式为 (0,11,21...)
        sep=b"|",  # 按数据拆分
        columns=None,  # 仅包含哪列
        include=None,  # 仅包含哪些列
        quote=None,  # 引用符号
        **kwargs,
    ):  # 其他 Data 支持的关键词参数
        """对金融科技部提供数据索取文件进行解析
        一般采用 GBK 编码，采用 "|" 进行分割
        columns 用于提取指定字段
        """
        from orange.utils.data import includer, mapper

        def _read(path: Path):  # , encoding, errors, sep, skip_header):
            with path.open("rb") as f:
                yield from f

        data = _read(self)
        if skip_header:
            next(data)
        if offsets:

            def _split(row):
                start = offsets[0]
                d = []
                for end in [*offsets[1:], None]:
                    d.append(row[start:end])
                    start = end
                return d
        else:
            if isinstance(sep, str):
                sep = sep.encode(encoding)

            def _split(row):
                return row.split(sep)

        data = map(_split, data)
        pipelines = []
        columns = columns or include
        if columns:
            pipelines.append(includer(*columns))
        pipelines.append(
            mapper(lambda row: [x.decode(encoding, errors).strip() for x in row])
        )
        if quote:
            pipelines.append(mapper(lambda row: [unquote(x, quote) for x in row]))
        return Data(data, *pipelines, *args, **kwargs)

    def rar(self, dest: str, passwd=None):
        "将本文件或文件打包成一个 Rar 文件"
        "如果当前路径为目录，并且目标路径也为目录的话，把当前文件夹打包后的压缩文件存在放在指定目录下"
        passwd = f"-p{passwd}" if passwd else ""
        dest = Path(dest)
        if not dest:
            raise Exception(f"目录 {dest} 不存在")
        if dest.is_dir() and self.is_dir():
            dest = dest / f"{self.name}.rar"
        if self.is_dir():
            self.parent.chdir()
            os.system(f'rar a {passwd} "{dest}" "{self.name}"')
        else:
            dest = dest / f"{self.pname}.rar"
            os.system(f'rar a -ep {passwd} "{dest}" "{self}"')


HOME = Path.home()
Cloud = (
    Path("~/Library/Mobile Documents/com~apple~CloudDocs")
    if sys.platform == "darwin"
    else Path("~/OneDrive")
)


@command(description="Windows 格式文件转换为 Unix 文件格式")
@arg("files", nargs="*", help="待转换的文件", metavar="file")
def convert(files):
    for file in files:
        Path(file).lines = Path(file).lines
        print('转换文件"%s"成功' % (file))


def clean_trash():
    Patterns = (
        "._.DS_Store",
        ".DS_Store",
        "._*",
        "~$*",
        "Thumbs.db",
        "*.tmp",
        "Icon?",
    )
    print("开始清查系统垃圾文件！")
    ROOT = HOME / "OneDrive/工作"
    for file_ in ROOT.rglob("*.*"):
        if any(map(file_.match, Patterns)):
            with suppress(PermissionError):
                file_.unlink()
                print(f"删除文件 {file_.name}")


@command(description="修复文件名的乱码")
@arg("pathes", nargs="+", metavar="path", help="文件名或路径")
def repare_filename(pathes):
    for path in map(Path, pathes):
        if path.is_dir():
            [p.repare_name() for p in path]
        else:
            path.repare_name()


@command(description="对下载的音乐进行转换，并加入 iTunes 音乐库", allow_empty=True)
@arg("path", default="~/Downloads", help="音乐文件目录")
def add_music_lib(path=None):
    src = Path(path or "~/Downloads")
    dest = HOME / "Music/iTunes/iTunes Media/Automatically Add to iTunes.localized"
    for path in src.iterdir():
        if path.lsuffix in (".flac", ".ape", ".mp3", ".m4a", ".wav"):
            path.music_tag.fixtags()
            if path.lsuffix in (".mp3", ".m4a"):  # 无需转码的音乐文件
                path.rename(dest / path.name)  # 直接修改文件名
                print(f"copy 文件 {path.name}")
            else:  # 无损音乐转成 .m4a 格式
                destname = (dest / path.name).with_suffix(".m4a")
                if not destname:
                    # 进行转码
                    sh(f'ffmpeg -i "{path}" -acodec alac "{destname}"')
                if destname:
                    path.unlink()  # 目标文件建立成功，删除源文件
