# 项目：   工具库软件
# 模块：   系统初始化
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2018-11-17 10:10

from orange import Path, HOME
import os
import sys

LINKS = {
    'emacsd/emacs': '.emacs',
    'conf/gitconfig': '.gitconfig',
    'conf/ssh': '.ssh',
    'conf/pypirc': '.pypirc',
    'conf/vscode': '.vscode',
}

WIN32_LINKS = {
    'conf/pip/pip.conf': 'AppData/Roaming/pip/pip.ini',
    'conf/vimrc_win': '_vimrc',
}

DARWIN_LINKS = {
    'conf/vimrc_mac': '.vimrc',
    'conf/pip': '.pip',
}


def win_init():
    # 修改注册表，增加.PY 和.PYW 为可执行文件
    from orange.shell.regkey import HKLM, REG_SZ, HKCU, add_path
    with HKCU / 'GNU/Emacs' as key:
        key['HOME'] = str(HOME), REG_SZ
        print('设置 Emacs 的 HOME 目录完成。')

    with HKLM / 'SYSTEM/CurrentControlSet/Control/Session Manager/Environment' as key:
        pathext = key['PATHEXT'][0]
        for ext in ('.PY', '.PYW'):
            if ext not in set(pathext.split(';')):
                pathext += ';' + ext
        key['PATHEXT'] = pathext, REG_SZ
    bin = str(HOME / 'OneDrive/bin')
    add_path(bin, bin)
    print(f'设置路径：{bin}')
    if os.name == 'nt':
        import platform
        if platform.win32_ver()[0] == '7':
            print('设置 Console 支持 "Microsoft YaHei Mono" 字体')
            with HKLM / "SOFTWARE/Microsoft/Windows NT/CurrentVersion/Console/TrueTypeFont" as key:
                key['00936'] = 'Microsoft YaHei Mono', REG_SZ


def do_link():
    if sys.platform == 'win32':
        Path('~/AppData/Roaming/pip').ensure()
        LINKS.update(WIN32_LINKS)
    elif sys.platform == 'darwin':
        LINKS.update(DARWIN_LINKS)
    elif sys.platform == 'linux':
        LINKS.update(DARWIN_LINKS)

    home = HOME
    src = home / 'OneDrive'

    for source, dest in LINKS.items():
        s = src / source
        d = home / dest
        d >> s
        print(f'创建连接文件：{d} ->{s}')


def main():
    do_link()
    if sys.platform == 'win32':
        win_init()
    elif sys.platform == 'darwin':
        # darwin_init()
        pass


if __name__ == '__main__':
    main()
