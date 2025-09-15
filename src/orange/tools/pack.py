# 项目：   标准库函数
# 模块：   打包主程序
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2022-04-23 08:53

from orange import arg, Path, command
detail = '''本程序用于打包文件夹
src:   源目录
dest:  目标目录
本程序可以将源目录下的每一个文件夹打包成一个 rar 文件，并使用 passwd 指定的密码进行加密
'''


@command(description=detail)
@arg("src", help='源目录')
@arg("dest", help="存放打包文件目录")
@arg("-p", "--passwd", nargs='?', help="压缩包密码")
def main(src, dest, passwd=None):
    Path(src).pack(dest, passwd=passwd)


if __name__ == '__main__':
    main()
