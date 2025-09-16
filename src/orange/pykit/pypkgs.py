# 项目：库函数
# 模块：包管理模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2018-09-13 09:13

# 有一台电脑是 win32 的系统，且无法上网，无法自动升级 Python 包。故
# 编写本程序来对这些程序包进行管理
# 修改：2023-03-12 14:10 不再使用配置文件来处理
import json
from typing import Optional

from orange import arg, shell
from orange.shell import Path

from .pysetup import pip

PyLib = Path("~/Documents/pylib")

excludes = set(
    [
        "green-mongo",
        "orange-kit",
        "coco",
        "jym",
        "params",
        "gmongo",
        "bs4",
        "heic",
        "bbsm",
        "jqb",
        "glemon",
        "lzbg",
        "fxq",
    ]
)


def is_connected(url: Optional[str] = None):
    """检查本机是否联网"""
    from urllib.request import urlopen

    url = url or "https://www.sohu.com"
    try:
        with urlopen(url) as rep:
            return rep.status == 200
    except Exception:
        ...


def batch_download():
    libpath = PyLib
    for pkg in get_installed_packages():
        if pkg not in excludes:
            pip(
                "download",
                pkg,
                "-d",
                str(libpath),
                "--no-deps",
                "--platform=win_amd64",
                "--python-version=38",
                "--only-binary=:all:",
            )


def get_installed_packages() -> tuple:
    pkgs = shell("pip3 list --format json")
    if pkgs:
        return tuple(pkg["name"] for pkg in json.loads(pkgs[0]))
    else:
        return tuple()


def get_cached_pkgs():
    for path in PyLib.glob("*.*"):
        # print(path)
        verinfo = path.verinfo
        # print(verinfo)
        if verinfo:
            name, ver, type_ = verinfo[:3]
            yield name, ver, type_, path


def cleanlib():
    pkg = None
    for r in sorted(get_cached_pkgs(), reverse=True):
        if pkg != r[0]:
            pkg = r[0]
        else:
            r[3].unlink()
            print(f"{r[3]} has been deleted")


@arg("-d", "--download", action="store_true", help="下载包文件")
@arg("-u", "--upgrade", action="store_true", help="升级文件")
@arg("-c", "--clean", action="store_true", help="清理无用的包")
def main(download=False, upgrade=False, **options):
    if download:
        batch_download()
    if upgrade:
        pkglist = shell("pip3 list -o")
        if pkglist:
            print(*pkglist, sep="\n")
            for line in pkglist[2:]:
                pkg = line.split()
                if pkg and pkg[0] not in excludes:
                    pip("install", "-U", pkg[0])

    if options["clean"]:
        cleanlib()


if __name__ == "__main__":
    main()
