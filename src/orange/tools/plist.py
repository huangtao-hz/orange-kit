# 项目：标准库函数
# 模块：macos的plist生成器
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-09-06 23:27
# 修改：2016-9-17 使用plistlib 来写入plist文件

import sys
from plistlib import dump, Dict
from orange.shell import Path
from orange.utils import arg


@arg('filename', nargs=1, help='文件名')
@arg('label', nargs=1, help='标签')
@arg('args', nargs='*', metavar='arg', help='其他参数')
def main(filename, label, *args):
    filename = str(Path(filename).with_suffix('.plist'))
    with open(filename, 'wb') as fn:
        dump(Dict(Label=label,
                  KeepAlive=True,
                  ProgramArguments=args), fn)
