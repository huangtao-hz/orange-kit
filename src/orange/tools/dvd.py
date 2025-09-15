# 项目：   工具箱
# 模块：   DVD转录
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2019-02-23 21:08

from orange import HOME, Path, arg, command, sh

Dest = HOME / "Videos"


@command(description="DVD 转录软件")
@arg("source", help="DVD所在盘符或存放VOB文件的目录")
@arg("-n", "--name", help="DVD光碟的名称")
def main(source, name):
    source = Path(source)
    if not source:
        print("请输入DVD文件所在目录")
        exit(1)
    if not name:
        print("请输入目标文件目录")
        exit(2)
    dest = Dest / name
    dest.ensure()
    for vob in source.rglob("*.VOB"):
        d = (dest / vob.name).with_suffix(".mp4")
        if not d:
            sh > f"ffmpeg -i {vob} {d}"
