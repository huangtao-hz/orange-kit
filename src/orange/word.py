# 项目：我的工具箱
# 模块：生成 Word 模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2023-04-21 23:35

from docx import Document as _Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Pt

from orange import Path, datetime, now, wlen
from typing import Union
from docx.styles.style import ParagraphStyle

from .utils.hz import Ordinal

HANZI = "零一二三四五六七八九十百"
NoPattern = r"[一二]"


class Document:
    """
    标准公文格式
    """

    def __init__(self):
        self.document = _Document()
        self.heading = [Ordinal(), Ordinal(), Ordinal(), Ordinal()]
        # section = self.document.sections[0]
        # section.top_margin = Cm(3.7)
        # section.bottom_margin = Cm(3.5)
        # section.left_margin = Cm(2.8)
        # section.right_margin = Cm(2.6)

        zw = self.document.styles["Normal"]
        assert isinstance(zw, ParagraphStyle)
        zw.font.size = Pt(16)
        zw.font.name = "仿宋_GB2312"
        zw._element.rPr.rFonts.set(qn("w:eastAsia"), "仿宋_GB2312")
        zw.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        zw.paragraph_format.first_line_indent = Pt(32)
        zw.paragraph_format.space_after = Pt(0)
        zw.paragraph_format.line_spacing = 1.5
        # zw.keep_together = False

        gwbt = self.document.styles.add_style("公文标题", WD_STYLE_TYPE.PARAGRAPH)
        assert isinstance(gwbt, ParagraphStyle)
        gwbt.font.size = Pt(22)
        gwbt.font.name = "方正小标宋简体"
        gwbt._element.rPr.rFonts.set(qn("w:eastAsia"), "方正小标宋简体")
        gwbt.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        gwbt.paragraph_format.space_after = Pt(0)
        gwbt.paragraph_format.line_spacing = 1

        zw = self.document.styles.add_style("一级标题", WD_STYLE_TYPE.PARAGRAPH)
        assert isinstance(zw, ParagraphStyle)
        zw.font.size = Pt(16)
        zw.font.name = "黑体"
        zw._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        zw.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        zw.paragraph_format.first_line_indent = Pt(32)
        zw.paragraph_format.space_after = Pt(0)
        zw.paragraph_format.line_spacing = 1.5

        zw = self.document.styles.add_style("二级标题", WD_STYLE_TYPE.PARAGRAPH)
        assert isinstance(zw, ParagraphStyle)
        zw.font.size = Pt(16)
        zw.font.name = "楷体"
        zw._element.rPr.rFonts.set(qn("w:eastAsia"), "楷体")
        zw.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        zw.paragraph_format.first_line_indent = Pt(32)
        zw.paragraph_format.space_after = Pt(0)
        zw.paragraph_format.line_spacing = 1.5

        zw = self.document.styles.add_style("文号", WD_STYLE_TYPE.PARAGRAPH)
        assert isinstance(zw, ParagraphStyle)
        zw.font.size = Pt(14)
        zw.font.name = "仿宋_GB2312"
        zw._element.rPr.rFonts.set(qn("w:eastAsia"), "仿宋_GB2312")
        zw.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        zw.paragraph_format.space_after = Pt(0)
        zw.paragraph_format.line_spacing = 1

    def save(self, path: Union[str, Path]):
        "保存到磁盘文件"
        self.document.save(str(path))

    def add_title(self, title: str):
        "添加标题"
        return self.document.add_paragraph(title, "公文标题")

    def add_wenhao(self, wenhao: str):
        "添加文号"
        return self.document.add_paragraph(wenhao, "文号")

    def add_zsjg(self, jgmc: str):
        "添加主送机构"
        if not jgmc.endswith("："):
            jgmc += "："
        p = self.document.add_paragraph(jgmc, "Normal")
        p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        p.paragraph_format.first_line_indent = Pt(0)

    def add_para(self, lines):
        "添加正文"
        for p in lines.splitlines():
            self.document.add_paragraph(p, "Normal")

    def add_heading(self, head, level=1):
        "添加标题"
        if not 0 < level < 5:
            raise Exception(f"小标题 {level} 错误")
        if level == 1:
            style = "一级标题"
        elif level == 2:
            style = "二级标题"
        else:
            style = "Normal"
        self.document.add_paragraph(head, style)

    def add_fwjg(self, fwjg, rq=None):
        "添加发文机构"
        if not rq:
            rq = now()
        rq = datetime(rq).format("%x")
        self.add_para("")
        p = self.document.add_paragraph(fwjg, "Normal")
        p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        p.paragraph_format.right_indent = Pt(
            ((wlen(rq) + 3) / 2 + 8 - wlen(fwjg) / 2) * 8
        )
        p = self.document.add_paragraph(rq, "Normal")
        p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        p.paragraph_format.right_indent = Pt(16 * 4)
