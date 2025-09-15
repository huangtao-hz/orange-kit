# 项目：标准库函数
# 模块：命令行处理模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2017-01-18 21:34
# 修改：2017-02-05 为__call__函数增加位置参数，可以支持主程序为classmethod
# 修改：2017-02-11 调整相关函数名

import sys
from argparse import ArgumentParser
from functools import partial, wraps


class _Command(object):
    kwargs = {}  # ArgumentParser 的参数，由command函数生成
    allow_empty = (
        False  # 是否允许参数为空，如允许则argv为None的情况下也调用执行函数
    )

    def __init__(self, run):
        self.run = run  # 可执行函数，命令行解析成功后调用
        self.args = []  # 参数列表
        self.subcommands = []  # 子命令列表

    @classmethod
    def wrapper(cls, cmd, *args, **kw):
        def _(fn):
            if not isinstance(fn, cls):
                fn = cls(fn)
            getattr(fn, cmd)(*args, **kw)
            return fn

        return _

    def add_subcommand(self, subcommand):
        self.subcommands.append(subcommand)

    def add_arg(self, *args, **kw):
        self.args.append((args, kw))

    def command(self, *subcommands, allow_empty=False, **kwargs):
        self.kwargs = kwargs  # ArgumentParser 的参数
        self.subcommands = list(subcommands)  # 子命令
        self.allow_empty = allow_empty  # 是否允许命令行为空

    def proc_args(self, parser):
        for args, kw in reversed(self.args):
            parser.add_argument(*args, **kw)

    def __call__(self, *args, argv=None):
        argv = argv or sys.argv[1:]
        parser = ArgumentParser(**self.kwargs)
        self.proc_args(parser)
        parser.set_defaults(proc=self.run)
        if self.subcommands:
            subparsers = parser.add_subparsers(help="Sub command")
            for subcommand in self.subcommands:
                help = subcommand._kw.pop("description")
                if help:
                    subcommand._kw["help"] = help
                sub = subparsers.add_parser(
                    subcommand.run.__name__, **subcommand.kwargs
                )
                subcommand.proc_args(sub)
                sub.set_defaults(proc=subcommand.run)
        if self.allow_empty or argv:
            kwargs = dict(parser.parse_args(argv)._get_kwargs())
            proc = kwargs.pop("proc", None)
            if proc:
                try:
                    proc(*args, **kwargs)
                except Exception as e:
                    print(str(e))
        else:
            parser.print_usage()


command = partial(_Command.wrapper, "command")
arg = wraps(ArgumentParser.add_argument)(partial(_Command.wrapper, "add_arg"))
