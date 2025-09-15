# 项目：工具函数库
# 模块：python模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2018-09-28 21:52
# 修改：2023-12-02 22:39 优化安装程序
# 修改：2023-12-03 09:15 不允许直接调用 setup.py 处理


from typing import Optional

from orange.shell import POSIX, Path, sh
from orange.utils.click import arg, command

libpath = Path("~/Documents/pylib")

PYTHON = "python3" if POSIX else "python"


def run_cmd(cmd: str, *args, **kw):
    "执行系统命令"
    sh(cmd, *args, capture_output=False, **kw)


def run_mod(mod, *args, **kw):
    "run python library module as a script"
    run_cmd(PYTHON, "-m", mod, *args, **kw)


def pyclean():
    "清理打包过程中生成的中间文件"
    Patterns = ("build", "dist", "*egg-info")
    for path in Path(".").iterdir():
        if path.match(*Patterns):
            path.rmtree()
            print(f"Path {path} have been deleted!")


def pysetup(*args):
    if not Path("setup.py"):
        print("Cant find file setup.py!")
        exit(1)
    pip("install .")
    pyclean()


def pip(*args):
    run_mod("pip", *args)


def pyupload():
    pysdist("upload")


def pysdist(*args):
    pip("wheel", "-w", str(Path("~/Documents/pylib")), "--no-deps", ".")
    pyclean()


# ver = sysconfig._PY_VERSION_SHORT_NO_DOT
BINARY_PARAMS = {
    "implementation": "cp",
    "platform": "win_amd64",
    "python-version": "38",  # 单位电脑最高可以装3.8
    "abi": "cp38m",  # 单位电脑的版本为 3.8
    "only-binary": ":all:",
}


def pydownload(*pkgs, source=True):
    if source:
        pip(
            "download",
            *pkgs,
            "-d",
            str(libpath),
            "--no-binary=:all:",
            "--no-deps",
        )
    else:
        pip(
            "download",
            *pkgs,
            "-d",
            str(libpath),
            "--no-deps",
            *(f"--{k}={v}" for k, v in BINARY_PARAMS.items()),
        )


@command(allow_empty=True)
@arg("packages", help="python package", nargs="*", metavar="package")
@arg("-p", "--path", default=libpath, help="指定的目录")
@arg("-d", "--download", help="默认的包目录", action="store_true")
@arg("-b", "--binary", action="store_true", help="下载二进制程序包")
def pyinstall(
    path: str,
    packages: Optional[list] = None,
    download: Optional[str] = None,
    upgrade=False,
    binary=False,
):
    root = Path(path)
    if download and packages:
        pydownload(*packages, source=not binary)
    else:
        if packages:
            pkgs = []
            for pkg in packages:
                filename = root.find(f"{pkg}*", key=lambda path: path.verinfo)
                if filename:
                    pkgs.append(filename)
                else:
                    pkgs.append(pkg)
            print("installed:", *pkgs)
            pip("install", *pkgs)
        else:
            if Path("setup.py"):
                pip("install", ".")
                pyclean()
            else:
                print("Cant find the file setup.py!")


if __name__ == "__main__":
    pyinstall()
