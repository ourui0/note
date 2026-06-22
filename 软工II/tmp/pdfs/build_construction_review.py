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
OUT = ROOT / "output" / "pdf" / "软件工程II构造篇复习.pdf"
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
styles.add(ParagraphStyle(name="CodeCN", parent=styles["Code"], fontName="Courier", fontSize=7.35, leading=9.7, textColor=colors.HexColor("#111827")))


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
    canvas.drawString(1.7 * cm, 1.0 * cm, "软件工程II 期末复习 - 构造篇")
    canvas.drawRightString(19.3 * cm, 1.0 * cm, f"{doc.page}")
    canvas.restoreState()


story = []
story.append(Spacer(1, 2.2 * cm))
story.append(p("软件工程II", "Subtitle"))
story.append(Paragraph("构造篇期末复习", styles["TitleCN"]))
story.append(p("依据：软件构造、代码设计课件，123.txt 答疑转写，考试题目类型与重点，往年卷构造题。", "Subtitle"))
story.append(note("使用建议", "构造题通常让你评价一段代码并改写。答题要按“正确性 - 可读性 - 可维护性 - 可靠性 - 测试/复杂度”的顺序分析，最后给出更清晰、更安全的伪代码或 Java 代码。"))
story.append(PageBreak())

story.append(h1("一、考试定位与优先级"))
story.append(table([
    ["优先级", "内容", "为什么重要", "答题产物"],
    ["高", "代码质量评价：正确、易读、可靠、可维护", "2020、2022 都有构造题要求分析代码优缺点", "列问题 + 解释影响 + 给改写代码"],
    ["高", "命名、格式、注释、魔法数字、复杂判断", "代码设计课件重点；往年卷代码故意写得很差", "指出坏味道并重构"],
    ["高", "异常、断言、防御式编程、边界情况", "答疑提到基本 assertion 概念要知道；构造题常考可靠性", "输入校验、边界处理、异常语义"],
    ["中高", "圈复杂度", "2022 测试题直接让算，但属于代码结构度量", "按判定节点 + 1 或控制流图计算"],
    ["中", "重构、TDD、单元测试、代码评审、调试", "构造活动常考简答或作为代码分析理由", "定义、步骤、优点、适用时机"],
    ["中", "持续集成 CI 和工具链", "2020 简答出现过", "好处 + 典型工具链"],
], widths=[2.0 * cm, 4.2 * cm, 5.1 * cm, 5.1 * cm]))
story.append(note("一句话判断", "构造题不是让你展示语法细节，而是让你证明自己能把代码写到“别人一看就明白、边界不出错、后续容易改”的程度。"))

story.append(h1("二、软件构造基础"))
story.append(h2("1. 什么是软件构造"))
story.append(p("软件构造是通过编码、验证、单元测试、集成测试和调试等工作，生产可工作的、有意义的软件的详细创建过程。它不是“只写代码”，而是设计落地、测试验证、调试修复、代码评审、构建集成和构造管理的组合。"))
story.extend(img("construction_activities.png", "课件截图：软件构造活动。构造包含详细设计调整、编程、测试、调试、评审、构建和管理。"))
story.append(h2("2. 代码质量目标"))
story.append(table([
    ["质量", "含义", "构造题常见表现"],
    ["易读性", "代码显而易见是正确的，别人能快速理解", "命名清晰、格式规范、控制结构简单、注释有意义"],
    ["易维护性", "代码容易修改和扩展", "方法短小、职责单一、避免重复、避免魔法数字"],
    ["可靠性", "执行正确并能妥善处理故障", "边界值、非法输入、异常、资源释放、状态一致性"],
    ["性能", "时间和空间效率合理", "选择合适数据结构和算法，避免不必要重复计算"],
    ["安全性", "不泄露重要信息，不留下漏洞", "输入校验、权限控制、避免越界和注入类问题"],
], widths=[2.4 * cm, 6.0 * cm, 8.0 * cm]))
story.extend(img("code_quality.png", "课件截图：程序代码的典型质量。构造题可以按这五类逐条分析。"))

