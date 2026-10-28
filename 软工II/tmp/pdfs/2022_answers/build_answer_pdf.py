from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage, ImageChops, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, ListFlowable, ListItem,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[3]
TMP = ROOT / "tmp" / "pdfs" / "2022_answers"
SOURCE = ROOT / "tmp" / "pdfs" / "2022_answers_source"
DIAG = TMP / "diagrams"
ASSET = TMP / "assets"
ASSET.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "output" / "pdf" / "2022年软件工程II往年卷参考答案.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont("CJK", FONT))
pdfmetrics.registerFontFamily("CJK", normal="CJK", bold="CJK", italic="CJK", boldItalic="CJK")

PURPLE = colors.HexColor("#50367F")
PURPLE_LIGHT = colors.HexColor("#EEE9F7")
BLUE = colors.HexColor("#315A8C")
BLUE_LIGHT = colors.HexColor("#EAF1F9")
GREEN = colors.HexColor("#2F7250")
GREEN_LIGHT = colors.HexColor("#EAF6EF")
ORANGE = colors.HexColor("#A76318")
ORANGE_LIGHT = colors.HexColor("#FFF3DF")
TEXT = colors.HexColor("#172033")
MUTED = colors.HexColor("#5F6B7C")
LINE = colors.HexColor("#D9DEEA")

styles = getSampleStyleSheet()
cover_title = ParagraphStyle("CoverTitle", fontName="CJK", fontSize=26, leading=36, textColor=PURPLE, alignment=TA_CENTER)
cover_sub = ParagraphStyle("CoverSub", fontName="CJK", fontSize=12, leading=20, textColor=MUTED, alignment=TA_CENTER)
h1 = ParagraphStyle("H1", fontName="CJK", fontSize=18, leading=25, textColor=PURPLE, spaceBefore=3, spaceAfter=8, keepWithNext=True)
h2 = ParagraphStyle("H2", fontName="CJK", fontSize=13.5, leading=19, textColor=BLUE, spaceBefore=6, spaceAfter=5, keepWithNext=True)
body = ParagraphStyle("Body", fontName="CJK", fontSize=9.6, leading=15.2, textColor=TEXT, spaceAfter=4, wordWrap="CJK")
small = ParagraphStyle("Small", parent=body, fontSize=8.4, leading=12.5, textColor=MUTED)
question = ParagraphStyle("Question", parent=body, fontSize=9.4, leading=15, textColor=TEXT)
bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-8, bulletIndent=4, spaceAfter=2)
caption = ParagraphStyle("Caption", parent=small, alignment=TA_CENTER, spaceBefore=3, spaceAfter=7)
toc = ParagraphStyle("TOC", parent=body, fontSize=10.5, leading=19)


def trim_white(im, cutoff=245):
    rgb = im.convert("RGB")
    bg = PILImage.new("RGB", rgb.size, "white")
    diff = ImageChops.difference(rgb, bg).convert("L").point(lambda p: 255 if p > (255-cutoff) else 0)
    bbox = diff.getbbox()
    if not bbox:
        return rgb
    l, t, r, b = bbox
    pad = 12
    return rgb.crop((max(0,l-pad), max(0,t-pad), min(rgb.width,r+pad), min(rgb.height,b+pad)))


