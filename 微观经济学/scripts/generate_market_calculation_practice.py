from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/市场相关计算题集合练习_第六章重点含第八章.pdf"


def para(text, style):
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def make_styles():
    font_name = "STHeitiEmbedded"
    pdfmetrics.registerFont(TTFont(font_name, "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("CoverTitle", fontName=font_name, fontSize=24, leading=32, alignment=TA_CENTER, textColor=colors.HexColor("#111827")))
    styles.add(ParagraphStyle("CoverSub", fontName=font_name, fontSize=14, leading=22, alignment=TA_CENTER, textColor=colors.HexColor("#374151")))
    styles.add(ParagraphStyle("H1", fontName=font_name, fontSize=15.2, leading=22, spaceBefore=8, spaceAfter=7, textColor=colors.HexColor("#111827"), keepWithNext=True))
    styles.add(ParagraphStyle("H2", fontName=font_name, fontSize=12.6, leading=18, spaceBefore=6, spaceAfter=5, textColor=colors.HexColor("#111827"), keepWithNext=True))
    styles.add(ParagraphStyle("Body", fontName=font_name, fontSize=10.0, leading=15.0, wordWrap="CJK", alignment=TA_LEFT, spaceAfter=3.5))
    styles.add(ParagraphStyle("Small", fontName=font_name, fontSize=9.0, leading=12.8, wordWrap="CJK", alignment=TA_LEFT, spaceAfter=2.5))
    styles.add(ParagraphStyle("Tiny", fontName=font_name, fontSize=8.6, leading=12, wordWrap="CJK", alignment=TA_CENTER))
    return styles, font_name


class Doc(BaseDocTemplate):
    def __init__(self, filename, font_name):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=21 * mm,
            rightMargin=21 * mm,
            topMargin=19 * mm,
            bottomMargin=17 * mm,
            title="市场相关计算题集合练习",
            author="Codex",
        )
        self.font_name = font_name
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self.header_footer)])

    def header_footer(self, canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont(self.font_name, 8.8)
            canvas.setFillColor(colors.HexColor("#6b7280"))
            canvas.drawString(doc.leftMargin, A4[1] - 11.5 * mm, "市场相关计算题集合练习")
            canvas.drawRightString(A4[0] - doc.rightMargin, 9.5 * mm, f"第 {doc.page} 页")
        canvas.restoreState()


def table(data, widths, style):
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(style)
    return t


def relation_tables(styles):
    story = []
    story.append(para("一、关键情况与公式关系速查", styles["H1"]))
    story.append(para("第六章的计算题不要先背零散公式，先判断两个市场：产品市场决定“收益边”，要素市场决定“成本边”。最根本的原则是：多用一单位要素带来的新增收益 = 多用一单位要素增加的成本，即 MRP=MFC。", styles["Body"]))

    data = [
        [para("判断对象", styles["Tiny"]), para("完全竞争", styles["Tiny"]), para("不完全竞争/买方垄断", styles["Tiny"]), para("物理意义", styles["Tiny"])],
        [para("产品市场", styles["Small"]), para("MR=P，所以 MRP=VMP=P×MP", styles["Small"]), para("MR<P，通常用 MRP=MR×MP", styles["Small"]), para("多生产出来的产品，能给厂商带来多少新增收益", styles["Small"])],
        [para("要素市场", styles["Small"]), para("MFC=W", styles["Small"]), para("MFC>W。若 W=a+bL，则 TFC=WL=aL+bL²，MFC=a+2bL", styles["Small"]), para("多雇一单位要素，总要素成本增加多少", styles["Small"])],
    ]
    story.append(table(data, [24 * mm, 43 * mm, 55 * mm, 45 * mm], TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])))
    story.append(Spacer(1, 3 * mm))
    story.append(para("常用符号解释：", styles["H2"]))
    rows = [
        ("MP 或 MPL", "边际产量，MP=ΔQ/ΔL。多用一单位要素，多生产多少产品；若要素是劳动，常写 MPL。"),
        ("MR", "边际收益，MR=ΔTR/ΔQ。多卖一单位产品，总收益增加多少。完全竞争时 MR=P；垄断时通常 MR<P。"),
        ("VMP", "边际产品价值，VMP=P×MP。多用一单位要素带来的新增产量，按产品价格计算值多少钱。"),
        ("MRP", "边际收益产品，MRP=MR×MP。多用一单位要素，使厂商总收益真正增加多少。"),
        ("MFC", "边际要素成本，MFC=ΔTFC/ΔL。多用一单位要素，厂商总要素成本增加多少。不是固定成本 FC。"),
        ("W", "要素价格。若要素是劳动，W 是工资率。要素市场完全竞争时 MFC=W。"),
    ]
    data2 = [[para("符号", styles["Tiny"]), para("含义与计算", styles["Tiny"])]] + [[para(a, styles["Small"]), para(b, styles["Small"])] for a, b in rows]
    story.append(table(data2, [28 * mm, 137 * mm], TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])))
    story.append(Spacer(1, 3 * mm))
    story.append(para("求值顺序口诀：先看产品市场选 VMP 或 MRP；再看要素市场选 W 或 MFC；最后令收益边 = 成本边。需要价格时由需求函数求 P，需要产量时由生产函数或需求函数反推。", styles["Body"]))
    return story