story.append(PageBreak())
story.append(h1("三、设计易读的代码"))
story.append(h2("1. 格式和逻辑组织"))
story.append(bullets([
    "使用缩进、对齐和空行表达逻辑结构。",
    "相关逻辑放在一起，复杂控制结构之间用空行分割。",
    "类定义内部可按成员变量、构造方法、public、protected、private 方法组织。",
    "条件和循环即使只有一行，也建议使用 `{}`，减少维护时误解。",
]))
story.append(h2("2. 命名"))
story.append(bullets([
    "类、属性、数据用名词；方法用动词或动词+名词；接口用名词或形容词。",
    "名称要表达真实职责，例如 `calculateStockDays` 比 `aa`、`doIt` 更好。",
    "遵守语言命名惯例；避免易混字符、无意义缩写、过长名称。",
    "临时变量可短，但业务变量必须有意义。",
]))
story.extend(img("naming_rules.png", "课件截图：命名规则。2020 构造题中的 `aa(int aa)` 是典型反例。"))
story.append(h2("3. 注释"))
story.append(bullets([
    "注释解释意图、约束、边界和复杂控制结构，不要重复代码字面含义。",
    "方法文档应说明参数、返回值和可能异常。",
    "注释必须和代码同步，错误注释比没有注释更危险。",
]))
story.extend(img("comment_rules.png", "课件截图：内部注释。重点不是注释越多越好，而是解释代码没有直接表达的信息。"))

story.append(h1("四、设计易维护的代码"))
story.append(h2("1. 小型任务与复杂决策"))
story.append(bullets([
    "每个函数/方法应内聚地完成一个目标；长方法说明它承担了太多任务。",
    "复杂判断可提取为有意义的布尔变量或方法，例如 `isLeadTimeInThreeDays(days)`。",
    "多分支规则可用 `else if`、表驱动、策略模式或规则对象，避免散乱的多个独立 if。",
]))
story.extend(img("small_tasks.png", "课件截图：小型任务。构造题中长方法、混合职责通常要拆分。"))
story.extend(img("complex_decision.png", "课件截图：复杂决策。把难懂条件封装成命名清晰的判断。"))
story.append(h2("2. 数据使用"))
story.append(bullets([
    "变量不要一变量多用，名称应与用途一致。",
    "限制全局变量；必须使用时要说明含义和使用范围。",
    "魔法数字/字符串要提取为具名常量，例如 `SEVEN_DAYS_STOCK = 7`。",
    "方法参数不要过多；必要时用参数对象，但避免印记耦合。",
]))
story.extend(img("data_use.png", "课件截图：数据使用。魔法数字、变量复用和全局变量是构造题常见扣分点。"))

story.append(PageBreak())
story.append(h1("五、设计可靠的代码"))
story.append(h2("1. 异常、断言、防御式编程"))
story.append(table([
    ["方式", "适用", "考试表述"],
    ["异常", "处理运行时可能发生、调用者需要知道的错误", "非法参数、外部资源失败、业务前置条件不满足时抛出或返回明确错误"],
    ["断言", "检查程序员假设/内部不变式，主要用于调试和契约检查", "基本概念要知道，不考特殊语法；可用伪代码表示 assert"],
    ["防御式编程", "不能保证外部输入和环境正确时，保护内部状态", "检查输入、边界、空值、资源状态和外部方法返回值"],
], widths=[2.7 * cm, 6.4 * cm, 7.3 * cm]))
story.extend(img("reliable_code.png", "课件截图：可靠代码。异常、断言、防御式编程分别服务于不同错误场景。"))
story.append(h2("2. 常见错误与修复"))
story.append(bullets([
    "边界错误：`<` 和 `<=` 混用，导致边界值走错分支。",
    "条件遗漏：规则区间不连续，某些输入无法得到合理结果。",
    "逻辑错误：多个独立 `if` 可能相互覆盖，应使用互斥 `else if`。",
    "硬编码：规则数字散落在代码中，变更时容易漏改。",
    "异常缺失：负数、空值、未知类型未处理。",
]))
story.extend(img("defect_fix.png", "课件截图：修复缺陷注意点。一次修复一个缺陷，并用测试和评审验证。"))

