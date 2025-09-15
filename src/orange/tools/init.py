# 项目：Python开发工具包
# 模块：工具包
# 作者：黄涛
# 创建：2015-9-2
# 修订：2015-9-3 添加setup.py以及testing的相关初始化
# 修订：2016-9-6 移除stdlib的支持

import os

from orange import Path, arg, now

INITIAL_VERSION = 'version="0.1"\n'
INITIAL_FILE = """# 项目：{project}
# 作者：{author}
# 邮件：{email}
# 创建：{date:%Y-%m-%d}
"""
SETUP_FILE = """#!/usr/bin/env python3
from orange import setup
requires=[
          ]
console_scripts=[
        # 'cmdname=package:function',
                 ]
gui_scripts=[
        # 'cmdname=package:function',
                 ]
setup(
        name='{prj_name}',
        author='{author}',
        author_email='{email}',
        description='{project}',
        install_requires=requires,
        long_description='{project}',
        entry_points={{'console_scripts':console_scripts,
                       'gui_scripts':gui_scripts}},
        url='https://github.com/huangtao-sh/{prj_name}.git',
        license='GPL',
        )
"""
TESTING_PKG = """from .test_sample import *
"""
TEST_SAMPLE = """import unittest
class TestSample(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sample(self):
        a='this is a test.'
        self.assertEqual(a,a)
"""


@arg("-p", "--project", help="项目描述")
@arg("-a", "--author", help="作者姓名", default="黄涛")
@arg("-e", "--email", help="电子邮件", default="hunto@163.com")
def main(project="", author="", email=""):
    """
    初始化项目文件
    自动在当前目录下生成包文件、初始版本号文件、安装文件和测试文件
    project:项目名称
    author:作者姓名
    email:作者的电子邮件
    """
    prj_name = os.path.split(os.path.abspath("."))[-1]
    ver_file = "%s/__version__.py" % (prj_name)
    pkg_file = "%s/__init__.py" % (prj_name)
    # 生成setup.py文件
    if not os.path.isfile("setup.py"):
        Path("setup.py").text = SETUP_FILE.format(
            author=author, prj_name=prj_name, project=project, email=email
        )
        print("已生成setup.py")

    # 创建包目录
    if not os.path.isdir(prj_name):
        os.mkdir(prj_name)
    # 生成初始化版本文件
    if not os.path.isfile(ver_file):
        Path(ver_file).text = INITIAL_VERSION
        print("当前程序版本初始化为：0.1")
    # 生成初始化包文件
    if not os.path.isfile(pkg_file):
        contents = INITIAL_FILE.format(
            project=project, author=author, email=email, date=now()
        )
        Path(pkg_file).text = contents
        print("已初始化包文件")

    # 生成测试模板文件
    if not os.path.isdir("testing"):
        testing = Path("testing")
        testing.ensure()
        (testing / "__init__.py").text = TESTING_PKG
        (testing / "test_sample.py").text = TEST_SAMPLE
        print("已创建测试模板文件")