def prepare_assets():
    cards=[]
    for n in range(2,8):
        im=PILImage.open(SOURCE / f"page-{n}.png").convert("RGB")
        if n == 7:
            im=im.crop((0,0,im.width,955))
        im=trim_white(im)
        im.thumbnail((680,700))
        card=PILImage.new("RGB",(710,740),"white")
        card.paste(im,((710-im.width)//2,15))
        d=ImageDraw.Draw(card)
        d.rectangle((1,1,708,738),outline=(210,215,226),width=2)
        d.text((18,710),f"原题界面 {n-1}",fill=(70,78,95))
        cards.append(card)
    collage=PILImage.new("RGB",(1420,2220),(242,245,250))
    for i,im in enumerate(cards): collage.paste(im,((i%2)*710,(i//2)*740))
    collage.save(ASSET / "ui-screens.png", quality=95)

    p8=PILImage.open(SOURCE / "page-8.png").convert("RGB")
    trim_white(p8.crop((135,185,1025,570))).save(ASSET / "issue-coupon-code.png")
    trim_white(p8.crop((125,730,1030,1375))).save(ASSET / "original-bad-class.png")
    p9=PILImage.open(SOURCE / "page-9.png").convert("RGB")
    trim_white(p9.crop((135,40,1025,625))).save(ASSET / "do-post-code.png")


def P(txt, style=body):
    return Paragraph(txt, style)


def bullets(items):
    return ListFlowable([ListItem(P(x), leftIndent=10) for x in items], bulletType="bullet", leftIndent=18, bulletFontName="CJK", bulletFontSize=8, bulletColor=BLUE)


def box(title, content, color=PURPLE_LIGHT, border=PURPLE):
    cells=[[P(f"<b>{escape(title)}</b>", question)], [P(content, question)]]
    t=Table(cells, colWidths=[17.1*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),("BOX",(0,0),(-1,-1),0.7,border),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
    ]))
    return [t,Spacer(1,7)]


def answer_box(text):
    t=Table([[P(text,body)]],colWidths=[17.1*cm],hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GREEN_LIGHT),("BOX",(0,0),(-1,-1),0.6,colors.HexColor('#9BC9AB')),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return [t,Spacer(1,7)]


def image(path, label, width=17*cm, max_h=19*cm):
    im=Image(str(path))
    ratio=im.imageHeight/im.imageWidth
    im.drawWidth=width; im.drawHeight=width*ratio
    if im.drawHeight>max_h:
        im.drawHeight=max_h; im.drawWidth=max_h/ratio
    return [Spacer(1,5),im,P(label,caption)]


def table(rows,widths,head=True):
    data=[[c if hasattr(c,'wrapOn') else P(str(c),small) for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1 if head else 0,hAlign="LEFT")
    commands=[("GRID",(0,0),(-1,-1),0.4,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]
    if head: commands += [("BACKGROUND",(0,0),(-1,0),BLUE_LIGHT),("TEXTCOLOR",(0,0),(-1,0),BLUE)]
    t.setStyle(TableStyle(commands)); return t


def qtitle(n,title): return [CondPageBreak(72*mm),P(f"{n}. {title}",h1)]


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE); canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont("CJK",8); canvas.setFillColor(MUTED)
    canvas.drawString(18*mm,9*mm,"2022 年软件工程 II 往年卷参考答案（非官方）")
    canvas.drawRightString(192*mm,9*mm,str(doc.page))
    canvas.restoreState()


prepare_assets()
story=[]

# Cover
story += [Spacer(1,50*mm),P("2022 年软件工程 II 往年卷",cover_title),Spacer(1,4*mm),P("完整参考答案",cover_title),Spacer(1,8*mm),P("保留原题描述 · 图形答案均以图片嵌入 · 覆盖十个考试模块",cover_sub),Spacer(1,25*mm)]
story += answer_box("说明：本文件依据工作区中的《2022 (2).pdf》和课程课件整理，不是官方标准答案。开放题可能存在多种合理建模方式；评分时应优先服从任课教师课件中的符号、命名和粒度要求。")
story += [Spacer(1,28*mm),P("校园卡自助系统 / 你南 App",cover_sub),PageBreak()]

# Context
story += [P("原卷场景与界面材料",h1)]
story += box("原题背景","场景：你南 App。后续需求、分析、体系结构、详细设计、人机交互与测试题均围绕校园卡自助系统展开。")
story += image(ASSET/"ui-screens.png","原卷第 2-7 页界面截图汇总：服务入口、生活服务、明细查询、充值、密码确认与充值成功。",16.8*cm,18.4*cm)
story += [PageBreak(),P("目录与答题口径",h1)]
story += [P("一、简答题　　二、需求获取　　三、需求分析　　四、体系结构　　五、详细设计",toc),P("六、模块化与信息隐藏　　七、设计模式　　八、软件构造　　九、人机交互　　十、软件测试",toc),Spacer(1,8)]
story += answer_box("作图口径：用例图与概念类图使用业务语言；详细设计图使用设计阶段名称；包图的依赖箭头指向“被依赖方”；顺序图时间自上而下。所有答案图均已转换为 PNG 图片嵌入。")

# Q1
story += qtitle("一","简答题")
story += box("原题","1. 什么是软件工程？<br/>2. 配置管理中变更控制的过程。<br/>3. 迭代增量模型和演化模型的差异及优缺点。")
story += [P("1. 什么是软件工程",h2)] + answer_box("软件工程是将系统化、规范化、可度量的方法应用于软件的开发、运行和维护，并研究这些方法的学科。它通过过程、方法和工具管理软件的复杂性与变化，在质量、成本、进度和可维护性之间取得平衡。")
story += [P("2. 配置管理中的变更控制",h2),bullets([
    "提出变更请求：说明变更原因、目标、范围、优先级及关联配置项。",
    "登记与初审：检查信息完整性，分类并确定是否进入影响分析。",
    "影响分析：分析对需求、设计、代码、测试、成本、进度、风险和已发布版本的影响。",
    "审批决策：由负责人或变更控制委员会决定批准、拒绝或延期，并确定实施版本。",
    "实施与验证：修改受控配置项，进行评审、测试和回归测试。",
    "更新基线与记录：同步文档、测试、版本号和配置状态报告，必要时执行配置审计并关闭请求。",
])]
story += [P("3. 迭代增量模型与演化模型",h2),table([
    ["比较项","迭代增量模型","演化模型"],
    ["核心思想","把系统分成多个可交付增量，每次迭代完成分析、设计、实现和测试，并逐步扩充功能。","先形成可运行核心或原型，再根据使用反馈持续修改需求、结构和实现，使系统随认识共同演化。"],
    ["适用情况","总体目标较清楚，可以按价值和依赖拆分增量。","需求高度不确定、创新性强，需要通过原型或早期版本探索。"],
    ["优点","较早交付价值；风险分散；每轮可验证；便于吸收反馈和控制范围。","快速验证需求；适应变化强；用户持续参与；能减少“做错产品”的风险。"],
    ["缺点","需要稳定架构和良好增量规划；跨增量依赖处理困难；频繁集成有成本。","容易形成临时性结构和技术债；范围、成本和完成标准较难控制；若忽视重构，质量会退化。"],
],[2.6*cm,7.2*cm,7.2*cm])]

# Q2
story += qtitle("二","需求获取")
story += box("原题","1. 写出校园卡自助系统的用例。<br/>2. 针对充值功能，写出业务需求、用户需求、系统级需求。<br/>3. 系统需要提供 API 供其他管理系统调用，属于什么需求？还有什么对外接口？")
story += [P("1. 用例识别",h2)] + image(DIAG/"01-usecase.png","图 2-1　校园卡自助系统用例图（参考）",17*cm,10.4*cm)
story += [P("2. 充值功能的三个需求层次",h2),table([
    ["层次","参考答案"],
    ["业务需求","学校希望提供安全、便捷的线上校园卡充值能力，减少人工窗口业务量，提高资金到账效率，并形成可审计的充值记录。可度量目标示例：80% 以上充值在线完成，成功交易 1 分钟内到账。"],
    ["用户需求","师生能够查看余额，选择预设或自定义金额、优惠券与支付方式，完成身份/支付验证；充值后查看结果、新余额和充值记录；失败时能够获知原因并重试。"],
    ["系统级需求","系统接收卡号、金额、优惠券和支付方式，校验身份、金额、卡状态及优惠券；计算实付金额；调用第三方支付；支付成功后以事务方式更新校园卡余额、记录流水并核销优惠券；支付失败不增加余额且保留失败记录。"],
    ["质量与约束补充","敏感数据加密传输；关键操作需要认证；防止重复提交；支付回调具备幂等性；完整审计；典型查询响应不超过 2 秒。"],
],[3.2*cm,13.8*cm])]
story += [P("3. 对外接口需求",h2)] + answer_box("向其他管理系统提供 API 属于“对外接口需求”，通常在系统级需求中单独描述；它也会带来安全性、性能和兼容性等非功能约束。对外接口一般包括：用户接口、硬件接口、软件接口和通信接口。此系统还可能连接统一身份认证、校园卡中心、银行/支付宝/微信、消息通知服务以及数据库；应规定协议、数据格式、认证、超时、错误码和版本策略。")

# Q3
story += qtitle("三","需求分析")
story += box("原题","学校师生可以进行充值、查询余额、绑定银行卡、查询明细等操作。<br/>1. 分析名词，确定概念类。<br/>2. 辨识概念类之间的联系（包括依赖、关联、聚合、组合、继承）。<br/>3. 识别重要属性，画出概念类图。")
story += [P("名词与概念类",h2),table([
    ["题干名词/业务信息","概念类及理由"],
    ["师生","抽象为用户；学生、教师是用户的具体类型。"],
    ["校园卡、余额、状态","校园卡是核心实体；余额和状态是其属性。"],
    ["银行卡、绑定","银行卡是可被用户绑定的外部支付账户。"],
    ["充值、查询明细","充值记录与交易明细是业务事件/记录；充值记录可视为交易明细的一种。"],
],[5.5*cm,11.5*cm])]
story += image(DIAG/"02-concept.png","图 3-1　概念类图（参考答案）",17*cm,10.4*cm)
story += answer_box("说明：概念类图不写方法。普通关联表示稳定业务关系；聚合表示银行卡可独立存在；组合用于校园卡和其交易明细的强生命周期关系；学生/教师、充值记录使用继承；虚线依赖只表达一次性“充值后更新余额”的使用关系。若教师要求概念模型只画关联，也可去掉该依赖。")

# Q4
story += qtitle("四","体系结构")
story += box("原题","1. 画出整个校园卡自助系统的物理包图。分为客户端和服务器端，体现分层概念，包含所有模块。HTML、CSS、JavaScript 和展示层在客户端，逻辑层和数据层在服务器端，使用 HTTP 通信和 REST API。<br/>2. 针对充值服务（充值、查询充值记录），写出展示层和逻辑层间接口以及逻辑层和数据层间接口，注意写出接口所在包名。")
story += image(DIAG/"03-physical-package.png","图 4-1　校园卡自助系统物理包图",17*cm,10.4*cm)
story += [P("2. 充值服务接口设计",h2),P("为避免用实现代码表达，这里用接口契约表保留包名、接口名、方法与职责。",small)]
story += [table([
    ["层间接口","包名与接口","方法签名（设计名称）","职责"],
    ["展示层 → 逻辑层","edu.nju.card.service.RechargeService","recharge(RechargeRequestVO): RechargeResultVO","校验请求、计算优惠、调用支付、更新余额并返回结果。"],
    ["展示层 → 逻辑层","edu.nju.card.service.RechargeService","queryRechargeRecords(userId, from, to): List&lt;RechargeRecordVO&gt;","按用户和时间范围查询充值记录，返回展示所需 VO。"],
    ["逻辑层 → 数据层","edu.nju.card.dao.CampusCardDAO","findByCardId(cardId): CampusCardPO","读取校园卡持久化对象。"],
    ["逻辑层 → 数据层","edu.nju.card.dao.CampusCardDAO","increaseBalance(cardId, amount, version): boolean","使用事务/乐观锁原子增加余额。"],
    ["逻辑层 → 数据层","edu.nju.card.dao.RechargeRecordDAO","save(recordPO): void","保存成功或失败的充值记录。"],
    ["逻辑层 → 数据层","edu.nju.card.dao.RechargeRecordDAO","findByUserAndTime(userId, from, to): List&lt;RechargeRecordPO&gt;","查询充值持久化记录。"],
],[2.7*cm,4.1*cm,5.5*cm,4.7*cm])]
story += answer_box("依赖方向：Controller 只依赖 Service 接口；ServiceImpl 实现 Service 接口并依赖 DAO 接口；DAOImpl 实现 DAO 接口。展示层不能直接访问 DAO，ServiceImpl 不能绕过 DAO 接口依赖具体 DAO 实现。")

# Q5
story += qtitle("五","详细设计")
story += box("原题","用户在充值时有不同的优惠券，同时可以用不同的充值方式（支付宝、微信等）。<br/>1. 画出 User、Card、多种 Coupon、ThirdPayment、PaymentRecord 类图。<br/>2. 当添加新的优惠券（有数值折扣、比例折扣）时，系统如何实现变更？<br/>3. 画出充值时对象交互的顺序图。")
story += image(DIAG/"04-detail-class.png","图 5-1　优惠券与第三方支付详细设计类图",17*cm,10.4*cm)
story += [P("2. 新增优惠券时的变更方式",h2)] + answer_box("将 Coupon 定义为稳定抽象，统一提供 calculatePayable(amount) 或 calculateDiscount(amount)。数值折扣和比例折扣分别作为 FixedAmountCoupon、PercentageCoupon 实现。充值服务只调用 Coupon 接口，不写类型判断。新增优惠券时只增加一个实现类，并通过工厂、依赖注入或配置注册；原有充值主流程无需修改，符合开闭原则、依赖倒置和里氏替换。")
story += [P("3. 对象交互顺序图",h2)] + image(ROOT/"output"/"2022年第五题-充值详细顺序图.png","图 5-2　充值详细顺序图：同时覆盖支付成功与失败分支",17*cm,13.4*cm)

# Q6
story += qtitle("六","模块化与信息隐藏")
story += box("原题","1. 用户包持有优惠券包中的优惠券，优惠券包又查询用户包信息以发放优惠券。违反了什么包原则？如何修改？画出修改后的包图和类图。<br/>2. 根据原题程序回答：（1）issueCoupon 和 addCoupon 是哪种耦合？可以接受吗？如何修改？（2）addCoupon 中多次调用 user 的 addCoupon，如何优化？")
story += image(ASSET/"issue-coupon-code.png","原题程序截图（保留原题材料）",15.5*cm,6.5*cm)
story += [P("1. 包原则与修改",h2)] + answer_box("两个包相互依赖形成环，违反无环依赖原则（ADP），也使包难以独立发布、测试和复用。修改时把“发放优惠券”的用例编排移入独立 application 包，并在稳定的 user.api 包中定义 CouponRecipient 接口；User 实现该接口，coupon 包保持纯粹，不再查询 user 包。依赖均指向抽象或领域包，图中不再有闭环。")
story += image(DIAG/"05-cycle-package.png","图 6-1　消除循环依赖后的包图",17*cm,10.4*cm)
story += image(DIAG/"06-cycle-class.png","图 6-2　消除循环依赖后的类图",17*cm,10.4*cm)
story += [KeepTogether([P("2. 方法耦合与重复调用",h2),bullets([
    "issueCoupon 把 type 作为控制信息传给 addCoupon，使被调用方法根据标志选择分支，属于控制耦合。控制耦合提高理解和修改成本，一般不应保留在可扩展业务规则中。",
    "用 CouponFactory 或 CouponPolicy 根据 UserType 创建 Coupon；发放服务依赖抽象，不再使用 switch。也可把策略与 UserType 绑定，通过多态选择规则。",
    "先得到唯一的 coupon 变量，再执行一次 recipient.addCoupon(coupon)，消除每个 case 中重复的调用。对未知类型应显式返回失败或抛出领域异常。",
])])]

# Q7
story += qtitle("七","设计模式")
story += box("原题","1. 以下类图违反了什么类的设计原则？如何优化？<br/>2. 用户有微信支付、支付宝支付，预计未来还会有更多支付方式。使用哪种设计模式可以方便实现？这种设计模式有什么好处？使用了哪些类设计原则？画出这种设计模式的类图描述。")
story += image(ASSET/"original-bad-class.png","原题待改类图（保留原题材料）",14.5*cm,10.3*cm)
story += [P("1. 类设计原则分析",h2)] + answer_box("Payment 接口同时声明电费、水费、餐费三个互不相关的方法，使每个交易实现类被迫依赖自己不用的操作，主要违反接口隔离原则（ISP），也削弱单一职责。直接优化是把 Payment 拆成 ElectricPayment、WaterPayment、DinnerPayment 三个小接口；每个交易类只实现 Transaction 和自己的付款接口。若三种行为签名完全一致，还可进一步统一为单方法 Payment 接口，由交易对象作为参数。")
story += image(DIAG/"07-isp.png","图 7-1　按接口隔离原则优化后的类图",17*cm,10.4*cm)
story += [P("2. 多支付方式设计",h2)] + answer_box("使用策略模式。PaymentStrategy 定义统一 pay(amount)；AlipayPayment、WechatPayment 等封装具体算法；RechargeService（Context）持有并调用一个策略。好处是算法可替换、消除大段条件分支、便于独立测试，新增支付方式只增加实现类。它体现开闭原则、依赖倒置、单一职责、里氏替换以及组合优于继承。")
story += image(DIAG/"08-strategy.png","图 7-2　第三方支付策略模式类图",17*cm,10.4*cm)

# Q8
story += qtitle("八","软件构造")
story += box("原题","从软件构造的角度分析以下程序的优缺点。")
story += image(ASSET/"issue-coupon-code.png","原题程序截图（issueCoupon / addCoupon）",15.5*cm,6.5*cm)
story += [P("优点",h2),bullets([
    "结构短小，issueCoupon 与单个用户的发放逻辑初步分离，循环意图容易看懂。",
    "使用 List&lt;User&gt; 和增强 for 循环，基本类型信息明确；每个 case 有 break，不会意外贯穿。",
])]
story += [P("缺点",h2),bullets([
    "使用整数 type 和 switch 表达业务规则，存在魔法值，违反开闭原则；每新增用户类型或优惠券都要修改原方法。",
    "addCoupon 同时负责规则选择、对象创建和发放，职责过多，并直接依赖具体 Coupon 类，耦合高、测试困难。",
    "每个分支重复调用 u.addCoupon；未知类型没有 default 或明确失败处理。",
    "缺少空集合、空用户、重复发放、优惠券库存/有效期、异常和部分成功处理；批量发放的事务边界不清楚。",
    "命名和类型不够安全：应使用 UserType 枚举而不是 int；应明确方法可见性、返回结果和错误语义。",
])]
story += [P("建议",h2),bullets([
    "引入 CouponFactory / CouponPolicy，采用映射或多态按 UserType 创建 Coupon；发放服务依赖接口并由依赖注入提供策略。",
    "创建完 Coupon 后只调用一次 addCoupon；补充参数校验、幂等键、日志、失败结果与必要的事务控制。",
    "将规则选择、优惠券创建、用户资格校验和持久化分开，使各组件可以独立单元测试。",
])]

# Q9
story += qtitle("九","人机交互")
story += box("原题","从人机交互的角度分析校园卡自助系统，说出好的地方；说出不好的地方并给出建议（至少三点）。")
story += [P("好的地方",h2),bullets([
    "首页按校园卡、图书、网络等业务分组，图标配文字，符合识别优于回忆，信息层次清楚。",
    "充值页展示余额、预设金额、自定义金额、支付方式和充值记录入口，核心任务路径较短。",
    "颜色、按钮和卡片风格总体一致；充值完成后立即弹出反馈，系统状态可见。",
    "明细页支持日期和类型筛选，并在每条记录中展示地点、时间、金额和余额。",
])]
story += [P("问题与改进建议",h2),table([
    ["问题/原则","改进建议"],
    ["充值时突然出现只有圆点的密码框，字段含义不清，文案“修改在线支付密码”容易误导。","明确标题为“请输入校园卡支付密码”，增加字段标签、忘记密码入口、剩余次数和错误提示；提供显示/隐藏密码。"],
    ["成功弹窗只显示“充值成功”，缺少金额、方式、时间、新余额和流水号。","在结果页展示交易摘要、电子回执、查看充值记录入口；失败时给出可执行原因和重试/联系客服操作。"],
    ["主按钮禁用/可用状态和对比度不够明显，用户不易判断为何不能提交。","在未选金额或支付方式时给出就地提示；确保按钮颜色、文字对比度和选中态达到可访问性要求。"],
    ["充值涉及不可逆资金操作，但缺少金额确认和防重复提交提示。","提交前显示确认摘要；点击后锁定按钮并显示进度；后台使用幂等机制，允许用户安全返回。"],
    ["优惠券未在充值界面体现，用户无法预知优惠和实付金额。","增加优惠券选择、可用条件、优惠金额和应付金额，默认推荐最优方案但允许更换。"],
    ["明细筛选结果缺少空状态、加载状态和导出能力。","提供骨架屏、无记录说明、重置筛选、分页/加载更多及下载对账单。"],
],[6.2*cm,10.8*cm])]

# Q10
story += qtitle("十","软件测试")
story += box("原题","条件覆盖是指保证程序中每个判断的每个结果都至少满足一次。对上文 doPost 方法：<br/>1. 计算圈复杂度。<br/>2. 设计最小的 100% 条件覆盖测试用例集。只需要提供 old、new1、new2 的值，username 可不考虑。（注意短路判断特性）")
story += image(ASSET/"do-post-code.png","原题 doPost 程序截图（保留原题材料）",15.5*cm,9.2*cm)
story += [P("1. 圈复杂度",h2)]
story += answer_box("令 A = new1 包含 new2；B = old 不包含 new1；C = new2 包含 new1；D = new1 不包含 old；E = loginUser(username, old)。Java 的 && 使用短路求值，控制流中 A、B、C、D 和 E 都是判定节点，因此 V(G) = 判定节点数 5 + 1 = 6。若只把整个复合 if 当成一个判定会得到 3，但本题特别强调短路特性，应按展开后的控制流取 6。")
story += image(DIAG/"09-cfg.png","图 10-1　短路条件控制流骨架",17*cm,9.6*cm)
story += [P("2. 最小 100% 条件覆盖测试集",h2)]
story += [table([
    ["用例","old","new1","new2","本次首次获得的关键结果"],
    ["T1","x","a","b","A = F，后续条件因短路不求值"],
    ["T2","zabz","ab","a","A = T，B = F"],
    ["T3","x","ab","a","A = T，B = T，C = F"],
    ["T4","a","ab","ab","A = T，B = T，C = T，D = F"],
    ["T5","validOld","N3wPwd!","N3wPwd!","A、B、C、D = T；桩设 E = T"],
    ["T6","invalidOld","N3wPwd!","N3wPwd!","A、B、C、D = T；桩设 E = F"],
],[1.3*cm,3*cm,3.3*cm,3.3*cm,6.1*cm])]
story += answer_box("最小性说明：要让 A、B、C、D 各自取到 F，受短路影响至少需要 4 个分别在对应位置失败的用例；要让 E 同时取 T 和 F，又必须有 2 个外层四条件均为 T 的用例，因此最少 6 个。T5/T6 中 validOld、invalidOld 表示让登录桩分别返回真、假，username 不作为输入变量考察。")

doc=BaseDocTemplate(str(OUT),pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=17*mm,bottomMargin=18*mm,title="2022年软件工程II往年卷参考答案",author="Codex")
frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="normal")
doc.addPageTemplates([PageTemplate(id="main",frames=[frame],onPage=header_footer)])
doc.build(story)
print(OUT)