story.append(h1("六、重构、评审、调试与 TDD"))
story.append(h2("1. 重构"))
story.append(p("重构是在不改变外部行为的前提下改进内部结构。它不能用来实现新功能，而是在新增功能后、修复缺陷时、代码评审发现坏味道时，用来降低复杂度和改善可维护性。"))
story.append(table([
    ["坏味道", "问题", "常见重构"],
    ["长方法", "职责太多、难测试", "提取方法、拆分步骤"],
    ["过多参数", "接口不简洁，调用方负担重", "拆方法或引入参数对象"],
    ["重复代码", "修改易漏", "提取公共方法"],
    ["魔法数字/字符串", "含义不清，规则变更难", "具名常量、枚举、配置表"],
    ["深层嵌套", "圈复杂度高、难读", "卫语句、提取条件、策略模式"],
], widths=[3.2 * cm, 6.2 * cm, 7.0 * cm]))
story.extend(img("refactoring.png", "课件截图：重构。构造题给改写代码时，本质就是一次小型重构。"))

story.append(PageBreak())
story.append(h2("2. 代码评审"))
story.append(bullets([
    "代码评审是对代码的系统检查，可发现代码错误、坏味道和规范问题。",
    "形式包括正式评审、轻量级评审和结对编程。",
    "评审点：逻辑正确性、边界处理、异常处理、命名格式、重复代码、接口依赖、安全风险。",
]))
story.extend(img("code_review.png", "课件截图：代码评审。AI 可以辅助发现坏味道，但最终判断仍需要开发者理解业务。"))
story.append(h2("3. 调试"))
story.append(bullets([
    "调试目标是定位并修复缺陷，过程包括重现问题、诊断缺陷、修复缺陷。",
    "重现问题可控制输入或控制环境；定位时先检查刚修改过的部分。",
    "修复后要补测试，检查同类缺陷是否还存在。",
]))
story.append(h2("4. TDD"))
story.append(bullets([
    "TDD 循环：Red 先写失败测试，Green 写最少代码通过测试，Refactor 在测试保护下重构。",
    "优点：驱动接口设计、提高可测试性、保护重构、减少回归缺陷。",
    "注意：测试用例仍要由开发者审查业务正确性，不能盲信自动生成测试。",
]))
story.extend(img("tdd_cycle.png", "课件截图：测试驱动开发。构造阶段单元测试和重构互相支撑。"))

story.append(h1("七、圈复杂度"))
story.append(h2("1. 计算方法"))
story.append(bullets([
    "控制流图公式：`V(G) = E - N + 2P`，一般单个方法 P=1。",
    "考试快速算法：圈复杂度 = 判定节点数 + 1。",
    "常见判定节点：`if`、`else if`、`while`、`for`、`case`、`catch`、三目运算等。",
    "复合条件是否额外计数要看课程/题目要求。若按基础 McCabe，通常每个判定语句 +1；若题目考条件覆盖，短路条件要单独分析测试。",
]))
story.extend(img("cyclomatic_complexity.png", "课件截图：圈复杂度。用它判断代码是否过复杂、是否需要重构。"))
story.append(h2("2. 常见例子"))
story.append(code("""
int f(int x) {
    if (x < 0) return -1;      // +1
    if (x == 0) return 0;      // +1
    return 1;
}
// 圈复杂度 = 2 个 if + 1 = 3

void g(int x) {
    switch (x) {
        case 1: ...
        case 2: ...
        default: ...
    }
}
// 常见算法：每个 case 分支会增加路径，按题目约定计算。
"""))