problems6 = [
    {
        "title": "1. 产品市场和要素市场均为完全竞争",
        "q": "某完全竞争厂商使用劳动 L 生产产品，短期生产函数为 Q=20L-L²，产品价格 P=5，工资率 W=40。求利润最大化的劳动使用量、产量和扣除工资后的收益余额。",
        "a": "解析：产品市场完全竞争，所以 MR=P，收益边用 VMP=P×MPL。MPL=dQ/dL=20-2L。\nVMP=5(20-2L)=100-10L。要素市场完全竞争，所以 MFC=W=40。\n令 VMP=W：100-10L=40，得 L=6。\nQ=20×6-6²=84。总收益 TR=5×84=420，工资成本=40×6=240，扣除工资后的收益余额=180。\n答案：L=6，Q=84，余额为180。"
    },
    {
        "title": "2. 产品市场不完全竞争、要素市场完全竞争",
        "q": "某卖方垄断厂商的产品需求函数为 P=100-Q，生产函数为 Q=10L，工资率 W=200。求利润最大化时的劳动雇用量、产量和产品价格。",
        "a": "解析：产品市场不完全竞争，所以用 MRP=MR×MPL。由 P=100-Q 得 TR=(100-Q)Q=100Q-Q²，MR=100-2Q。\n又 Q=10L，所以 MPL=10，且 MR=100-20L。\nMRP=(100-20L)×10=1000-200L。要素市场完全竞争，所以 MFC=W=200。\n令 MRP=W：1000-200L=200，得 L=4。\nQ=10×4=40，P=100-40=60。\n答案：L=4，Q=40，P=60。"
    },
    {
        "title": "3. 产品市场完全竞争、要素市场买方垄断",
        "q": "某厂商在产品市场是完全竞争者，在劳动市场是买方垄断者。劳动供给函数为 W=20+2L，劳动的边际产品价值 VMP 恒为60。求最优劳动雇用量和工资。",
        "a": "解析：产品市场完全竞争，收益边用 VMP。要素市场买方垄断，不能用 VMP=W，而要用 VMP=MFC。\n总要素成本 TFC=WL=(20+2L)L=20L+2L²。\nMFC=dTFC/dL=20+4L。\n令 VMP=MFC：60=20+4L，得 L=10。\n工资 W=20+2×10=40。\n答案：L=10，W=40。"
    },
    {
        "title": "4. 卖方垄断下由 MRP 反求价格",
        "q": "某厂商为卖方垄断，产品需求函数为 P=160-10Q，生产要素价格为300。已知利润最大化时该要素的边际产量 MP=15，求产品价格。",
        "a": "解析：卖方垄断说明产品市场不完全竞争，使用 MRP=MR×MP。要素市场若工资既定，则 MRP=W。\nMR×15=300，得 MR=20。\n由 P=160-10Q 得 TR=(160-10Q)Q=160Q-10Q²，MR=160-20Q。\n令 160-20Q=20，得 Q=7。\n代回需求函数：P=160-10×7=90。\n答案：P=90。"
    },
    {
        "title": "5. 买方垄断下不能直接令 VMP=W",
        "q": "某厂商在产品市场是完全竞争者，在要素市场是垄断者。已知要素供给函数 W=30+10L，该要素的边际产品价值 VMP=90。求最优要素使用量。",
        "a": "解析：产品市场完全竞争，收益边为 VMP。要素市场买方垄断，要用 MFC，而不是直接用 W。\nTFC=WL=(30+10L)L=30L+10L²。\nMFC=dTFC/dL=30+20L。\n令 VMP=MFC：90=30+20L，得 L=3。\n若误用 VMP=W，会得 L=6，这是把买方垄断错当成要素市场完全竞争。\n答案：L=3。"
    },
    {
        "title": "6. 由生产函数求劳动需求函数",
        "q": "某完全竞争厂商生产函数为 Q=40L^0.5，产品价格 P=20，工资率为 W。求该厂商的劳动需求函数，并求 W=100 时的劳动需求量。",
        "a": "解析：完全竞争产品市场和要素市场下，劳动需求由 VMP=W 决定。\nMPL=dQ/dL=20L^(-0.5)=20/√L。\nVMP=P×MPL=20×20/√L=400/√L。\n令 400/√L=W，得 √L=400/W，所以 L=(400/W)²。\n当 W=100 时，L=(400/100)²=16。\n答案：劳动需求函数 L=(400/W)²；W=100 时 L=16。"
    },
    {
        "title": "7. 由总产量表判断是否继续雇用",
        "q": "某完全竞争厂商产品价格 P=8，工资 W=40。劳动投入 L=1,2,3,4,5 时，总产量 Q 分别为 10,18,24,28,30。求每一单位劳动的 VMP，并判断最优雇用量。",
        "a": "解析：先求 MPL：第1至第5个工人的边际产量分别为10,8,6,4,2。\nVMP=P×MPL，所以分别为80,64,48,32,16。\n完全竞争要素市场下雇用到 VMP 不低于 W 且下一单位低于 W 的位置。\n第3个工人的 VMP=48>40，第4个工人的 VMP=32<40，所以最优雇用量为 L=3。\n答案：VMP 依次为80,64,48,32,16；最优 L=3。"
    },
    {
        "title": "8. 土地供给固定与地租",
        "q": "某地土地总供给固定为10单位，土地需求函数为 R=100-5T，其中 R 为每单位土地地租，T 为土地使用量。求均衡地租和土地总租金。",
        "a": "解析：土地供给固定，供给曲线垂直，土地数量由供给决定，地租主要由需求决定。\nT=10，代入需求函数：R=100-5×10=50。\n土地总租金=R×T=50×10=500。\n答案：均衡地租 R=50，土地总租金=500。"
    },
    {
        "title": "9. 经济租金的计算",
        "q": "某生产要素当前收入为每单位80元，其转移收入即机会成本为每单位50元。若使用量为20单位，求该要素的经济租金总额。",
        "a": "解析：经济租金是要素收入中超过机会成本的部分。\n每单位经济租金=80-50=30。\n总经济租金=30×20=600。\n答案：经济租金总额为600。"
    },
    {
        "title": "10. 同时存在垄断产品市场与买方垄断要素市场",
        "q": "某厂商产品需求函数为 P=120-Q，生产函数为 Q=5L，劳动供给函数为 W=20+L。求利润最大化的 L、Q、P 和 W。",
        "a": "解析：产品市场不完全竞争，用 MRP=MR×MPL。P=120-Q，所以 MR=120-2Q。Q=5L，MPL=5，因此 MR=120-10L。\nMRP=(120-10L)×5=600-50L。\n要素市场买方垄断，用 MFC。TFC=WL=(20+L)L=20L+L²，MFC=20+2L。\n令 MRP=MFC：600-50L=20+2L，得 580=52L，L=145/13≈11.15。\nQ=5L=725/13≈55.77。P=120-Q≈64.23。W=20+L≈31.15。\n答案：L≈11.15，Q≈55.77，P≈64.23，W≈31.15。"
    },
]


