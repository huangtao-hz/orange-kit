# 项目：   Word 的库
# 模块：   Word 库表的封装
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2024-12-18 07:47

from docx.oxml.ns import qn
from docx.oxml.parser import OxmlElement
from docx.styles.style import ParagraphStyle
from docx.text.font import Font
from docx.text.paragraph import Paragraph
from typing import Optional


def Remove(elem):
    "删除指定的元素，包括：段落、表格、图片等"
    return elem._element.getparent().remove(elem._element)


def _setFontName(self, value: str):
    """增加中文字体的设置"""
    rPr = self._element.get_or_add_rPr()
    rPr.rFonts_ascii = value
    rPr.rFonts_hAnsi = value
    rPr.rFonts.set(qn("w:eastAsia"), value)


def insert_paragraph_after(
    self: Paragraph, text: str = "", style: Optional[ParagraphStyle] = None
) -> Paragraph:
    "在指定的段落后面插入段落"
    "看不太懂，从网上抄的，貌似可以正常工作"
    new_p = OxmlElement("w:p")
    self._p.addnext(new_p)
    new_para = Paragraph(new_p, self._parent)
    if style:
        new_para.style = style
    if text:
        new_para.add_run(text)
    return new_para


Font.name = Font.name.setter(_setFontName)  # 替换掉原来的设置字体，以便支持中文字体
Paragraph.insert_paragraph_after = (
    insert_paragraph_after  # 为段落对象增加在段后增加段落的功能
)


def set_table_border(table, auto=True, **kwargs):
    """
    设置表格的边框
    用法:
    set_table_border(
        table,
    top={"sz": 12, "val": "single", "color": "#FF0000"},
    bottom={"sz": 12, "color": "#00FF00", "val": "single"},
    left={"sz": 24, "val": "dashed"},
    right={"sz": 12, "val": "dashed"},
    )
    """
    # default = {"sz": 1, "val": "single", "color": "#000000", "space": "0"}
    borders = OxmlElement("w:tblBorders")
    for tag in ("bottom", "top", "left", "right", "insideV", "insideH"):
        edge_data = kwargs.get(tag)
        if edge_data:
            any_border = OxmlElement(f"w:{tag}")
        for key in ["sz", "val", "color", "space", "shadow"]:
            if key in edge_data:
                any_border.set(qn(f"w:{key}"), str(edge_data[key]))
                borders.append(any_border)
    table._tbl.tblPr.append(borders)