story.append(PageBreak())
story.append(h1("八、往年卷风格例题与答案"))
story.append(h2("例题 1：2020 订货规则代码评价与改写"))
story.append(p("原题代码大意：根据供应商交货期返回备货销量天数，但代码写成 `public int aa(int aa){...}`，使用多个独立 if 和魔法数字。"))
story.append(code("""
public int aa(int aa){int bb = 0;if(aa < 3) bb= 7;
if(aa < 7 && aa >=3) bb = 15;
if(aa < 10 && aa >= 7 ) bb = 20;
if(aa < 15 && aa >= 10) bb = 30;
if(aa >= 20) bb = 40;
return bb;}
"""))
story.append(h2("1. 可指出的问题"))
story.append(bullets([
    "命名差：`aa`、`bb` 完全不能表达含义，违反易读性要求。",
    "格式差：所有语句挤在一起，缺少缩进、换行和代码块。",
    "魔法数字：3、7、10、15、20、40 等规则数字散落，缺少常量名。",
    "边界错误：题目说“3 天以内/7 天以内”，通常应包含边界，代码用 `<` 排除了 3、7、10、15。",
    "规则区间不连续：15 到 19 天没有分支，会返回默认 0，可靠性差。",
    "多个独立 if：规则本应互斥，应该使用 `else if` 或表驱动表达。",
    "缺少非法输入处理：负数交货期不应正常返回。",
]))
story.append(h2("2. 改写示例"))
story.append(code("""
private static final int STOCK_DAYS_FOR_3_DAYS = 7;
private static final int STOCK_DAYS_FOR_7_DAYS = 15;
private static final int STOCK_DAYS_FOR_10_DAYS = 20;
private static final int STOCK_DAYS_FOR_15_DAYS = 30;
private static final int STOCK_DAYS_FOR_20_OR_MORE_DAYS = 40;

public int calculateStockDays(int leadTimeDays) {
    if (leadTimeDays < 0) {
        throw new IllegalArgumentException(\"leadTimeDays must be non-negative\");
    }
    if (leadTimeDays <= 3) {
        return STOCK_DAYS_FOR_3_DAYS;
    } else if (leadTimeDays <= 7) {
        return STOCK_DAYS_FOR_7_DAYS;
    } else if (leadTimeDays <= 10) {
        return STOCK_DAYS_FOR_10_DAYS;
    } else if (leadTimeDays <= 15) {
        return STOCK_DAYS_FOR_15_DAYS;
    } else if (leadTimeDays >= 20) {
        return STOCK_DAYS_FOR_20_OR_MORE_DAYS;
    }
    throw new IllegalArgumentException(\"no reorder rule for leadTimeDays\");
}
"""))
story.append(note("关于 16-19 天", "原题规则写成“15 天以内”和“20 天以上”，中间 16-19 天语义不明确。可靠代码不能悄悄返回 0；应抛异常或在答案中说明需要澄清需求。如果老师默认规则连续，也可把最后一段写成 `else return 40`。"))

