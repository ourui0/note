"""Typora LaTeX style adaptation: readable monochrome Chinese, minimum 11pt."""
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent/'proj2_submission/report.pdf'
pdfmetrics.registerFont(TTFont('Song', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=6))
pdfmetrics.registerFont(TTFont('Hei', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
body=ParagraphStyle('Body',fontName='Song',fontSize=11.2,leading=18.2,wordWrap='CJK',alignment=TA_JUSTIFY,spaceAfter=8,textColor=colors.HexColor('#222222'))
heading=ParagraphStyle('Heading',parent=body,fontName='Hei',fontSize=13,leading=20,spaceBefore=10,spaceAfter=7,keepWithNext=True)
title=ParagraphStyle('Title',parent=heading,fontSize=21,leading=30,alignment=TA_CENTER,spaceBefore=12,spaceAfter=9)
meta=ParagraphStyle('Meta',parent=body,alignment=TA_CENTER,fontSize=11,leading=17,spaceAfter=14)
code=ParagraphStyle('Code',fontName='Courier',fontSize=11,leading=15,spaceBefore=5,spaceAfter=10,leftIndent=8)

def furniture(canvas,doc):
    canvas.saveState(); canvas.setFillColor(colors.HexColor('#555555'))
    canvas.setFont('Hei',11); canvas.drawString(48,A4[1]-32,'南京大学 · 编译原理')
    canvas.setFont('Times-Roman',11); canvas.drawRightString(A4[0]-48,A4[1]-32,'EXPERIMENT 02')
    canvas.setStrokeColor(colors.HexColor('#888888')); canvas.setLineWidth(.5)
    canvas.line(48,A4[1]-40,A4[0]-48,A4[1]-40)
    canvas.line(48,42,A4[0]-48,42)
    canvas.setFont('Song',11); canvas.drawString(48,26,'C-- 语义分析')
    canvas.drawRightString(A4[0]-48,26,f'第 {doc.page} 页'); canvas.restoreState()

story=[]; block=None
for line in (ROOT/'report.md').read_text().splitlines():
    if line.startswith('```'):
        if block is None: block=[]
        else: story.append(Preformatted('\n'.join(block),code)); block=None
    elif block is not None: block.append(line)
    elif line=='<!-- pagebreak -->': story.append(PageBreak())
    elif line.startswith('# '): story.append(Paragraph(escape(line[2:]),title))
    elif line.startswith('## '): story.append(Paragraph(escape(line[3:]),heading))
    elif line.startswith('姓名：'): story.append(Paragraph(escape(line),meta))
    elif line.strip(): story.append(Paragraph(escape(line),body))
doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=49,bottomMargin=55,title='实验二：C-- 语义分析',author='欧睿')
doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
print(OUTPUT)
