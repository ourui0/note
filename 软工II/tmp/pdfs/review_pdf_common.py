from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
SLIDES = ROOT / "tmp" / "pdfs" / "slides"
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"

pdfmetrics.registerFont(TTFont("STHeiti", FONT))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CN", parent=styles["Normal"], fontName="STHeiti", fontSize=10.2, leading=15.4, wordWrap="CJK", textColor=colors.HexColor("#1f2937"), spaceAfter=5))
styles.add(ParagraphStyle(name="Small", parent=styles["CN"], fontSize=8.75, leading=12.4, textColor=colors.HexColor("#374151")))
styles.add(ParagraphStyle(name="TitleCN", parent=styles["Title"], fontName="STHeiti", fontSize=26, leading=33, alignment=TA_CENTER, textColor=colors.HexColor("#111827"), spaceAfter=14))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["CN"], fontSize=12.4, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#4b5563"), spaceAfter=18))
styles.add(ParagraphStyle(name="H1CN", parent=styles["Heading1"], fontName="STHeiti", fontSize=17, leading=23, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="H2CN", parent=styles["Heading2"], fontName="STHeiti", fontSize=13.2, leading=18, textColor=colors.HexColor("#1e3a8a"), spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="BoxTitle", parent=styles["CN"], fontSize=11.5, leading=15, textColor=colors.HexColor("#111827"), spaceAfter=4))
styles.add(ParagraphStyle(name="CodeCN", parent=styles["Code"], fontName="Courier", fontSize=7.25, leading=9.5, textColor=colors.HexColor("#111827")))


def p(text, style="CN"):
    return Paragraph(text, styles[style])


def h1(text):
    return Paragraph(text, styles["H1CN"])


def h2(text):
    return Paragraph(text, styles["H2CN"])


def bullets(items):
    return ListFlowable(
        [ListItem(p(item), leftIndent=10) for item in items],
        bulletType="bullet",
        leftIndent=16,
        bulletFontName="STHeiti",
        bulletFontSize=8,
        bulletColor=colors.HexColor("#2563eb"),
    )


def numbered(items):
    return ListFlowable(
        [ListItem(p(item), leftIndent=12) for item in items],
        bulletType="1",
        leftIndent=18,
        bulletFontName="STHeiti",
        bulletFontSize=9,
    )


def table(rows, widths=None, small=True):
    style_name = "Small" if small else "CN"
    data = [[cell if hasattr(cell, "wrapOn") else p(str(cell), style_name) for cell in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "STHeiti"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def note(title, body):
    t = Table([[p(f"<b>{title}</b>", "BoxTitle")], [p(body, "Small")]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#93c5fd")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 7)])


def img(path, caption, width=15.7 * cm, max_height=9.2 * cm):
    if not path.exists():
        return []
    im = Image(str(path))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    if im.drawHeight > max_height:
        im.drawHeight = max_height
        im.drawWidth = im.drawHeight / ratio
    return [Spacer(1, 5), im, p(caption, "Small"), Spacer(1, 5)]


def slide(group, page, caption, width=15.7 * cm, max_height=9.2 * cm):
    return img(SLIDES / group / f"page-{page:02d}.png", caption, width, max_height)


def code(text):
    t = Table([[Preformatted(text.strip("\n"), styles["CodeCN"])]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def header_footer(title):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setFont("STHeiti", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(1.7 * cm, 1.0 * cm, f"软件工程II 期末复习 - {title}")
        canvas.drawRightString(19.3 * cm, 1.0 * cm, f"{doc.page}")
        canvas.restoreState()
    return draw