problems8 = [
    {
        "title": "11. 负外部性与庇古税",
        "q": "某商品市场需求为 P=100-Q，私人边际成本 MPC=20+Q，生产带来的边际外部成本 MEC=10。求市场均衡产量、社会有效产量和应征收的单位庇古税。",
        "a": "解析：市场均衡按私人边际成本决定：100-Q=20+Q，得 Qm=40。\n社会边际成本 MSC=MPC+MEC=30+Q。社会有效产量满足 MSB=MSC，即 100-Q=30+Q，得 Q*=35。\n理想庇古税等于效率产量处的边际外部成本。本题 MEC 恒为10，所以 t=10。\n答案：市场产量40，社会有效产量35，庇古税10。"
    },
    {
        "title": "12. 正外部性与补贴",
        "q": "某教育服务需求即私人边际收益 MPB=80-Q，私人边际成本 MPC=20+Q，边际外部收益 MEB=20。求市场均衡数量、社会有效数量和单位补贴。",
        "a": "解析：市场均衡由 MPB=MPC：80-Q=20+Q，得 Qm=30。\n社会边际收益 MSB=MPB+MEB=100-Q。社会有效数量满足 MSB=MPC：100-Q=20+Q，得 Q*=40。\n理想补贴等于效率数量处的边际外部收益，本题 MEB 恒为20，所以补贴 s=20。\n答案：市场数量30，社会有效数量40，单位补贴20。"
    },
    {
        "title": "13. 公共物品的纵向加总",
        "q": "社会有两个消费者，公共物品数量为 G。甲的边际支付意愿为 MB1=60-G，乙的边际支付意愿为 MB2=40-G。公共物品边际成本 MC=50。求有效供给量 G。",
        "a": "解析：公共物品具有非竞争性，同一数量 G 被多人共同消费，所以社会边际收益要纵向加总：MSB=MB1+MB2=(60-G)+(40-G)=100-2G。\n有效供给满足 MSB=MC：100-2G=50，得 G=25。\n注意：私人物品是横向加总需求，公共物品是纵向加总边际支付意愿。\n答案：G=25。"
    },
    {
        "title": "14. 洛伦兹曲线与基尼系数的近似计算",
        "q": "某社会人口按五等分分组，累计人口比例为 0,0.2,0.4,0.6,0.8,1.0；累计收入比例为 0,0.05,0.15,0.30,0.55,1.0。用梯形面积法近似计算基尼系数。",
        "a": "解析：基尼系数 G=1-2×洛伦兹曲线下方面积。\n每段宽度均为0.2，梯形面积分别为：\n(0+0.05)/2×0.2=0.005；(0.05+0.15)/2×0.2=0.020；(0.15+0.30)/2×0.2=0.045；(0.30+0.55)/2×0.2=0.085；(0.55+1.00)/2×0.2=0.155。\n面积合计 A=0.310。\nG=1-2A=1-0.620=0.380。\n答案：基尼系数约为0.38。"
    },
]


