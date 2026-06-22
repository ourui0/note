from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "软件工程II测试篇复习.pdf"
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


def img(name, caption, width=15.7 * cm):
    path = SLIDES / name
    if not path.exists():
        return []
    im = Image(str(path))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    if im.drawHeight > 9.2 * cm:
        im.drawHeight = 9.2 * cm
        im.drawWidth = im.drawHeight / ratio
    return [Spacer(1, 5), im, p(caption, "Small"), Spacer(1, 5)]


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


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("STHeiti", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(1.7 * cm, 1.0 * cm, "软件工程II 期末复习 - 测试篇")
    canvas.drawRightString(19.3 * cm, 1.0 * cm, f"{doc.page}")
    canvas.restoreState()


story = []
story.append(Spacer(1, 2.2 * cm))
story.append(p("软件工程II", "Subtitle"))
story.append(Paragraph("测试篇期末复习", styles["TitleCN"]))
story.append(p("依据：软件测试课件，123.txt 答疑转写，考试题目类型与重点，2020/2022 往年卷测试题。", "Subtitle"))
story.append(note("使用建议", "测试题主要考“会不会选测试用例”。不要只背概念，要能从规格或代码中找边界、条件、路径，并写成清晰的测试用例表。"))
story.append(PageBreak())

story.append(h1("一、考试定位与优先级"))
story.append(table([
    ["优先级", "内容", "依据", "答题产物"],
    ["高", "黑盒测试：等价类划分、边界值分析", "2020 测试题直接考边界值；课件重点", "输入值、预期输出、覆盖理由"],
    ["高", "白盒测试：语句覆盖、条件覆盖、路径覆盖", "2022 测试题考条件覆盖；课件重点", "覆盖目标 + 最小测试用例集"],
    ["中高", "圈复杂度", "2022 测试题和构造篇均涉及", "判定节点数 + 1，或控制流图 E-N+2"],
    ["中", "测试级别：单元、集成、系统、验收、回归", "课件基本概念；大作业链路也会涉及", "每一级测什么、依据什么、是否需要桩/驱动"],
    ["中", "测试用例选择与 AI 辅助测试", "课程新版内容", "AI 可生成，但人要审查边界、约束和检错能力"],
    ["低", "测试相关图", "答疑说图相关不用考虑", "不作为本篇重点"],
], widths=[2.0 * cm, 4.7 * cm, 5.0 * cm, 4.7 * cm]))
story.append(note("考试提醒", "答疑中“测试相关的图不用考虑吧”的回复意味着测试篇不必把状态图、协作图等图形测试方法作为核心。更应该把时间放在边界值、等价类、条件覆盖、路径覆盖这些能落到测试用例的内容上。"))

story.append(h1("二、软件测试基础"))
story.append(h2("1. 软件测试的目标"))
story.append(bullets([
    "测试是为了发现缺陷，而不是证明程序没有缺陷。",
    "测试验证两件事：是否在构建正确的东西，是否把东西构建正确。",
    "测试用例通常包括：输入、执行条件、测试步骤、预期结果，必要时还包括实际结果和通过/失败判定。",
    "好的测试用例要有明确目的，能覆盖风险高、容易出错或需求关键的场景。",
]))
story.extend(img("testing/page-32.png", "课件截图：测试技术。考试主要落在黑盒测试方法和白盒测试方法。"))
story.append(h2("2. 测试级别"))
story.append(table([
    ["级别", "关注点", "依据/对象", "是否常用桩和驱动"],
    ["单元测试", "单个函数、类、模块是否正确", "详细设计、代码、接口契约", "常用桩和驱动隔离依赖"],
    ["集成测试", "模块之间接口、调用顺序、数据传递是否正确", "体系结构设计、接口设计、协作关系", "常用桩和驱动；自顶向下/自底向上"],
    ["系统测试", "整个系统是否满足需求", "需求规格、用例文档、非功能需求", "通常不依赖桩和驱动"],
    ["验收测试", "用户是否认可系统满足业务目标", "业务需求、验收标准、真实场景", "由用户或代表参与"],
    ["回归测试", "修改后原有功能是否被破坏", "已有有效测试用例集、变更影响范围", "自动化很重要"],
], widths=[2.3 * cm, 4.4 * cm, 5.0 * cm, 4.7 * cm]))
story.extend(img("testing/page-31.png", "课件截图：系统测试。系统测试以需求规格说明或用例文档为基础。"))

story.append(PageBreak())
story.append(h1("三、黑盒测试"))
story.append(p("黑盒测试基于规格说明设计测试用例，不关心程序内部代码结构。考试中看到业务规则、输入范围、输出范围时，优先想到黑盒测试。"))
story.append(h2("1. 等价类划分"))
story.append(bullets([
    "把输入域划分为若干等价类，认为同一类中的数据对程序行为具有相同代表性。",
    "有效等价类：符合规格说明、合理有意义的数据集合。",
    "无效等价类：不符合规格说明、非法或异常的数据集合。",
    "设计用例时至少覆盖每个有效等价类，并尽量让每个无效等价类单独出现，便于定位原因。",
]))
story.extend(img("testing/page-37.png", "课件截图：等价类划分。有效等价类用于检验程序是否实现规格说明中的功能和性能。"))
story.append(h2("2. 边界值分析"))
story.append(bullets([
    "边界值分析关注输入或输出等价类的边界及边界附近，因为错误最容易发生在边界。",
    "常用取值：最小值、最小值+1、最大值-1、最大值；必要时加入刚低于最小值、刚高于最大值。",
    "如果规则分段，例如 3、7、10、15、20 天，就在每个分界点附近取值。",
    "如果题目规格有空洞或歧义，应在答案中指出，并设计测试用例暴露该问题。",
]))
story.extend(img("testing/page-40.png", "课件截图：边界值分析。2020 测试题正是这种类型。"))
story.append(h2("3. 决策表与状态转换"))
story.append(bullets([
    "决策表适合多个条件组合决定多个动作的业务规则，例如优惠、权限、审批。",
    "状态转换测试适合对象有明确状态和事件，例如订单、借阅、账户冻结/解冻。",
    "本次复习中图相关不是重点，但要知道它们都属于基于规格的黑盒测试方法。",
]))

story.append(PageBreak())
story.append(h1("四、白盒测试"))
story.append(p("白盒测试基于代码结构设计测试用例，关注语句、分支、条件、路径是否被执行。考试中看到代码片段、if/while/&&/|| 时，优先想到白盒覆盖。"))
story.append(h2("1. 常见覆盖准则"))
story.append(table([
    ["覆盖准则", "含义", "答题抓手"],
    ["语句覆盖", "每条语句至少执行一次", "找一组能让所有语句跑到的输入"],
    ["判定/分支覆盖", "每个判定的真、假分支至少执行一次", "每个 if/while 至少 T/F 各一次"],
    ["条件覆盖", "每个判定中每个原子条件的真、假至少满足一次", "拆出 C1、C2、C3；注意短路求值"],
    ["路径覆盖", "每条独立执行路径至少执行一次", "根据控制流图或分支组合列路径"],
], widths=[3.0 * cm, 6.2 * cm, 7.2 * cm]))
story.extend(img("testing/page-47.png", "课件截图：语句覆盖。语句覆盖最弱，只要求每行代码至少执行一次。"))
story.extend(img("testing/page-51.png", "课件截图：条件覆盖。2022 测试题的关键词就是条件覆盖。"))
story.extend(img("testing/page-52.png", "课件截图：路径覆盖。路径覆盖更强，但路径数量可能很快膨胀。"))
story.append(h2("2. 短路求值"))
story.append(bullets([
    "`A && B && C` 中，如果 A 为假，B 和 C 不会被求值。",
    "`A || B || C` 中，如果 A 为真，B 和 C 不会被求值。",
    "做条件覆盖时，不能只让某个条件在逻辑上可能为真/假，还要确保程序实际求值到该条件。",
    "因此为了让后面的条件出现假值，前面的条件必须先被设计为真。",
]))
story.append(h2("3. 圈复杂度"))
story.append(bullets([
    "快速算法：圈复杂度 V(G) = 判定节点数 + 1。",
    "判定节点通常包括 if、else if、while、for、case、catch，以及复杂布尔表达式中独立判断的拆分口径。",
    "控制流图算法：V(G) = E - N + 2P。单个连通程序片段中 P=1。",
    "考试常用结论：圈复杂度越高，独立路径越多，测试和维护成本越高。",
]))

story.append(h1("五、基于用例的系统测试"))
story.append(p("系统测试的功能测试计划可以以需求规格说明或用例文档为基础。基于用例的测试不是让你重画用例图，而是从用例主成功场景、扩展场景和异常场景中提取测试用例。"))
story.append(table([
    ["来源", "测试关注点", "示例"],
    ["用例前置条件", "条件不满足时系统是否拒绝或提示", "未登录时不能充值"],
    ["主成功场景", "正常流程能否完成", "选择充值 - 输入金额 - 支付成功 - 更新余额"],
    ["扩展场景", "可选流程、分支流程是否正确", "选择不同支付方式、取消支付"],
    ["异常场景", "错误输入和外部失败是否处理", "金额为负、支付失败、网络超时"],
    ["后置条件", "状态和数据是否一致", "余额增加、交易记录生成、失败不扣款"],
], widths=[3.2 * cm, 6.2 * cm, 7.0 * cm]))
story.append(note("和需求篇的关系", "需求题要求你会写用例；测试题则要求你能把用例转换成测试。一个完整用例至少可以派生正常、边界、异常、权限、状态一致性等测试场景。"))

story.append(h1("六、AI 辅助测试的答题口径"))
story.append(bullets([
    "AI 可以辅助生成测试框架、等价类、边界值、决策表、状态转换测试用例，也可以根据代码生成白盒覆盖用例。",
    "AI 输出不能直接相信，需要人工检查：是否遗漏业务约束、是否覆盖边界、预期结果是否正确、是否只追求覆盖率而检错能力弱。",
    "高风险模块、支付/安全/隐私等关键逻辑应保留人工审查和关键测试用例。",
    "可以用覆盖率报告、历史缺陷、代码变更范围来让 AI 帮助补充回归测试。",
]))
story.extend(img("testing/page-53.png", "课件截图：大模型辅助白盒测试与覆盖率提升。重点是辅助，不是替代工程判断。"))

story.append(PageBreak())
story.append(h1("七、例题与参考答案"))
story.append(h2("例题 1：2020 仓库订货规则边界值测试"))
story.append(p("题目核心：供应商交货期天数为输入，备货销量天数为返回值。规则分界点为 3、7、10、15、20 天，要求用边界值法设计测试。"))
story.append(table([
    ["测试编号", "输入交货期", "预期结果", "覆盖理由"],
    ["T1", "2", "7 天销量", "低于 3 的边界附近"],
    ["T2", "3", "7 天销量", "3 天以内的边界值，按“以内”理解为 <=3"],
    ["T3", "4", "15 天销量", "刚超过 3，进入 7 天以内区间"],
    ["T4", "6", "15 天销量", "低于 7 的边界附近"],
    ["T5", "7", "15 天销量", "7 天以内的边界值"],
    ["T6", "8", "20 天销量", "刚超过 7，进入 10 天以内区间"],
    ["T7", "9", "20 天销量", "低于 10 的边界附近"],
    ["T8", "10", "20 天销量", "10 天以内的边界值"],
    ["T9", "11", "30 天销量", "刚超过 10，进入 15 天以内区间"],
    ["T10", "14", "30 天销量", "低于 15 的边界附近"],
    ["T11", "15", "30 天销量", "15 天以内的边界值"],
    ["T12", "16", "需求需澄清/应有明确规则", "15 到 20 之间存在规格空洞"],
    ["T13", "19", "需求需澄清/应有明确规则", "刚低于 20，继续暴露规格空洞"],
    ["T14", "20", "40 天销量", "20 天以上的边界值，按“以上”理解为 >=20"],
    ["T15", "21", "40 天销量", "刚超过 20"],
], widths=[2.0 * cm, 2.6 * cm, 4.8 * cm, 7.0 * cm]))
story.append(note("答题加分点", "如果题目只要求设计测试用例，可以给出边界表；如果允许评价需求，应指出 15<交货期<20 的规则没有定义，真实项目中必须澄清需求，否则无法判断预期输出。"))

story.append(PageBreak())
story.append(h2("例题 2：2022 条件覆盖和圈复杂度"))
story.append(code("""
if (new1.indexOf(new2) != -1
    && old.indexOf(new1) == -1
    && new2.indexOf(new1) != -1
    && new1.indexOf(old) == -1) {
    if (dao.loginUser(username, old)) {
        dao.rePassword(new1);
        writer.print("yes");
    } else {
        writer.print("no");
    }
} else {
    writer.print("no");
}
"""))
story.append(h2("1. 圈复杂度"))
story.append(p("若按两个 if 判定计算，圈复杂度 = 2 + 1 = 3。若按复杂布尔表达式中的每个 `&&` 条件拆分为独立判定，则外层 4 个原子条件 + 内层 loginUser 共 5 个判定，圈复杂度 = 5 + 1 = 6。考试中如果题目强调短路条件覆盖，建议说明采用拆分原子条件的口径。"))
story.append(h2("2. 100% 条件覆盖测试用例"))
story.append(p("令 C1: new1 包含 new2；C2: old 不包含 new1；C3: new2 包含 new1；C4: new1 不包含 old。由于 `&&` 短路，若要评价后面的条件，前面的条件必须为真。"))
story.append(table([
    ["用例", "old", "new1", "new2", "实际求值结果", "覆盖目的"],
    ["T1", "x", "abc", "z", "C1=F", "覆盖 C1 假；后续不求值"],
    ["T2", "xxabcxx", "abc", "a", "C1=T, C2=F", "覆盖 C2 假"],
    ["T3", "x", "abc", "a", "C1=T, C2=T, C3=F", "覆盖 C3 假"],
    ["T4", "a", "abc", "abc", "C1=T, C2=T, C3=T, C4=F", "覆盖 C4 假"],
    ["T5", "x", "abc", "abc", "C1=T, C2=T, C3=T, C4=T", "覆盖 C1-C4 真，并进入内层 if"],
], widths=[1.4 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 5.4 * cm, 3.0 * cm]))
story.append(note("为什么至少要这么多", "在 `&&` 短路下，要让第 k 个条件取假，前 k-1 个条件必须先取真，所以 C1 假、C2 假、C3 假、C4 假和全真通常需要分开构造。"))

story.append(h1("八、答题模板"))
story.append(h2("1. 黑盒测试用例设计模板"))
story.append(table([
    ["步骤", "写法"],
    ["找输入/输出", "输入是什么，输出或系统状态是什么"],
    ["划等价类", "有效类、无效类分别列出"],
    ["找边界", "每个区间边界取边界值和边界附近值"],
    ["写表格", "测试编号、输入、预期输出、覆盖理由"],
    ["指出歧义", "若规格有空洞、重叠或含糊，明确写“需求需澄清”"],
], widths=[3.4 * cm, 13.0 * cm]))
story.append(h2("2. 白盒覆盖题模板"))
story.append(table([
    ["步骤", "写法"],
    ["拆条件", "把 if 中的原子条件标为 C1、C2、C3"],
    ["看短路", "`&&` 后面的条件要在前面为真时才求值；`||` 后面的条件要在前面为假时才求值"],
    ["列覆盖目标", "每个条件 T/F；或每条语句、每条路径"],
    ["构造最小集", "一行一个测试用例，写输入值和覆盖的条件结果"],
    ["算复杂度", "判定节点 + 1；说明是否拆分复合条件"],
], widths=[3.4 * cm, 13.0 * cm]))
story.append(h2("3. 概念速记"))
story.append(table([
    ["概念", "速记答案"],
    ["黑盒测试", "基于规格，不看内部代码，典型方法有等价类、边界值、决策表、状态转换"],
    ["白盒测试", "基于代码结构，看内部控制流，典型方法有语句覆盖、分支覆盖、条件覆盖、路径覆盖"],
    ["边界值分析", "在等价类边界及边界附近选测试用例，因为边界最容易出错"],
    ["条件覆盖", "每个判定中每个原子条件的真、假都至少满足一次，注意短路求值"],
    ["路径覆盖", "每条独立执行路径至少执行一次，覆盖强但成本高"],
    ["回归测试", "修改后重新运行相关测试，确认原有功能没有被破坏"],
], widths=[3.2 * cm, 13.2 * cm]))

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=1.8 * cm,
    leftMargin=1.8 * cm,
    topMargin=1.55 * cm,
    bottomMargin=1.55 * cm,
)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT)
