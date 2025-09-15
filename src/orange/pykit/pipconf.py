# 项目：我的工具箱
# 模块：配置 PIP 的镜像服务器
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2023-03-05 13:45

import sys

pipconf = """
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=pypi.tuna.tsinghua.edu.cn
"""


def main():
    from orange import Path

    conf_path = None
    if sys.platform == "darwin":
        conf_path = Path("~/.pip/pip.conf")
    elif sys.platform == "win32":
        conf_path = Path(r"%localappdata%/pip/pip.ini")
    if conf_path:
        conf_path.parent.ensure()
        conf_path.text = pipconf
        print("配置 pip.conf 完成！")
    else:
        print(f"尚不支持 {sys.platform} 操作系统")
