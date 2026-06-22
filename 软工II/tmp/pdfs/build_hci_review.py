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
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "软件工程II人机交互篇复习.pdf"
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


def slide(page, caption, width=15.7 * cm, max_height=9.2 * cm):
    return img(SLIDES / "hci" / f"page-{page:02d}.png", caption, width, max_height)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("STHeiti", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(1.7 * cm, 1.0 * cm, "软件工程II 期末复习 - 人机交互篇")
    canvas.drawRightString(19.3 * cm, 1.0 * cm, f"{doc.page}")
    canvas.restoreState()


story = []
story.append(Spacer(1, 2.2 * cm))
story.append(p("软件工程II", "Subtitle"))
story.append(Paragraph("人机交互篇期末复习", styles["TitleCN"]))
story.append(p("依据：03-04 人机交互设计课件，123.txt，语音版重点，考试题目类型与重点，2020/2022 往年卷。", "Subtitle"))
story.append(note("使用建议", "人机交互题的核心不是背诵原则，而是看到界面后能说清楚：哪里好或不好、体现或违反什么原则、会给用户造成什么影响、应该怎样修改。"))
story.append(PageBreak())

story.append(h1("一、考试定位与优先级"))
story.append(table([
    ["优先级", "内容", "依据", "答题产物"],
    ["高", "三条黄金原则与常用界面设计原则", "语音重点明确要求掌握；2020/2022 均考界面点评", "原则 + 界面证据 + 用户影响 + 改进"],
    ["高", "可用性及五个维度", "课件基本目标；可作为评价界面的总框架", "易学性、效率、易记性、容错性、满意度"],
    ["高", "导航、反馈、防错、错误恢复、一致性", "界面点评最容易落点", "至少找出 3 点，正反均可"],
    ["中高", "人机交互设计过程", "语音重点明确要求了解整体开发过程", "用户任务分析到原型、评估、迭代实现"],
    ["中", "人的记忆、精神模型、用户差异、人因", "支撑设计原则的原因", "解释为什么识别优于回忆、为什么要照顾不同用户"],
    ["中", "可用性评估和可访问性", "课件重点，适合简答或改进建议", "启发式评估、用户测试、A/B 测试、POUR"],
], widths=[2.0 * cm, 4.6 * cm, 5.1 * cm, 4.7 * cm]))
story.append(note("往年题型", "2020：给出询价单页面，要求结合原则点评至少 3 点。2022：分析校园卡自助系统，说出好的地方、不好的地方并给出建议，至少 3 点。复习时应以“会评价界面”为主线。"))

story.append(h1("二、人机交互基础与可用性"))
story.append(h2("1. 什么是人机交互"))
story.append(p("人机交互 HCI 研究人与计算机系统之间的交互。设计目标是让交互简单、自然、有效，使用户能够顺利完成任务。界面应符合用户的技能、经验和预期，不应把数据库、模块、内部状态等实现细节强加给用户。"))
story.append(h2("2. 可用性的五个维度"))
story.append(table([
    ["维度", "含义", "界面评价时怎么观察"],
    ["易学性", "新用户能快速掌握操作", "入口是否清楚、术语是否熟悉、是否有引导"],
    ["效率", "熟练用户能高效完成任务", "步骤是否精简、是否支持快捷方式和默认值"],
    ["易记性", "中断使用后无需重新学习", "布局和操作是否稳定一致、选项是否可见"],
    ["容错性", "错误少，能快速从错误中恢复", "是否防止误操作、可撤销、错误提示是否可行动"],
    ["满意度", "用户使用时感到舒适和愉快", "信息是否清晰、等待是否焦虑、视觉是否克制"],
], widths=[2.5 * cm, 6.2 * cm, 7.7 * cm]))
story.extend(slide(7, "课件截图：可用性是易学性、效率、易记性、容错性和满意度的综合。"))

story.append(PageBreak())
story.append(h1("三、理解用户"))
story.append(h2("1. 人的基本特性"))
story.append(bullets([
    "短时记忆有限：让选项和状态可见，由系统替用户记忆，避免要求用户背命令或重复输入。",
    "人会犯错：设计应优先防错，并提供撤销、重做、确认和恢复机制。",
    "用户存在差异：新手、偶发性熟练用户和专家需要不同层次的帮助与效率工具。",
    "人的感知和动作能力受设备、环境影响：移动端要考虑触屏尺寸、拇指可达区、光照、网络和噪声。",
]))
story.extend(slide(11, "课件截图：人的短时记忆有限、人会犯错且用户各不相同。"))
story.append(h2("2. 三类用户与设计权衡"))
story.append(table([
    ["用户", "特点", "设计侧重"],
    ["新手", "不熟悉业务和系统", "清晰导航、可见选项、引导、防错、帮助"],
    ["偶发性熟练用户", "有经验但不连续使用", "稳定一致、易记、保留上下文"],
    ["专家", "长期高频使用", "快捷键、批量操作、减少步骤、可定制"],
], widths=[3.0 * cm, 6.0 * cm, 7.4 * cm]))
story.append(note("常见权衡", "易学性和效率有时冲突。新手偏好可见的菜单和提示，专家偏好快捷键和批量操作。好的系统可以同时提供清晰的默认路径和可选的高效路径。"))
story.append(h2("3. 精神模型 Mental Model"))
story.append(p("精神模型是用户对任务和系统工作方式的理解。设计应从用户真正想完成的目标出发，使用用户熟悉的概念与隐喻。例如用户想“充值校园卡”，界面应围绕金额、支付方式和结果组织，而不是展示数据库表名、服务接口或内部事务编号。"))
story.extend(slide(15, "课件截图：发现用户目标与任务，使界面模型贴近用户的精神模型。"))

story.append(h1("四、交互风格、导航与反馈"))
story.append(h2("1. 常见交互风格"))
story.append(table([
    ["风格", "优点", "缺点/适用对象"],
    ["直接操纵", "对象可见、易学、反馈直接", "复杂信息空间中导航较难；适合一般用户"],
    ["菜单选择", "无需记忆命令、减少非法输入", "层级过深会降低效率"],
    ["表单填充", "适合结构化数据、易校验", "字段多时认知负担高"],
    ["命令语言", "输入少、表达力强、效率高", "学习成本高、容易出错；适合专家"],
    ["自然语言", "交流自然、适合偶发用户和 AI", "有歧义、不确定、结果需核验"],
], widths=[2.5 * cm, 6.3 * cm, 7.6 * cm]))
story.extend(slide(24, "课件截图：常见界面类型及其适用场景。"))
story.append(h2("2. 导航"))
story.append(bullets([
    "全局结构：按用户任务组织功能，区分主题和重要性，让用户知道可以去哪里。",
    "局部结构：通过布局、按钮位置、颜色、字号、面包屑和选中状态，让用户知道当前在哪里、下一步做什么。",
    "避免层级过深、名称含糊、同一功能在不同页面位置不一致。",
]))
story.extend(slide(32, "课件截图：导航分为全局结构和局部结构，设计依据是任务模型与用户关注点。"))

story.append(PageBreak())
story.append(h2("3. 反馈"))
story.append(bullets([
    "用户操作后应及时显示结果和当前状态，交互是双向的。",
    "简单操作需要近乎即时响应；普通任务应在数秒内反馈。",
    "耗时任务应提供进度条、阶段提示或骨架屏，并允许中断或后台执行。",
    "不要只显示“失败”或错误码，要指出发生了什么、原因可能是什么、用户下一步能做什么。",
]))
story.extend(slide(33, "课件截图：反馈时间经验准则。意外且无法解释的延迟会破坏体验。"))
story.append(h2("4. 对话与错误处理"))
story.append(table([
    ["原则", "不好的表现", "改进"],
    ["状态可见", "点击后无变化，不知道是否提交", "显示加载、成功/失败和当前状态"],
    ["防止错误", "删除紧邻保存，输入格式不限", "拉开危险操作、约束输入、禁用无效操作"],
    ["帮助恢复", "只显示 E1003", "使用清晰语言说明问题并给解决办法"],
    ["用户可控", "无法取消或返回，误操作不可逆", "提供取消、返回、撤销，关键操作确认"],
    ["简约", "无关信息和按钮争夺注意力", "按任务优先级隐藏或弱化次要内容"],
], widths=[2.6 * cm, 6.2 * cm, 7.6 * cm]))

story.append(h1("五、人机交互设计过程"))
story.append(p("人机交互设计贯穿需求开发和软件设计全过程，不是编码完成后再美化界面。"))
story.append(numbered([
    "研究用户、任务、设备和使用环境，明确用户目标与可用性目标。",
    "建立 Persona、用户旅程或任务模型，发现用户的精神模型和痛点。",
    "设计全局导航、交互风格和对话结构。",
    "形成界面布局和线框图，制作低保真到高保真原型。",
    "让真实用户参与评估，根据问题反复修改。",
    "实现界面，并继续验证可用性和可访问性。",
]))
story.extend(slide(39, "课件截图：导航设计、界面设计、原型化、评估与修正贯穿开发过程。"))

story.append(h1("六、界面设计原则"))
story.append(h2("1. 三条黄金原则"))
story.append(table([
    ["原则", "核心含义", "考试中常见证据"],
    ["让用户掌控系统", "控制交互节奏，能退出、取消、撤销和重做", "返回、取消、撤销、关键操作确认、允许中断"],
    ["减少用户记忆负担", "系统替用户记忆，识别优于回忆", "选项可见、默认值、历史记录、自动填充、上下文保留"],
    ["保持一致性", "相似内容和操作有相似表现与结果", "术语、布局、颜色、图标、控件、反馈遵循统一规则"],
], widths=[4.0 * cm, 6.1 * cm, 6.3 * cm]))
story.extend(slide(43, "课件截图：Pressman 三条黄金原则。"))
story.append(h2("2. Nielsen 十条启发式原则"))
story.append(table([
    ["原则", "一句话理解"],
    ["系统状态可见", "始终告诉用户系统正在做什么"],
    ["与现实世界匹配", "使用用户熟悉的语言、顺序和概念"],
    ["用户可控", "支持撤销、重做、退出和取消"],
    ["一致性与标准", "遵循平台惯例，相同操作有相同结果"],
    ["防止错误", "预防错误优先于事后提示"],
    ["识别优于回忆", "让信息、选项和状态可见"],
    ["灵活高效", "为熟练用户提供快捷方式"],
    ["简约设计", "去掉与当前任务无关的信息"],
    ["帮助恢复错误", "清楚说明问题并提供解决方案"],
    ["帮助与文档", "文档可搜索、简短、以任务为导向"],
], widths=[5.2 * cm, 11.2 * cm]))

story.append(PageBreak())
story.extend(slide(44, "课件截图：Nielsen 十条可用性启发式原则，是界面点评的核心检查单。", max_height=10.0 * cm))
story.append(note("原则之间的关系", "三条黄金原则是总纲，Nielsen 十条原则把它们细化。考试不必机械写出全部原则名称，抓住当前界面最明显的 3-6 个问题，并给出证据和改进即可。"))
story.append(h2("3. 高频界面检查点"))
story.append(table([
    ["检查维度", "观察问题"],
    ["任务与信息层级", "主任务是否突出？内容是否按用户任务分组？"],
    ["状态与反馈", "用户是否知道当前位置、系统状态和操作结果？"],
    ["导航与出口", "入口、返回、取消、完成是否清楚？"],
    ["一致性", "同类按钮、术语、颜色、图标和布局是否一致？"],
    ["防错与恢复", "危险操作是否隔离？输入是否校验？是否可撤销？"],
    ["认知负担", "是否要求记忆？信息是否过密？是否有合理默认值？"],
    ["效率", "常用操作是否短路径？专家是否有快捷方式？"],
    ["可访问性", "对比度、字号、键盘、标签、颜色传意是否合适？"],
], widths=[4.0 * cm, 12.4 * cm]))

story.append(h1("七、原型、评估与可访问性"))
story.append(h2("1. 原型化"))
story.append(p("原型用于在投入完整实现前验证信息结构、任务流程和交互方案。典型迭代为：线框图 - 低保真原型 - 用户测试 - 高保真原型 - 用户评估 - 最终实现。"))
story.extend(slide(48, "课件截图：GUI 从一开始就要规划，并在各阶段让用户参与。"))

story.append(PageBreak())
story.append(h2("2. 可用性评估方法"))
story.append(table([
    ["方法", "做法", "适合发现"],
    ["启发式评估", "3-5 名专家依据原则逐条检查", "一致性、反馈、出口、错误提示等已知原则问题"],
    ["用户测试", "真实用户执行典型任务，可配合有声思维", "真实迷惑点、任务失败、精神模型偏差"],
    ["A/B 测试", "同时比较两个版本的任务完成率或转化率", "两个具体方案的量化差异"],
    ["眼动追踪", "观察注意力热图", "重要元素是否被忽视、视觉层级是否合理"],
], widths=[3.1 * cm, 6.6 * cm, 6.7 * cm]))
story.extend(slide(50, "课件截图：启发式评估、用户测试和 A/B 测试的适用范围。"))
story.append(h2("3. 可访问性"))
story.append(bullets([
    "可感知：图片有替代文本，文字与背景保持足够对比度。",
    "可操作：所有功能可以通过键盘访问，焦点顺序合理。",
    "可理解：语言清楚，表单有标签，错误可识别并可修复。",
    "健壮性：与屏幕阅读器和其他辅助技术兼容。",
    "不能只靠颜色传递信息，应同时使用文字、图标或形状。",
]))
story.extend(slide(51, "课件截图：WCAG 的 POUR 四原则与常见无障碍问题。"))

story.append(h1("八、界面点评题答法"))
story.append(h2("1. 标准答题链"))
story.append(table([
    ["步骤", "写法", "示例"],
    ["指出现象", "描述界面上可观察的证据", "删除按钮紧邻保存按钮且样式相同"],
    ["对应原则", "说明体现或违反的原则", "违反防错原则、视觉层级不清"],
    ["解释影响", "说明对用户造成什么后果", "容易误触并产生不可逆数据损失"],
    ["给出改进", "提出具体可执行的修改", "拉开距离、降低危险操作权重、增加确认或撤销"],
], widths=[2.5 * cm, 6.0 * cm, 7.9 * cm]))
story.append(note("推荐句式", "界面的……体现/违反了……原则，因为……，会导致用户……；建议……。不要只写“颜色不好看”“按钮太多”，必须说明原则、影响和具体修改。"))
story.append(h2("2. 找点顺序"))
story.append(numbered([
    "先看主任务是否突出，信息是否按用户任务组织。",
    "再看当前位置、流程进度、操作结果是否可见。",
    "检查返回、取消、撤销、完成等出口。",
    "检查危险操作、输入约束、错误提示和恢复机制。",
    "检查术语、按钮、颜色、图标和布局的一致性。",
    "最后补充效率、简约性、可访问性和不同用户群体。",
]))
story.append(h2("3. 常见失分方式"))
story.append(bullets([
    "只列原则名称，没有引用界面证据。",
    "只说好或不好，没有解释用户影响。",
    "改进建议过于空泛，例如“优化界面”“调整布局”。",
    "把视觉审美等同于人机交互，没有联系任务完成、错误率和认知负担。",
    "同一点换几个原则重复描述，实际有效观点不足三点。",
]))

story.append(h1("九、例题 1：2020 询价单界面点评"))
story.extend(img(ROOT / "tmp" / "pdfs" / "render_hci_past" / "2020-crop-13.png", "往年卷截图：2020 人机交互题，要求结合设计原则点评至少 3 点。", width=15.9 * cm, max_height=9.0 * cm))
story.append(h2("参考答案：体现较好的方面"))
story.append(table([
    ["界面证据", "原则与分析"],
    ["顶部流程条显示采购单草稿、询价单、接收报价等阶段，并高亮当前阶段", "体现系统状态可见和导航清晰，用户能判断当前处于流程中的什么位置以及后续步骤"],
    ["订单基本信息、产品明细、金额合计分区呈现", "体现信息分组和与任务匹配，减少在密集数据中寻找关键内容的负担"],
    ["提供编辑、新建、打印、确认订单、取消等明确操作", "提供可见操作并保留取消出口，体现识别优于回忆和用户可控"],
    ["合计金额放在右下并以更大、更粗的样式强调", "建立视觉层级，突出完成判断所需的关键信息"],
], widths=[7.0 * cm, 9.4 * cm]))

story.append(PageBreak())
story.append(h2("参考答案：可改进的方面"))
story.append(table([
    ["问题", "影响/违反原则", "改进建议"],
    ["顶部命令数量较多，多个按钮视觉权重接近", "主操作不突出，增加选择负担，违反简约设计", "按任务分组，只突出当前阶段的主要操作，将低频操作放入更多菜单"],
    ["红色操作按钮较多，颜色语义不统一", "用户难以区分主操作、警告和危险操作，违反一致性", "统一颜色语义：主操作使用单一强调色，危险操作仅用红色并与普通操作隔离"],
    ["文字和表格字号较小、灰度偏低、信息密度高", "降低可读性和可访问性，用户容易看错金额或字段", "提高字号与对比度，增加行距，允许表格列宽调整和重点字段固定"],
    ["部分图标和术语缺乏解释", "依赖回忆，可能与用户精神模型不一致", "图标配文字或工具提示，业务术语使用用户熟悉的名称"],
    ["关键操作的结果反馈和错误恢复在界面上不明确", "用户不确定是否提交成功，误操作后难恢复", "提交时显示进度与结果；对关键操作提供确认、撤销或操作记录"],
], widths=[5.0 * cm, 5.8 * cm, 5.6 * cm]))
story.append(note("考试写法", "题目只要求至少 3 点时，建议写 5-6 点，正面和负面都可以。每一点都要引用界面中的具体按钮、流程条、表格、颜色或信息层级作为证据。"))

story.append(h1("十、例题 2：校园卡自助系统"))
story.append(p("题目：从人机交互角度分析校园卡自助系统，说出好的地方；说出不好的地方并给出建议，至少三点。假设系统包含充值、查询余额、绑定银行卡、查询明细、挂失等功能。"))
story.append(h2("参考答案"))
story.append(table([
    ["观察点", "分析与建议"],
    ["任务入口", "若首页直接展示“充值、余额、明细、挂失”等高频任务，符合用户精神模型且易学；应按频率和风险确定层级，而不是按内部模块分类"],
    ["充值反馈", "支付过程中应显示当前步骤、处理中状态和最终结果；长时间无反馈会让用户重复提交，应禁用重复点击并显示进度"],
    ["金额输入", "应限制正数、范围和精度，提供常用金额选项，并在提交前显示到账金额，体现防错和减少记忆负担"],
    ["挂失操作", "挂失属于高风险操作，应与普通查询分开，二次确认并说明后果；成功后明确显示卡状态和补办入口"],
    ["银行卡信息", "敏感卡号应脱敏展示，绑定/解绑有清楚确认和错误恢复，符合安全感与用户可控"],
    ["不同用户", "新手需要清晰标签和引导，熟练用户可使用最近操作、默认支付方式和快捷充值，提高效率"],
], widths=[3.1 * cm, 13.3 * cm]))

story.append(PageBreak())
story.append(h1("十一、AI 时代的人机交互"))
story.append(bullets([
    "透明性：告诉用户 AI 的能力边界、不确定性和数据使用情况。",
    "信任校准：提醒用户核验重要结果，流畅表达不等于正确。",
    "可控性：用户能够停止生成、拒绝建议、撤销操作；Agent 执行关键动作前请求确认。",
    "感知延迟：通过流式输出、进度提示和阶段状态降低等待感。",
    "优雅降级：AI 失败时提供重试、人工处理或传统界面路径。",
]))
story.extend(slide(57, "课件截图：AI 系统在传统原则之外还要强调透明、可解释、人工覆盖和优雅降级。"))

story.append(h1("十二、考前速记"))
story.append(table([
    ["问法", "速答"],
    ["HCI 的目标是什么？", "让人与计算机的交互简单、自然、有效，使用户顺利完成任务"],
    ["可用性包括什么？", "易学性、效率、易记性、容错性、满意度"],
    ["三条黄金原则是什么？", "让用户掌控系统、减少用户记忆负担、保持一致性"],
    ["为什么识别优于回忆？", "人的短时记忆有限，让选项和状态可见可降低认知负担和错误率"],
    ["精神模型是什么？", "用户对任务和系统工作方式的理解；界面应使用用户熟悉的概念并贴近其目标"],
    ["HCI 设计过程是什么？", "用户与任务分析 - 交互和导航设计 - 原型化 - 用户评估 - 迭代实现"],
    ["如何答界面点评题？", "问题/优点 - 对应原则 - 用户影响 - 具体改进"],
    ["常见评估方法？", "启发式评估、用户测试/有声思维、A/B 测试、眼动追踪"],
], widths=[4.1 * cm, 12.3 * cm]))
story.append(note("最后一分钟检查", "至少准备六个万能观察点：状态反馈、导航出口、一致性、防错恢复、记忆负担、信息层级。遇到陌生界面时按这六项逐个扫，通常足够组织出 3-6 个有效答案。"))

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
