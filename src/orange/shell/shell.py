# 项目：库函数
# 模块：系统模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2018-09-27 19:21

import os
from subprocess import PIPE, run
from sys import version_info
from typing import Optional, Union

POSIX = os.name == "posix"
encoding = "utf8" if POSIX else "gbk"


def shell(
    cmd: str,
    *args,
    prefix: Optional[str] = "-",
    input=None,
    capture_output=True,
    **options,
) -> tuple[int, str]:
    """
    调用方式：   code,output = sh('dir')
    返回值：     code 系统返回值
                output     命令输出内容
    """
    if prefix is None:
        prefix = "-" if POSIX else "/"
    params = [cmd]
    for arg in args:
        if not isinstance(arg, str):
            arg = str(arg)
        if any(space in arg for space in (" ", "\t")) and not arg.startswith(
            '"'
        ):
            arg = f'"{arg}"'
        params.append(arg)
    for option, arg in options.items():
        if prefix == "-" and len(option) > 1:
            p = "--"
        else:
            p = prefix
        if isinstance(arg, bool):
            if arg:
                params.append(f"{p}{option}")
        else:
            arg = str(arg)
            params.append(f"{p}{option}:{arg}")
    cmd = " ".join(params)
    if version_info[:2] >= (3, 7):
        rt = run(
            cmd,
            input=input,
            encoding=encoding,
            capture_output=capture_output,
            shell=True,
        )
    else:
        if capture_output:
            stdout, stderr = PIPE, PIPE
        else:
            stdout, stderr = None, None
        rt = run(
            cmd,
            input=input,
            stdout=stdout,
            stderr=stderr,
            encoding=encoding,
            shell=True,
        )
    return rt.returncode, rt.stdout


class Shell(type):
    __slots__ = ()

    def __call__(
        self,
        cmd: str,
        *args,
        prefix: str = "-",
        input=None,
        capture_output=True,
        **options,
    ) -> Union[tuple[int, str], int]:
        """
        调用方式：   code,output = sh('dir')
        返回值：     code 系统返回值
                    output     命令输出内容
        """
        code, out = shell(
            cmd,
            *args,
            prefix=prefix,
            input=input,
            capture_output=capture_output,
            **options,
        )
        return (code, out) if capture_output else code

    def __gt__(self, cmd: str) -> int:
        """
        调用方式： sh > 'dir'
        系统直接打印输出执行命令的输出
        返回值 ：操作系统的返回值
        """
        r = run(cmd, shell=True, encoding=encoding)
        return r.returncode


class sh(metaclass=Shell):
    __slots__ = ()
