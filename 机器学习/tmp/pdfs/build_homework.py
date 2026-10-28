from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUT = Path(__file__).resolve().parents[2] / "output" / "pdf" / "欧睿_241870008_作业一.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

registerFont(TTFont("CJK", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))


class Curve(Flowable):
    def __init__(self, title, xlabel, ylabel, points, color, diagonal=False):
        super().__init__()
        self.width = 12.6 * cm
        self.height = 8.0 * cm
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.points = points
        self.color = color
        self.diagonal = diagonal

    def draw(self):
        c = self.canv
        left, bottom = 1.45 * cm, 1.2 * cm
        width, height = 10.0 * cm, 5.8 * cm
        c.setFont("CJK", 10)
        c.drawCentredString(left + width / 2, bottom + height + 0.45 * cm, self.title)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.8)
        c.line(left, bottom, left + width + 0.25 * cm, bottom)
        c.line(left, bottom, left, bottom + height + 0.18 * cm)
        for i in range(6):
            value = i / 5
            x = left + value * width
            y = bottom + value * height
            c.line(x, bottom - 2, x, bottom + 2)
            c.line(left - 2, y, left + 2, y)
            c.setFont("Times-Roman", 7)
            c.drawCentredString(x, bottom - 0.35 * cm, f"{value:.1f}")
            c.drawRightString(left - 0.18 * cm, y - 2, f"{value:.1f}")
        c.setFont("Times-Roman", 9)
        c.drawString(left + width + 0.33 * cm, bottom - 2, self.xlabel)
        c.drawString(left - 0.18 * cm, bottom + height + 0.22 * cm, self.ylabel)
        if self.diagonal:
            c.setDash(4, 3)
            c.setStrokeColor(colors.HexColor("#9a9a9a"))
            c.line(left, bottom, left + width, bottom + height)
            c.setDash()
        c.setStrokeColor(self.color)
        c.setFillColor(self.color)
        c.setLineWidth(1.7)
        for p, q in zip(self.points, self.points[1:]):
            c.line(left + p[0] * width, bottom + p[1] * height,
                   left + q[0] * width, bottom + q[1] * height)
        for x0, y0 in self.points:
            c.circle(left + x0 * width, bottom + y0 * height, 2.1, fill=1, stroke=0)


def draw_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.5)
        canvas.line(2.1 * cm, h - 1.55 * cm, w - 2.1 * cm, h - 1.55 * cm)
        canvas.setFont("CJK", 9)
        canvas.drawString(2.1 * cm, h - 1.35 * cm, "2026 年秋季")
        canvas.drawCentredString(w / 2, h - 1.35 * cm, "机器学习")
        canvas.drawRightString(w - 2.1 * cm, h - 1.35 * cm, "作业一")
    canvas.setFont("Times-Roman", 9)
    canvas.drawCentredString(w / 2, 1.25 * cm, str(doc.page))
    canvas.restoreState()


styles = getSampleStyleSheet()
body = ParagraphStyle(
    "CNBody", fontName="CJK", fontSize=10.2, leading=16,
    alignment=TA_JUSTIFY, spaceAfter=5,
)
small = ParagraphStyle(
    "CNSmall", parent=body, fontSize=9.2, leading=14, spaceAfter=3,
)
section = ParagraphStyle(
    "CNSection", fontName="CJK", fontSize=17, leading=23,
    alignment=TA_LEFT, spaceBefore=5, spaceAfter=10,
)
answer = ParagraphStyle(
    "CNAnswer", fontName="CJK", fontSize=13, leading=18,
    spaceBefore=8, spaceAfter=7,
)
eq = ParagraphStyle(
    "Equation", fontName="CJK", fontSize=10.5, leading=17,
    alignment=TA_CENTER, spaceBefore=4, spaceAfter=6,
)
note = ParagraphStyle(
    "Question", parent=small, backColor=colors.HexColor("#f4f6f8"),
    borderColor=colors.HexColor("#c9d0d8"), borderWidth=0.5,
    borderPadding=7, spaceBefore=2, spaceAfter=8,
)
title = ParagraphStyle(
    "Title", fontName="CJK", fontSize=25, leading=34,
    alignment=TA_CENTER, spaceAfter=4,
)
subtitle = ParagraphStyle(
    "Subtitle", fontName="CJK", fontSize=17, leading=24,
    alignment=TA_CENTER, spaceAfter=24,
)
identity = ParagraphStyle(
    "Identity", fontName="CJK", fontSize=14, leading=22,
    textColor=colors.blue, alignment=TA_CENTER, spaceAfter=18,
)


