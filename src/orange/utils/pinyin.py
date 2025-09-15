# 项目：工具库
# 模块：拼音模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2018-09-27 21:29

from pypinyin import slug
from pypinyin.constants import FIRST_LETTER, NORMAL


def get_py(s, style=FIRST_LETTER, separator="") -> str:
    """
    获取拼音首字母。
    """
    return slug(s,style,separator=separator)

def get_pinyin(s, style=NORMAL, separator="") -> str:
    """
    获取拼音首字母。
    """
    return slug(s,style,separator=separator)