story.append(PageBreak())
story.append(h2("例题 2：2022 发券代码优缺点"))
story.append(code("""
void issueCoupon(List<User> users){
    for(user:users){
        addCoupon(user,user.getType());
    }
}
void addCoupon(User u,int type){
    switch(type){
        case STUDENT:u.addCoupon(new FiveYuanCoupon());break;
        case TEACHER:u.addCoupon(new TenYuanCoupon());break;
        ...
    }
}
"""))
story.append(h2("1. 可说的优点"))
story.append(bullets([
    "结构直接，容易看出遍历用户并按类型发券。",
    "发券逻辑集中在 `addCoupon` 中，比散落在多处略好。",
]))
story.append(h2("2. 主要问题"))
story.append(bullets([
    "控制耦合：`type` 作为 flag 控制 `addCoupon` 内部 switch，调用者和被调用者都要知道类型含义。",
    "违反 OCP：新增用户类型或优惠券类型要修改 `switch`。",
    "违反 DIP：方法直接依赖具体优惠券类 `FiveYuanCoupon`、`TenYuanCoupon`。",
    "缺少防御式编程：`users`、`user` 可能为空，未知 type 没有处理。",
    "命名和格式可继续改善，例如泛型、变量名、空格、default 分支。",
]))
story.append(h2("3. 改写方向"))
story.append(code("""
interface CouponPolicy {
    Coupon createCouponFor(User user);
}

class StudentCouponPolicy implements CouponPolicy {
    public Coupon createCouponFor(User user) {
        return new FiveYuanCoupon();
    }
}

class TeacherCouponPolicy implements CouponPolicy {
    public Coupon createCouponFor(User user) {
        return new TenYuanCoupon();
    }
}

class CouponIssuer {
    private final Map<UserType, CouponPolicy> policies;

    public void issueCoupons(List<User> users) {
        if (users == null) {
            throw new IllegalArgumentException(\"users must not be null\");
        }
        for (User user : users) {
            issueCoupon(user);
        }
    }

    private void issueCoupon(User user) {
        if (user == null) {
            return;
        }
        CouponPolicy policy = policies.get(user.getType());
        if (policy == null) {
            throw new IllegalArgumentException(\"unsupported user type\");
        }
        user.addCoupon(policy.createCouponFor(user));
    }
}
"""))
story.append(bullets([
    "这相当于用策略/工厂思想封装发券变化点。",
    "新增类型时新增 `CouponPolicy`，尽量不改原有流程，符合 OCP。",
    "业务流程依赖 `CouponPolicy` 抽象，符合 DIP。",
]))

story.append(h1("九、构造题答题模板"))
story.append(h2("1. 分析代码问题模板"))
story.append(bullets([
    "正确性：边界是否对、分支是否完整、默认返回是否合理。",
    "可读性：命名、缩进、空行、注释、括号、逻辑组织。",
    "可维护性：魔法数字、重复代码、长方法、复杂判断、控制耦合。",
    "可靠性：非法输入、空值、未知类型、异常、资源释放。",
    "可测试性：分支是否容易覆盖，是否可用 Mock 隔离依赖。",
]))
story.append(h2("2. 改代码模板"))
story.append(code("""
1. Rename: use meaningful method/variable names.
2. Validate: check invalid input early.
3. Constants: replace magic numbers with named constants.
4. Branches: use clear if/else-if or table-driven rules.
5. Refactor: extract complex decisions into named methods.
6. Test: cover normal, boundary, and abnormal cases.
"""))
story.append(h2("3. 简答题速记"))
story.append(table([
    ["概念", "速记答案"],
    ["软件构造", "通过编码、验证、单元测试、集成测试、调试等工作生产可工作软件的过程"],
    ["调试", "重现问题、诊断缺陷、修复缺陷"],
    ["重构", "不改变外部行为，改善内部结构"],
    ["TDD", "Red-Green-Refactor"],
    ["代码评审", "同行系统检查代码，发现缺陷和坏味道"],
    ["CI", "频繁集成、自动构建、自动测试，尽早发现集成问题"],
    ["圈复杂度", "控制流图复杂度；快速算法为判定节点数 + 1"],
], widths=[3.3 * cm, 13.1 * cm]))

story.append(h2("4. 持续集成 CI"))
story.append(bullets([
    "好处：尽早发现集成错误，减少“大爆炸式集成”风险；自动运行构建和测试，提高反馈速度；保证主干代码持续可工作。",
    "工具链例子：Git/GitHub/GitLab 管理版本；Maven/Gradle/npm 构建；JUnit/pytest 运行测试；GitHub Actions/GitLab CI/Jenkins 执行流水线；SonarQube 做静态分析。",
]))


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