def P(text, style=body):
    return Paragraph(text, style)


def equation(text):
    return P(text, eq)


def data_table(rows, widths=None, header=True, font_size=8.6):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="CENTER")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "CJK"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.55, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6"))]
    t.setStyle(TableStyle(commands))
    return t


doc = BaseDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=2.1 * cm, rightMargin=2.1 * cm,
    topMargin=1.85 * cm, bottomMargin=1.75 * cm,
    title="机器学习作业一 - 欧睿 241870008",
    author="欧睿",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=draw_page))
story = []

story += [
    P("姓名：欧睿　　学号：241870008　　日期：2026 年 9 月 24 日", identity),
]

# Section 1
story += [P("一. (30 points) 性能度量", section)]
confusion = [
    ["真实类别 / 预测类别", "第 1 类", "第 2 类", "第 3 类"],
    ["第 1 类", "9", "2", "1"], ["第 2 类", "1", "7", "2"], ["第 3 类", "3", "1", "10"],
]
story += [P("题目：根据下列三分类混淆矩阵，计算准确率，one-vs-rest 下的 micro/macro P、R、F1；并对给定 5 个样例的多标签结果计算同类指标。", note), data_table(confusion, [4.7*cm, 2.0*cm, 2.0*cm, 2.0*cm]), P("解：", answer)]
story += [
    P("1. 样例总数为 12+10+14=36，对角线上正确样例数为 9+7+10=26。"),
    equation("Accuracy = 26/36 = 13/18 ≈ 0.72"),
    P("2. 约定行为真实正/负，列为预测正/负。三个 one-vs-rest 矩阵如下："),
]
ovr = [
    ["类别", "TP", "FN", "FP", "TN"],
    ["第 1 类", "9", "3", "4", "20"], ["第 2 类", "7", "3", "3", "23"], ["第 3 类", "10", "4", "3", "19"],
]
story += [data_table(ovr, [2.4*cm]*5),
    equation("P<sub>1</sub>=9/13,　P<sub>2</sub>=7/10,　P<sub>3</sub>=10/13"),
    equation("R<sub>1</sub>=9/12=3/4,　R<sub>2</sub>=7/10,　R<sub>3</sub>=10/14=5/7"),
    P("汇总后 ΣTP=26、ΣFP=10、ΣFN=10，因而："),
    equation("micro-P = micro-R = 26/36 = 13/18 ≈ 0.72"),
    equation("macro-P = (9/13+7/10+10/13)/3 = 281/390 ≈ 0.72"),
    equation("macro-R = (3/4+7/10+5/7)/3 = 101/140 ≈ 0.72"),
    P("3. 三类的 F1 分别为 18/25、7/10、20/27。"),
    equation("micro-F1 = 13/18 ≈ 0.72"),
    equation("macro-F1 = (18/25+7/10+20/27)/3 = 2917/4050 ≈ 0.72"),
    P("4. 多标签任务中，按标签统计如下："),
]
ml = [
    ["标签", "TP", "FP", "FN", "P", "R", "F1"],
    ["1", "3", "0", "0", "1", "1", "1"],
    ["2", "2", "1", "0", "2/3", "1", "4/5"],
    ["3", "2", "1", "1", "2/3", "2/3", "2/3"],
    ["4", "1", "1", "1", "1/2", "1/2", "1/2"],
]
story += [data_table(ml, [1.6*cm]*7),
    P("汇总得 TP=8、FP=3、FN=2。"),
    equation("micro-P=8/11≈0.73,　micro-R=8/10=0.80,　micro-F1=16/21≈0.76"),
    equation("macro-P=17/24≈0.71,　macro-R=19/24≈0.79,　macro-F1=89/120≈0.74"),
]

