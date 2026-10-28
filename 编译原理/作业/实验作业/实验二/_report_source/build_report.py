"""Build Experiment 2 using the same typography and layout as Experiment 1."""

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "proj2_submission" / "report.pdf"
pdfmetrics.registerFont(TTFont("ReportSong", "/System/Library/Fonts/Supplemental/Songti.ttc", subfontIndex=6))
pdfmetrics.registerFont(TTFont("ReportHei", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))

ACCENT = colors.HexColor("#563568")
DARK = colors.HexColor("#1E1E20")
MID = colors.HexColor("#666269")

body = ParagraphStyle("Body", fontName="ReportSong", fontSize=11.2, leading=17.2,
                      alignment=TA_JUSTIFY, wordWrap="CJK", textColor=DARK, spaceAfter=5.5)
bullet = ParagraphStyle("Bullet", parent=body, leftIndent=13, firstLineIndent=-10, spaceAfter=3.8)
heading = ParagraphStyle("Heading", parent=body, fontName="ReportHei", fontSize=13.5,
                         leading=19, alignment=TA_LEFT, spaceBefore=5, spaceAfter=3, keepWithNext=True)
title = ParagraphStyle("Title", parent=heading, fontSize=20, leading=26,
                       alignment=TA_CENTER, spaceBefore=9, spaceAfter=4)
eyebrow = ParagraphStyle("Eyebrow", parent=body, fontName="ReportHei", fontSize=11,
                         leading=15, alignment=TA_CENTER, textColor=MID, spaceAfter=8)
brand_cn = ParagraphStyle("BrandCN", parent=heading, fontSize=13, leading=17, textColor=ACCENT)
brand_en = ParagraphStyle("BrandEN", parent=body, fontName="Times-Roman", fontSize=11,
                          leading=17, alignment=TA_RIGHT, textColor=MID)
section_number = ParagraphStyle("SectionNumber", parent=heading, fontSize=11.5, leading=17,
                                alignment=TA_CENTER, textColor=colors.white)
meta = ParagraphStyle("Meta", parent=body, fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=0)
code = ParagraphStyle("Code", fontName="Courier", fontSize=11, leading=14.5,
                      leftIndent=15, textColor=DARK, spaceBefore=2, spaceAfter=6)


def title_block(text):
    masthead = Table([[Paragraph("南京大学", brand_cn), Paragraph("NANJING UNIVERSITY", brand_en)]],
                     colWidths=[252, 252])
    masthead.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.1, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [masthead, Paragraph(escape(text), title),
            Paragraph("编译原理课程实验报告 · EXPERIMENT 02", eyebrow)]


def metadata(text):
    cells = [Paragraph(item, meta) for item in text.split("　　")]
    table = Table([cells], colWidths=[252, 252])
    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, colors.HexColor("#999999")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [table, Spacer(1, 7)]


def section(text):
    match = re.match(r"^(\d+)　(.*)$", text)
    number, label = match.groups() if match else ("", text)
    table = Table([[Paragraph(number, section_number), Paragraph(escape(label), heading)]],
                  colWidths=[26, 478])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), ACCENT), ("LINEBELOW", (1, 0), (1, 0), 0.65, ACCENT),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 8), ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [table, Spacer(1, 3)]


TOTAL_PAGES = [0]

def footer(canvas, document):
    footer.last_page = document.page
    canvas.saveState()
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(0.7)
    canvas.line(45, 41, A4[0] - 45, 41)
    canvas.setFillColor(MID)
    canvas.setFont("ReportSong", 11)
    canvas.drawString(45, 25, "南京大学 · 编译原理")
    total = TOTAL_PAGES[0] or document.page
    canvas.drawRightString(A4[0] - 45, 25, f"第 {document.page} 页 / 共 {total} 页")
    canvas.restoreState()


def build_story():
    """每次调用都产出全新的 flowable 列表，避免复用被 build 消耗过的对象。"""
    story = []
    code_lines = []
    in_code = False
    for raw in (ROOT / "report.md").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), code))
                code_lines = []
            in_code = not in_code
        elif in_code:
            code_lines.append(raw)
        elif line == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif line.startswith("# "):
            story.extend(title_block(line[2:]))
        elif line.startswith("## "):
            story.extend(section(line[3:]))
        elif line.startswith("姓名："):
            story.extend(metadata(line))
        elif line.startswith("• "):
            story.append(Paragraph(escape(line), bullet))
        elif line:
            story.append(Paragraph(escape(line), body))
    return story


def make_doc():
    return SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=45, rightMargin=45,
                             topMargin=31, bottomMargin=50,
                             title="实验二：C-- 语义分析",
                             author="欧睿", subject="GNU Flex / GNU Bison / C99")


OUTPUT.parent.mkdir(parents=True, exist_ok=True)
# 第一遍：只为统计总页数；第二遍：用正确页数输出正式文件。
TOTAL_PAGES[0] = 0
make_doc().build(build_story(), onFirstPage=footer, onLaterPages=footer)
TOTAL_PAGES[0] = footer.last_page
make_doc().build(build_story(), onFirstPage=footer, onLaterPages=footer)
print(OUTPUT, "共", TOTAL_PAGES[0], "页")
