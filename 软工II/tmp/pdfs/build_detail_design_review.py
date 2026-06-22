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
OUT = ROOT / "output" / "pdf" / "软件工程II详细设计篇复习.pdf"
SLIDES = ROOT / "tmp" / "pdfs" / "slides"
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"


pdfmetrics.registerFont(TTFont("STHeiti", FONT))
styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CN",
        parent=styles["Normal"],
        fontName="STHeiti",
        fontSize=10.2,
        leading=15.5,
        wordWrap="CJK",
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["CN"],
        fontSize=8.75,
        leading=12.4,
        textColor=colors.HexColor("#374151"),
    )
)
styles.add(
    ParagraphStyle(
        name="TitleCN",
        parent=styles["Title"],
        fontName="STHeiti",
        fontSize=26,
        leading=33,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=14,
    )
)
styles.add(
    ParagraphStyle(
        name="Subtitle",
        parent=styles["CN"],
        fontSize=12.4,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=18,
    )
)
styles.add(
    ParagraphStyle(
        name="H1CN",
        parent=styles["Heading1"],
        fontName="STHeiti",
        fontSize=17,
        leading=23,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="H2CN",
        parent=styles["Heading2"],
        fontName="STHeiti",
        fontSize=13.2,
        leading=18,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=8,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="BoxTitle",
        parent=styles["CN"],
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="CodeCN",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7.55,
        leading=10.1,
        textColor=colors.HexColor("#111827"),
    )
)


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
        start="circle",
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
    data = []
    style_name = "Small" if small else "CN"
    for row in rows:
        data.append([cell if hasattr(cell, "wrapOn") else p(str(cell), style_name) for cell in row])
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "STHeiti"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def note(title, body):
    t = Table([[p(f"<b>{title}</b>", "BoxTitle")], [p(body, "Small")]], colWidths=[16.4 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#93c5fd")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return KeepTogether([t, Spacer(1, 7)])


def img(name, caption, width=15.7 * cm):
    path = SLIDES / name
    if not path.exists():
        return []
    im = Image(str(path))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    if im.drawHeight > 9.3 * cm:
        im.drawHeight = 9.3 * cm
        im.drawWidth = im.drawHeight / ratio
    return [Spacer(1, 5), im, p(caption, "Small"), Spacer(1, 5)]


def code(text):
    t = Table([[Preformatted(text.strip("\n"), styles["CodeCN"])]], colWidths=[16.4 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("STHeiti", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(1.7 * cm, 1.0 * cm, "软件工程II 期末复习 - 详细设计篇")
    canvas.drawRightString(19.3 * cm, 1.0 * cm, f"{doc.page}")
    canvas.restoreState()


story = []
story.append(Spacer(1, 2.2 * cm))
story.append(p("软件工程II", "Subtitle"))
story.append(Paragraph("详细设计篇期末复习", styles["TitleCN"]))
story.append(p("依据：课程 PPT、123.txt 答疑转写、语音版重点、考试题目类型与重点；往年卷用于例题风格参考。", "Subtitle"))
story.append(
    note(
        "使用建议",
        "详细设计题的核心不是背一个模式名，而是把需求和体系结构继续落到类、对象协作和可修改性设计上。复习时按“职责分配 - 类图 - 详细顺序图 - 设计原则 - 变化点封装”的顺序练。",
    )
)
story.append(PageBreak())

story.append(h1("一、考试定位与优先级"))
story.append(
    table(
        [
            ["优先级", "内容", "为什么重要", "答题产物"],
            ["高", "GRASP：Information Expert、Creator、Controller", "老师口头重点明确提到；详细设计要解决职责分配", "说明谁负责什么、为什么由它负责，并画类图/顺序图"],
            ["高", "类的设计原则：OCP、DIP、SRP、LSP、ISP、组合优于继承等", "答疑说类的原则会考，可能组合考多个", "判断违反原则、说明原因、给出重构方案"],
            ["高", "详细顺序图", "2022 往年卷出现“对象交互顺序图”", "Actor/Boundary/Controller/Service/DAO/Entity 的对象协作"],
            ["中高", "设计模式诱导题：策略模式、工厂/抽象工厂、状态模式等", "今年设计模式更偏诱导式，不单纯背模式名", "找到变化点，用接口+多态封装变化"],
            ["中", "状态图与代码转换、控制风格", "答疑强调状态图主体；课件有集中/委托/分散控制风格", "明确状态主体、状态迁移，或说明控制职责分配"],
            ["中", "内聚耦合，尤其控制耦合和印记耦合", "不是最重，但答疑专门展开提醒", "识别 flag 参数、过量参数对象，提出多态/只传必要参数"],
        ],
        widths=[2.0 * cm, 4.0 * cm, 5.3 * cm, 5.1 * cm],
    )
)
story.append(
    note(
        "一句话判断",
        "详细设计题通常在问：这个系统内部应该有哪些类？每个类负责什么？对象之间按什么顺序协作？当规则、优惠券、支付方式变化时，怎样少改旧代码？",
    )
)

story.append(h1("二、详细设计基础"))
story.append(h2("1. 什么是详细设计"))
story.append(
    p(
        "详细设计是把体系结构中的模块继续细化到可编码粒度的设计活动。体系结构回答“系统有哪些大模块、怎么连接”，详细设计回答“模块内部有哪些类、方法、对象协作和算法”。"
    )
)
story.append(
    table(
        [
            ["维度", "来自需求/体系结构的输入", "详细设计输出"],
            ["静态结构", "概念类图、模块接口、PO/VO/DTO", "设计类图：类、接口、属性、方法、继承/实现/关联/组合"],
            ["动态行为", "用例、系统顺序图、业务流程", "详细顺序图/通信图：对象之间如何发消息"],
            ["状态行为", "状态图、复杂对象生命周期", "状态机实现、State 模式或 switch/transition 设计"],
            ["质量要求", "可修改性、性能、安全、可测试性", "设计理由：为什么这样分配职责、如何降低耦合"],
        ],
        widths=[2.4 * cm, 6.8 * cm, 7.2 * cm],
    )
)
story.extend(img("detail_inputs.png", "课件截图：详细设计输入。需求、系统顺序图、概念类图和体系结构接口都会影响详细设计。"))
story.extend(img("detail_outputs.png", "课件截图：详细设计输出。注意详细设计不是只画图，还要能说明设计理由。"))

story.append(h2("2. 概念类图和设计类图的区别"))
story.append(
    table(
        [
            ["对比", "概念类图", "设计类图"],
            ["阶段", "需求分析/领域建模", "详细设计"],
            ["类的含义", "问题域概念，例如产品、库存、订单", "软件实现类，例如 Service、Controller、Repository、策略类"],
            ["内容", "类名、重要属性、概念关系；不含方法", "类名、属性、方法、接口、可见性、实现关系"],
            ["重点", "理解业务对象和关系", "分配职责、支撑代码实现和可修改性"],
        ],
        widths=[2.5 * cm, 6.9 * cm, 7.0 * cm],
    )
)
story.extend(img("detail_class_relations.png", "课件截图：详细设计中的类关系。关联、聚合、组合、继承、实现都可能进入设计类图。"))

story.append(PageBreak())
story.append(h1("三、面向对象详细设计：职责与协作"))
story.append(h2("1. 职责 Responsibility"))
story.append(
    bullets(
        [
            "职责就是一个类应该知道什么、维护什么数据，或者应该执行什么任务。",
            "数据职责通常变成属性，操作职责通常变成方法。",
            "详细设计的本质，是把系统职责逐步分配给具体类，并让这些类通过消息协作完成用例。",
        ]
    )
)
story.append(h2("2. 协作 Collaboration"))
story.append(
    bullets(
        [
            "单个对象通常不能独自完成完整用例，需要和其他对象协作。",
            "协作在详细顺序图中体现：谁先收到消息，谁调用谁，谁返回结果。",
            "好的协作应该让每个对象做自己最擅长、最有信息的事情，避免一个 God Class 做所有事。",
        ]
    )
)
story.append(
    note(
        "答题模板",
        "先说明系统操作由 Controller 接收；Controller 不直接做所有业务，而是委托给 Service/领域对象；拥有数据的类承担计算职责；数据访问交给 DAO/Repository；变化点通过接口、多态或策略类封装。",
    )
)

story.append(h1("四、GRASP 模式"))
story.append(h2("1. 总览"))
story.append(
    table(
        [
            ["GRASP", "解决的问题", "考试答法"],
            ["Information Expert 信息专家", "某个职责应该给谁？", "给拥有完成该职责所需信息的类"],
            ["Creator 创建者", "谁负责创建某对象？", "由包含/聚合/记录/紧密使用该对象，或拥有初始化数据的类创建"],
            ["Controller 控制器", "谁接收系统事件？", "由系统、子系统、用例控制器或外观控制器接收，再协调其他对象"],
            ["Low Coupling 低耦合", "如何减少类之间依赖？", "避免不必要依赖，依赖接口，职责分配不引入过多连接"],
            ["High Cohesion 高内聚", "如何让类职责集中？", "每个类围绕清晰职责，不把无关任务塞到同一类"],
        ],
        widths=[4.0 * cm, 5.3 * cm, 7.1 * cm],
    )
)
story.extend(img("grasp.png", "课件截图：GRASP 总览。考试中重点用它解释“为什么由这个类负责”。"))
story.append(h2("2. Information Expert 信息专家"))
story.append(
    p(
        "把职责分配给拥有完成该职责所需信息的类。例如计算订单总价，应由订单或订单项相关类负责，而不是界面类负责；计算库存是否低于阈值，应由库存/规则相关对象或服务协调完成。"
    )
)
story.extend(img("info_expert.png", "课件截图：信息专家。判断标准不是“哪个类名字像”，而是谁拥有所需信息。"))
story.append(h2("3. Creator 创建者"))
story.append(
    bullets(
        [
            "B 聚合或组合 A，则 B 常负责创建 A。",
            "B 记录、紧密使用 A，或拥有初始化 A 的数据，也可以由 B 创建 A。",
            "如果创建逻辑复杂或需要隔离变化，可以引入 Factory，而不是把创建散落各处。",
        ]
    )
)
story.extend(img("creator.png", "课件截图：Creator。单据创建明细项、上下文创建策略对象，都是常见考点。"))

story.append(PageBreak())
story.append(h2("4. Controller 控制器"))
story.append(
    bullets(
        [
            "Controller 负责接收来自 UI/API 的系统事件，例如 `recharge(...)`、`runSchedule(...)`。",
            "它应协调对象，而不是承担所有业务计算。业务规则应下放给 Service/领域对象。",
            "可选控制器：系统整体、子系统、设备/组织外观、用例控制器、人工 Pure Fabrication 控制器。",
        ]
    )
)
story.extend(img("controller.png", "课件截图：Controller。控制器连接界面事件和领域对象协作。"))
story.extend(img("controller_bad_good.png", "课件截图：控制器的坏设计与好设计。避免表现层直接操纵领域对象，也避免控制器膨胀。"))

story.append(h1("五、详细顺序图"))
story.append(h2("1. 系统顺序图 vs 详细顺序图"))
story.append(
    table(
        [
            ["对比", "系统顺序图", "详细顺序图"],
            ["视角", "系统作为黑盒", "系统内部对象协作"],
            ["生命线", "Actor、System", "Actor、Boundary、Controller、Service、DAO/Repository、Entity"],
            ["来源", "用例主流程/系统级需求", "系统顺序图中的某个系统操作 + 体系结构接口 + 领域模型"],
            ["考试信号", "“参与者与系统交互”", "“对象交互”“类之间协作”“充值时对象交互”"],
        ],
        widths=[2.3 * cm, 6.8 * cm, 7.3 * cm],
    )
)
story.append(h2("2. 绘制步骤"))
story.append(
    numbered(
        [
            "选定一个系统操作，例如 `recharge(cardId, amount, payMethod)` 或 `runSchedule()`。",
            "找 Boundary：页面/API/界面对象，负责接收用户输入。",
            "找 Controller：接收系统事件并协调流程。",
            "找 Service/领域对象：执行业务规则，如计算优惠、判断库存、生成单据。",
            "找 DAO/Repository：查询和保存持久化对象。",
            "按时间顺序画同步调用和返回消息；有分支时使用 `alt`。",
        ]
    )
)
story.append(
    code(
        """
Actor -> Boundary: submit(...)
Boundary -> Controller: operation(...)
Controller -> Service: operation(...)
Service -> Repository: find/save/update(...)
Repository --> Service: PO/entity
Service -> DomainObject/Strategy: calculate(...)
Service --> Controller: ResultVO
Controller --> Boundary: show(result)
Boundary --> Actor: display result
"""
    )
)
story.append(
    note(
        "UML 箭头规范",
        "同步消息：实线 + 实心三角箭头；异步消息：按老师答疑记为虚线 + 鱼骨箭头；返回消息：虚线 + 开放箭头。考试手绘时要区分“调用”和“返回”。",
    )
)

story.append(PageBreak())
story.append(h1("六、控制风格与状态图"))
story.append(h2("1. 控制风格"))
story.append(
    table(
        [
            ["控制风格", "含义", "优缺点/适用"],
            ["集中式", "一个 Controller/FSM 统一发起调用", "流程清楚，容易调试；但控制器容易膨胀"],
            ["委托式", "控制器保留主决策，将子任务委托给专家对象", "更符合高内聚低耦合，是考试中较稳的设计"],
            ["分散式", "多个对象各自承担局部决策", "扩展灵活，但对象交互复杂，理解成本高"],
        ],
        widths=[2.8 * cm, 6.4 * cm, 7.2 * cm],
    )
)
story.extend(img("control_styles.png", "课件截图：控制风格。答题时优先解释为什么避免控制器过胖，为什么委托给信息专家。"))
story.append(h2("2. 状态图"))
story.append(
    bullets(
        [
            "画状态图前先确定主体：是单个订单、一张充值记录、一个红绿灯，还是整个路口系统。",
            "状态图表达某个对象/主体在生命周期中的状态和迁移，不是画所有类之间的调用。",
            "状态图可以转为代码：简单情况用 switch/if；复杂且状态行为变化明显时可用 State 模式。",
        ]
    )
)
story.extend(img("state_concept.png", "课件截图：状态图概念。答疑里老师特别强调“先明确主体”。"))
story.extend(img("state_to_code.png", "课件截图：状态图到代码。复杂状态行为可转成 State 模式。"))

story.append(h1("七、类的设计原则"))
story.append(h2("1. 必背原则表"))
story.append(
    table(
        [
            ["原则", "核心含义", "常见违反", "修改方向"],
            ["SRP 单一职责", "一个类只有一个变化原因", "User 类同时负责数据、支付、发券、导出报表", "拆分类，把不同变化原因分离"],
            ["OCP 开闭原则", "对扩展开放，对修改关闭", "新增优惠券/支付方式要改原有 switch", "抽象接口 + 新增实现类 + 多态"],
            ["DIP 依赖倒置", "高层模块依赖抽象，不依赖具体实现", "Service 直接 new WeChatPay", "依赖 PaymentStrategy/Repository 接口"],
            ["ISP 接口隔离", "客户端不依赖不使用的方法", "Robot 被迫实现 eat/sleep", "拆成多个小接口"],
            ["LSP 里氏替换", "子类能替换父类且不破坏契约", "企鹅继承 Bird 但 fly 抛异常", "重新抽象父类或拆接口"],
            ["LoD 迪米特法则", "只与你的直接朋友交谈", "a.getB().getC().doX()", "通过委托封装消息链"],
            ["组合优于继承", "优先用组合进行黑盒复用", "为复用代码滥用继承", "持有接口对象，运行时可替换"],
            ["权限最小化", "从 private 开始，必要时再放宽", "public 字段、暴露集合内部", "封装字段，提供受控方法"],
        ],
        widths=[3.3 * cm, 4.3 * cm, 4.4 * cm, 4.4 * cm],
    )
)
story.extend(img("principles_p1_p7.png", "课件截图：原则 P1-P7。类原则可能组合考，重点会让你判断违反了什么原则。"))
story.extend(img("principles_p8_p14.png", "课件截图：原则 P8-P14。OCP、DIP、SRP、组合优于继承是变化题里的常用答案。"))

story.append(PageBreak())
story.append(h2("2. 内聚与耦合"))
story.append(
    bullets(
        [
            "高内聚：一个类/方法内部元素围绕同一职责，修改理由集中。",
            "低耦合：类之间依赖少、依赖稳定抽象、少暴露实现细节。",
            "控制耦合：调用者传入 flag/type，方法内部 switch 决定行为。修改方向：多态、策略模式、命令对象。",
            "印记耦合：把一个大对象传给方法，但方法只需要其中一两个字段。修改方向：只传必要参数或提取专用参数对象。",
        ]
    )
)
story.append(
    code(
        """
// 控制耦合：type 控制内部逻辑
void pay(String type, Money amount) {
    if (type.equals(\"WECHAT\")) { ... }
    else if (type.equals(\"ALIPAY\")) { ... }
}

// 重构方向：策略 + 多态
interface PaymentStrategy { PayResult pay(Money amount); }
class WeChatPay implements PaymentStrategy { ... }
class AliPay implements PaymentStrategy { ... }
"""
    )
)
story.extend(img("isp.png", "课件截图：接口隔离原则。接口越胖，调用方被迫知道/实现越多无关内容。"))
story.extend(img("composition_over_inheritance.png", "课件截图：组合优于继承。策略模式、支付方式、优惠券规则都常用组合和多态。"))

story.append(h1("八、设计模式诱导题"))
story.append(h2("1. 答题套路"))
story.append(
    numbered(
        [
            "先找变化点：优惠券类型、支付方式、订货规则、状态行为、对象创建族。",
            "判断旧设计问题：switch/if 扩散、控制耦合、违反 OCP/DIP/SRP。",
            "抽象稳定接口：如 `CouponStrategy`、`PaymentStrategy`、`ReorderRule`。",
            "把每种变化做成实现类：新增类型只新增类，不改旧业务流程。",
            "上下文类组合接口对象，并在运行时选择或注入具体实现。",
            "画类图：Context 持有 Strategy 接口，ConcreteStrategy 实现接口。",
        ]
    )
)
story.extend(img("strategy_pattern.png", "课件截图：策略模式。遇到“未来还会新增多种算法/优惠/支付方式”，优先想到它。"))
story.extend(img("strategy_class.png", "课件截图：策略模式类图。核心是 Context 组合 Strategy，具体策略通过多态替换。"))

story.append(PageBreak())
story.append(h1("九、往年卷风格例题与答案"))
story.append(h2("例题 1：2022 校园卡充值 - 优惠券和支付方式"))
story.append(
    p(
        "题型：用户充值时有不同优惠券，同时可以用支付宝、微信等不同充值方式。要求画 User、Card、多种 Coupon、ThirdPayment、PaymentRecord 类图；新增数值折扣、比例折扣如何实现变更；画充值对象交互顺序图。"
    )
)
story.append(h2("1. 类图答案思路"))
story.append(
    code(
        """
User 1 ---- 1 Card
User 1 ---- 0..* Coupon
Card 1 ---- 0..* PaymentRecord

<<interface>> Coupon
  +discount(amount): Money
FixedAmountCoupon implements Coupon
PercentageCoupon implements Coupon

<<interface>> ThirdPayment
  +pay(userId, amount): PayResult
WeChatPayment implements ThirdPayment
AliPayPayment implements ThirdPayment

RechargeService
  - payment: ThirdPayment
  +recharge(user, card, amount, coupon): RechargeResult
"""
    )
)
story.append(
    bullets(
        [
            "优惠券变化点用 `Coupon` 接口封装，固定金额优惠券和比例优惠券分别实现。",
            "支付方式变化点用 `ThirdPayment` 接口封装，微信、支付宝分别实现。",
            "RechargeService 依赖抽象接口，符合 DIP；新增优惠券或支付方式时新增类，符合 OCP。",
            "User 和 Card 是领域对象，PaymentRecord 记录充值结果，Card 与 PaymentRecord 可画 1 对 0..* 关联。",
        ]
    )
)
story.append(h2("2. 充值详细顺序图答案模板"))
story.append(
    code(
        """
User -> RechargePage: submit(amount, couponId, payType)
RechargePage -> RechargeController: recharge(requestVO)
RechargeController -> RechargeService: recharge(requestVO)
RechargeService -> CouponRepository: find(couponId)
CouponRepository --> RechargeService: Coupon
RechargeService -> Coupon: discount(amount)
Coupon --> RechargeService: discountedAmount
RechargeService -> PaymentFactory: getPayment(payType)
PaymentFactory --> RechargeService: ThirdPayment
RechargeService -> ThirdPayment: pay(userId, discountedAmount)
ThirdPayment --> RechargeService: PayResult
alt 支付成功
  RechargeService -> CardRepository: updateBalance(cardId, discountedAmount)
  RechargeService -> PaymentRecordRepository: save(record)
  RechargeService --> RechargeController: RechargeResultVO(success)
else 支付失败
  RechargeService --> RechargeController: RechargeResultVO(failReason)
end
RechargeController --> RechargePage: show(result)
"""
    )
)

story.append(h2("例题 2：2020 进销存 - 再订货规则变化"))
story.append(
    p(
        "题型：旧规则是库存低于固定值订货，后来可能新增考虑近期活动、销售趋势等新的计算方式。问逻辑层如何设计以更好应对变更。"
    )
)
story.append(
    bullets(
        [
            "问题：如果在排程服务中用 `if/switch(ruleType)` 判断规则，会形成控制耦合，新增规则要改旧代码，违反 OCP。",
            "设计：抽象 `ReorderStrategy` 或 `ReorderRule` 接口，不同规则各自实现 `needReorder(...)` 和 `calculateQuantity(...)`。",
            "排程服务只依赖接口；规则选择可由工厂、配置或规则仓储返回具体策略。",
            "优点：新增“近期活动规则”只新增策略类，原有排程流程不变；符合 OCP、DIP、低耦合、高内聚。",
        ]
    )
)
story.append(
    code(
        """
interface ReorderStrategy {
    boolean needReorder(Inventory inv, SalesData sales);
    int calculateQuantity(Inventory inv, SalesData sales);
}

class FixedThresholdStrategy implements ReorderStrategy { ... }
class PromotionAwareStrategy implements ReorderStrategy { ... }
class SalesTrendStrategy implements ReorderStrategy { ... }

class ScheduleService {
    private ReorderStrategy strategy;
    PurchaseInquiry runSchedule(...) {
        if (strategy.needReorder(inv, sales)) {
            int qty = strategy.calculateQuantity(inv, sales);
            return inquiryFactory.create(product, qty);
        }
    }
}
"""
    )
)

story.append(PageBreak())
story.append(h2("例题 3：设计原则判断题"))
story.append(
    table(
        [
            ["现象", "违反原则/问题", "修改"],
            ["新增支付方式要修改 `pay(type)` 的 switch", "OCP、控制耦合", "抽象 PaymentStrategy，新增实现类"],
            ["RechargeService 直接 new WeChatPay", "DIP", "依赖 ThirdPayment 接口，由工厂/DI 提供实现"],
            ["User 类同时负责用户资料、发券、充值、报表导出", "SRP", "拆分 User、CouponService、RechargeService、ReportService"],
            ["Robot 实现 Worker 但 eat/sleep 抛异常", "ISP，也可能 LSP", "拆成 Workable、Feedable 等小接口"],
            ["Penguin 继承 Bird，但 fly() 无法满足", "LSP", "Bird 不承诺 fly，抽出 Flyable 接口"],
            ["a.getB().getC().doSomething()", "LoD/消息链", "在 A 或 B 中提供委托方法，隐藏内部结构"],
            ["sendEmail(Employee e) 只用 e.email", "印记耦合", "只传 email 或 EmailAddress"],
        ],
        widths=[5.8 * cm, 4.5 * cm, 6.1 * cm],
    )
)

story.append(h1("十、考场速记模板"))
story.append(h2("1. 详细设计答题万能结构"))
story.append(
    bullets(
        [
            "先列类：Boundary/Controller/Service/Repository/Entity/Strategy。",
            "再分职责：Controller 接收系统事件，Service 组织业务流程，信息专家承担计算，Repository 访问数据。",
            "再画关系：接口实现、组合、关联；变化点用接口 + 多态。",
            "再画顺序图：从用户操作到 Controller，再到 Service、Repository、策略/领域对象，最后返回 VO。",
            "最后说原则：高内聚低耦合，OCP/DIP/SRP，必要时说明策略模式或状态模式。",
        ]
    )
)
story.append(h2("2. 类图模板：变化点封装"))
story.append(
    code(
        """
Context/Service ----> <<interface>> Strategy
Strategy <|.. ConcreteStrategyA
Strategy <|.. ConcreteStrategyB

Context only calls Strategy.operation(...)
Adding a new behavior = add ConcreteStrategyC, not modify Context.
"""
    )
)
story.append(h2("3. 顺序图模板：充值/支付/排程"))
story.append(
    code(
        """
Actor -> Page/API -> Controller -> Service
Service -> Repository: query needed PO/entity
Service -> Strategy/DomainObject: calculate/validate
Service -> Repository: save/update
Service --> Controller: ResultVO
Controller --> Page/API: show result
"""
    )
)
story.append(h2("4. 设计理由模板"))
story.append(
    bullets(
        [
            "该设计把变化点抽象为接口，业务流程依赖抽象而非具体实现，符合 DIP。",
            "新增一种规则/支付方式/优惠券时只需新增实现类，不修改原有流程，符合 OCP。",
            "每个类只承担一个清晰职责，避免 God Class，符合 SRP 和高内聚。",
            "上下文类通过组合持有策略对象，避免继承耦合，运行时可以灵活切换。",
        ]
    )
)


doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=1.8 * cm,
    leftMargin=1.8 * cm,
    topMargin=1.7 * cm,
    bottomMargin=1.55 * cm,
)
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(OUT)