# Section 2
story += [P("二. (30 points) 排序与曲线性能度量", section)]
story += [P("题目：10 个样例已按正类置信度降序排列，标签序列为 1,0,1,1,0,0,1,0,1,0。逐步将前 k 个判为正例，求 P-R、ROC 端点及曲线、AUC 和 FPR80。", note), P("解：", answer)]
rank_rows = [
    ["k", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    ["TP", "0", "1", "1", "2", "3", "3", "3", "4", "4", "5", "5"],
    ["FP", "0", "0", "1", "1", "1", "2", "3", "3", "4", "4", "5"],
    ["R/TPR", "0", ".20", ".20", ".40", ".60", ".60", ".60", ".80", ".80", "1", "1"],
    ["P", "1", "1", ".50", ".67", ".75", ".60", ".50", ".57", ".50", ".56", ".50"],
    ["FPR", "0", "0", ".20", ".20", ".20", ".40", ".60", ".60", ".80", ".80", "1"],
]
story += [P("共有 5 个正例和 5 个负例。逐步统计为："), data_table(rank_rows, [1.6*cm]+[1.05*cm]*11, font_size=7.3)]
pr_points = [(0,1),(.2,1),(.2,.5),(.4,.667),(.6,.75),(.6,.6),(.6,.5),(.8,.571),(.8,.5),(1,.556),(1,.5)]
roc_points = [(0,0),(0,.2),(.2,.2),(.2,.4),(.2,.6),(.4,.6),(.6,.6),(.6,.8),(.8,.8),(.8,1),(1,1)]
story += [
    P("1. P-R 端点依次为："),
    P("(0,1), (0.2,1), (0.2,0.5), (0.4,0.667), (0.6,0.75), (0.6,0.6), (0.6,0.5), (0.8,0.571), (0.8,0.5), (1,0.556), (1,0.5)", eq),
    Curve("P-R 曲线", "R", "P", pr_points, colors.HexColor("#1565c0")),
    P("2. ROC 端点依次为："),
    P("(0,0), (0,0.2), (0.2,0.2), (0.2,0.4), (0.2,0.6), (0.4,0.6), (0.6,0.6), (0.6,0.8), (0.8,0.8), (0.8,1), (1,1)", eq),
    Curve("ROC 曲线", "FPR", "TPR", roc_points, colors.HexColor("#c62828"), diagonal=True),
    P("3. 竖直段的水平宽度为 0，每个水平段宽为 0.2。"),
    equation("AUC = 0.2 × (0.2+0.6+0.6+0.8+1.0) = 0.64"),
    P("4. FPR80 表示在检出 80% 正例时误报负例的比例，所以越低越好。在 k=7（纳入 x<sub>7</sub>）时首次达到 TPR=4/5=0.80，此时 FP=3。"),
    equation("FPR80 = FP/N = 3/5 = 0.60"),
]

# Section 3
story += [PageBreak(), P("三. (10 points) 数据预处理", section)]
story += [P("题目：特征值为 18, 21, 24, 27, 30。写出 Min-max 与 Z-score 公式，计算映射到 [-1,1] 的结果与总体标准差定义下的 Z-score，并说明加入 60 后的影响。", note), P("解：", answer)]
story += [
    P("1. 设原特征极值为 x<sub>min</sub>、x<sub>max</sub>，目标区间为 [x'<sub>min</sub>,x'<sub>max</sub>]，则："),
    equation("x' = x'<sub>min</sub> + (x-x<sub>min</sub>)/(x<sub>max</sub>-x<sub>min</sub>) × (x'<sub>max</sub>-x'<sub>min</sub>)"),
    equation("z=(x-μ)/σ,　μ=(1/m)Σx<sub>i</sub>,　σ=√[(1/m)Σ(x<sub>i</sub>-μ)<super>2</super>]"),
    P("2. x<sub>min</sub>=18、x<sub>max</sub>=30，故 x'=-1+(x-18)/12×2=(x-24)/6。"),
    equation("18,21,24,27,30　→　-1, -1/2, 0, 1/2, 1"),
    P("3. 均值 μ=24，总体方差为 [(-6)<super>2</super>+(-3)<super>2</super>+0<super>2</super>+3<super>2</super>+6<super>2</super>]/5=18，所以 σ=3√2。"),
    equation("Z-score = -√2, -1/√2, 0, 1/√2, √2 ≈ -1.41,-0.71,0,0.71,1.41"),
    P("4. 加入 60 后，最小值仍为 18，最大值变为 60。原有点的 Min-max 值变为 x'=-1+(x-18)/21：除 18 仍为 -1 外，其余点向 -1 压缩，30 不再为 1。"),
    P("对 Z-score，均值由 24 升到 30，标准差增大为 √195。原有各点改为 (x-30)/√195：顺序不变，整体向负方向移动，且点与点的间距被压缩。"),
]

# Section 4
story += [PageBreak(), P("四. (30 points) 模型比较检验", section)]
cv = [
    ["实验", "A 第 1 折", "B 第 1 折", "A 第 2 折", "B 第 2 折"],
    ["1", "0.18", "0.24", "0.22", "0.26"], ["2", "0.20", "0.25", "0.19", "0.22"],
    ["3", "0.17", "0.24", "0.23", "0.26"], ["4", "0.21", "0.25", "0.20", "0.22"],
    ["5", "0.16", "0.22", "0.21", "0.25"],
]
story += [P("题目：根据下列 5×2 交叉验证错误率，以 Δ=E<sub>A</sub>-E<sub>B</sub> 计算成对差值、每次均值与方差，再计算题定 t 统计量，在 α=0.05 和 0.01 下判断差异。", note), data_table(cv, [1.6*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]), P("解：", answer)]
story += [
    P("1. 不同数据划分的难度不同。把 A 和 B 在同一训练/测试划分上的错误率相减，能抵消划分难度的共同影响，使差值主要反映学习器本身。"),
    P("普通 k 折交叉验证的训练集大量重叠，各折差值并不独立，直接配对 t 检验可能低估方差。5×2 方法做 5 次尽量独立的随机二分，每次交换训练集与测试集，并用两折差值估计当次变异，因而更谨慎地处理重采样的相关性与方差估计问题。"),
    P("2. 按 Δ=E<sub>A</sub>-E<sub>B</sub> 逐行计算："),
]
diff = [
    ["i", "Δᵢ⁽¹⁾", "Δᵢ⁽²⁾", "Δ̅ᵢ", "σᵢ²"],
    ["1", "-0.06", "-0.04", "-0.05", "0.0002"],
    ["2", "-0.05", "-0.03", "-0.04", "0.0002"],
    ["3", "-0.07", "-0.03", "-0.05", "0.0008"],
    ["4", "-0.04", "-0.02", "-0.03", "0.0002"],
    ["5", "-0.06", "-0.04", "-0.05", "0.0002"],
]
story += [data_table(diff, [1.4*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.2*cm]),
    P("例如第 1 次：Δ̅<sub>1</sub>=(-0.06-0.04)/2=-0.05，σ<sub>1</sub><super>2</super>=(-0.06+0.05)<super>2</super>+(-0.04+0.05)<super>2</super>=0.0002。"),
    P("3. 五个方差的和为 0.0016，所以："),
    equation("τ<sub>t</sub> = -0.05 / √(0.0016/5) = -0.05/√0.00032 ≈ -2.80"),
    P("4. 双边检验比较 |τ<sub>t</sub>|=2.80 与临界值："),
    P("• α=0.05：2.80&gt;2.5706，拒绝 H<sub>0</sub>，认为两学习器存在显著性能差异。"),
    P("• α=0.01：2.80&lt;4.0321，不拒绝 H<sub>0</sub>，证据不足以在 1% 水平下认定性能不同。"),
    P("在 α=0.05 的显著结论中，各次均值均为负且 τ<sub>t</sub>&lt;0，即 A 的错误率显著低于 B，因而学习器 A 更优。"),
]

doc.build(story)
print(OUT)