def add_problem(story, item, styles):
    story.append(KeepTogether([
        para(item["title"], styles["H2"]),
        para(item["q"], styles["Body"]),
    ]))
    story.append(para(item["a"], styles["Small"]))
    story.append(Spacer(1, 1.8 * mm))


def build_pdf():
    styles, font_name = make_styles()
    story = []
    story.extend([
        Spacer(1, 42 * mm),
        para("市场相关计算题集合练习", styles["CoverTitle"]),
        Spacer(1, 6 * mm),
        para("第六章重点：生产要素市场与收入分配", styles["CoverSub"]),
        para("附：第八章可计算题型判断与典型练习", styles["CoverSub"]),
        Spacer(1, 14 * mm),
    ])
    meta = [
        ["题型", "计算题；按“题目-解析/解题思路-答案”编排"],
        ["重点", "MFC、MRP、MP、MR、MPL、VMP 的关系与求值"],
        ["第八章判断", "适合出计算题，但范围集中在外部性、公共物品、基尼系数等"],
        ["参考", "题型表达参考《作业答案汇总》"],
    ]
    meta_table = Table([[para(a, styles["Body"]), para(b, styles["Body"])] for a, b in meta], colWidths=[32 * mm, 118 * mm], hAlign="CENTER")
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    story.extend(relation_tables(styles))
    story.append(PageBreak())

    story.append(para("二、第六章重点计算题", styles["H1"]))
    story.append(para("本部分按作业答案式写法展开。每题先判断市场状态，再确定左边收益项与右边成本项，最后代入求解。", styles["Body"]))
    for p in problems6:
        add_problem(story, p, styles)

    story.append(Spacer(1, 5 * mm))
    story.append(para("三、第八章是否适合出计算题？", styles["H1"]))
    story.append(para("适合，但不是所有内容都适合。第八章的选择题和概念题更多；计算题通常集中在以下四类：1. 负外部性与庇古税；2. 正外部性与补贴；3. 公共物品的社会边际收益加总；4. 洛伦兹曲线与基尼系数。信息不对称、道德风险、逆向选择通常更适合概念判断题。", styles["Body"]))
    story.append(para("四、第八章典型计算题", styles["H1"]))
    for p in problems8:
        add_problem(story, p, styles)

    story.append(Spacer(1, 4 * mm))
    story.append(para("复习提醒：第六章计算题的本质是“新增收益与新增成本比较”；第八章计算题的本质是“私人条件与社会条件比较”。", styles["Small"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Doc(str(OUT), font_name)
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build_pdf()
