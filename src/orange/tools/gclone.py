#!/usr/bin/env python3
# 项目：克隆github.com上的项目
# 模块：命令行模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2015-06-11 12:28
# 修订：2016-11-18 采用Parser来分析参数
# 修改：2018-09-12 10:35 采用 shell 来处理命令行

# from stdlib import parse_args,exec_shell
from typing import Optional

from orange import Path, arg, shell


@arg("repos", nargs="+", metavar="repo", help="要下载的软件仓库，可以为多个")
@arg("-u", "--user", nargs="?", help="要下载的用户名,默认为本人的仓库")
def proc(repos: list[str], user: Optional[str] = None, protocol: str = "SSH"):
    if user is None:
        from configparser import ConfigParser

        config = ConfigParser()
        config.read([str(Path("~/.gitconfig"))])
        try:
            user = config.get("user", "name")
        except Exception:
            raise Exception("用户不存在！")
    protocol = protocol.upper()
    URL = "git@github.com:" if protocol == "SSH" else "https://github.com/"
    for repo in repos:
        if "/" not in repo:
            repo = f"{user}/{repo}"
        url = f"{URL}/{repo}.git"
        print("cloning", url)
        shell(f"git clone {url}")
