from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from review_pdf_common import (
    ROOT,
    bullets,
    code,
    h1,
    h2,
    header_footer,
    note,
    numbered,
    p,
    slide,
    styles,
    table,
)


OUT = ROOT / "output" / "pdf" / "软件工程II模块化与信息隐藏篇复习.pdf"
story = []

story.append(Spacer(1, 2.2 * cm))
story.append(p("软件工程II", "Subtitle"))
story.append(Paragraph("模块化与信息隐藏篇期末复习", styles["TitleCN"]))
story.append(p("依据：04-02 面向对象的模块化与信息隐藏课件，123.txt，语音版重点，考试题目类型与重点，2020/2022 往年卷。", "Subtitle"))
story.append(note("使用建议", "本篇的最高优先级是类设计原则。做题时先识别代码或类图中的依赖和变化，再回答“违反什么原则、为什么、怎样重构”。控制耦合和印记耦合虽然不是今年最重内容，但往年卷直接考过，仍应会判断。"))
story.append(PageBreak())

story.append(h1("一、考试定位"))
story.append(table([
    ["优先级", "知识点", "依据", "典型题型"],
    ["高", "类设计原则 P1-P14，尤其 OCP、DIP、SRP、ISP、LSP", "答疑明确“类的原则都会考”", "给代码/类图，判断符合或违反哪些原则并优化"],
    ["高", "信息隐藏、面向接口、封装变化", "语音重点；也是设计模式的基础", "解释为什么要抽象接口、怎样隔离变化"],
    ["中高", "控制耦合、印记耦合", "123.txt 专门展开；2020/2022 有类似题", "判断耦合类型并重构"],
    ["中", "高内聚低耦合、消息链、迪米特法则、组合优于继承", "课件基础", "分析依赖、消息链和继承层次"],
    ["参考", "包原则与循环依赖", "答疑说本次非重点，但 2022 往年题出现", "识别循环依赖并通过接口/第三方包消除"],
], widths=[2.0 * cm, 5.1 * cm, 4.8 * cm, 4.5 * cm]))
story.append(note("一句话定位", "模块化与信息隐藏关心的是“变化能否被限制在一个模块内部”。高内聚让一个模块专心做一件事，低耦合让模块之间只通过稳定、最小的接口合作。"))

story.append(h1("二、模块化基础"))
story.append(h2("1. 什么是模块"))
story.append(p("模块是可以独立设计、实现和测试的自包含软件单元。面向对象系统中可以有方法级、类级和包级模块。模块的边界应围绕职责和变化原因建立，而不是机械地按文件数量划分。"))
story.append(table([
    ["粒度", "构件", "职责边界"],
    ["方法级", "Method / Function", "一个清晰操作"],
    ["类级", "Class", "相关状态与行为能力"],
    ["包级", "Package / Namespace", "相关类的集合与对外接口"],
], widths=[3.1 * cm, 5.1 * cm, 8.2 * cm]))
story.extend(slide("modular", 6, "课件截图：模块化的两个核心指标是耦合和内聚，目标是高内聚、低耦合。"))
story.append(h2("2. 内聚与耦合"))
story.append(bullets([
    "内聚：模块内部元素之间的关联程度，越高越好。高内聚意味着职责集中、变化原因少。",
    "耦合：模块之间的依赖强度，越低越好。低耦合意味着一个模块的修改不容易波及其他模块。",
    "高内聚与低耦合相互促进：职责分散常导致大量跨模块调用，职责集中则接口更小。",
]))

story.append(PageBreak())
story.append(h1("三、访问耦合与常见问题"))
story.append(h2("1. 访问耦合"))
story.append(p("类 A 调用类 B 的方法、访问字段、把 B 作为参数或沿消息链访问间接对象时，会产生访问耦合。设计目标不是完全消除依赖，而是让依赖指向稳定、最小的接口。"))
story.extend(slide("modular", 9, "课件截图：访问耦合强度。直接访问字段和实现细节会破坏封装。"))
story.append(h2("2. 消息链与迪米特法则"))
story.append(code("""
// 消息链：调用方知道了三层内部结构
String city = customer.getAddress().getCity().toUpperCase();

// 推荐：由 Customer 提供委托方法
String city = customer.getCityName();
"""))
story.append(bullets([
    "消息链暴露 Customer、Address、City 的内部组织方式；任一层变化都会影响调用者。",
    "迪米特法则：只与你的直接朋友交谈。方法只调用自身、参数、自己创建的对象和直接字段。",
    "仅引入局部变量能提高可读性，但不能降低结构耦合；真正的修复是委托和封装。",
]))
story.extend(slide("modular", 10, "课件截图：Cascading Message 问题与委托修复。"))

story.append(h2("3. 控制耦合"))
story.append(p("控制耦合是调用方传入 flag、类型码或字符串，用它控制被调用方法内部选择哪段逻辑。调用方和被调用方必须共同理解这些控制值的含义。"))
story.append(code("""
void addCoupon(User user, int type) {
    switch (type) {
        case STUDENT: user.addCoupon(new FiveYuanCoupon()); break;
        case TEACHER: user.addCoupon(new TenYuanCoupon()); break;
    }
}
"""))
story.append(p("改进方向：把类型差异封装为多态对象，让统一接口负责行为；或把不同职责拆成不同方法。新增类型时增加实现类，而不是修改 switch。"))

story.append(PageBreak())
story.append(h2("4. 印记耦合 Stamp Coupling"))
story.append(p("印记耦合是把完整数据结构或对象传给方法，但方法只使用其中少量字段。被调用方被迫依赖它不需要的结构。"))
story.append(code("""
// 只使用 employee.email，却传入完整 Employee
void sendEmail(Employee employee) {
    mailer.send(employee.getEmail());
}

// 只传递真正需要的信息
void sendEmail(String email) {
    mailer.send(email);
}
"""))
story.append(note("与 VO 的联系", "展示层只应得到界面真正需要的数据。返回 VO 而不是完整 PO，也是在减少不必要的数据依赖和印记耦合。"))
story.append(h2("5. 控制耦合与印记耦合对比"))
story.append(table([
    ["类型", "识别特征", "问题", "常见修复"],
    ["控制耦合", "flag/type 控制内部 if/switch", "双方共同依赖控制码语义", "多态、策略、拆分方法"],
    ["印记耦合", "传整个对象，只用少数字段", "依赖超出实际需要的数据结构", "只传必要值、窄接口、专用 DTO/VO"],
], widths=[2.8 * cm, 4.5 * cm, 4.5 * cm, 4.6 * cm]))

story.append(h1("四、面向接口与接口隔离"))
story.append(h2("1. 面向接口编程"))
story.append(code("""
// 依赖具体实现
ArrayList<String> names = new ArrayList<>();

// 依赖稳定接口
List<String> names = new ArrayList<>();
"""))
story.append(bullets([
    "调用者依赖接口契约，而不是某个具体实现。",
    "实现类可以替换，调用代码通常不变。",
    "支持多态、依赖注入和 Mock 测试。",
]))
story.extend(slide("modular", 12, "课件截图：面向接口编程是降低耦合的核心手段。"))
story.append(h2("2. 接口隔离原则 ISP"))
story.append(p("客户端不应被迫依赖它不使用的方法。肥接口会迫使实现类提供无意义方法，甚至抛出 UnsupportedOperationException。应按客户端角色拆成更小、更专一的接口。"))
story.extend(slide("modular", 13, "课件截图：将 Worker 拆成 Workable 与 Feedable，使 Robot 不依赖无关方法。"))

story.append(PageBreak())
story.append(h1("五、继承耦合与里氏替换"))
story.append(h2("1. 里氏替换原则 LSP"))
story.append(p("子类型必须能够替换父类型而不改变程序正确性。判断 IS-A 不能只看自然语言或数学集合，更要看行为契约。"))
story.append(table([
    ["契约要素", "LSP 要求"],
    ["前置条件", "子类不能比父类更严格"],
    ["后置条件", "子类不能比父类保证更少"],
    ["不变式", "子类必须维护父类的全部不变式"],
    ["异常/语义", "不能把正常行为改成异常或完全不同的含义"],
], widths=[4.0 * cm, 12.4 * cm]))
story.extend(slide("modular", 16, "课件截图：正方形继承长方形会破坏宽高独立的不变式，是经典 LSP 反例。"))
story.append(h2("2. 组合优于继承"))
story.append(bullets([
    "继承是白盒复用，子类依赖父类实现细节；父类修改可能破坏所有子类。",
    "组合是黑盒复用，只依赖对象接口，运行时还可以动态替换。",
    "只有真正稳定的行为 IS-A 关系才适合继承；行为变化维度多时优先组合。",
]))
story.extend(slide("modular", 19, "课件截图：组合通过接口复用行为，职责和变化边界更清晰。"))

story.append(PageBreak())
story.append(h1("六、信息隐藏与封装"))
story.append(h2("1. 信息隐藏的本质"))
story.append(p("Parnas 的核心思想是：每个模块都应隐藏一个重要设计决策。隐藏的不只是字段，而是实现细节和未来变化。变化被限制在模块内部，其他模块只依赖稳定接口。"))
story.append(table([
    ["秘密", "含义", "示例"],
    ["主要秘密", "模块职责可能怎样改变", "折扣规则、持久化职责是否变化"],
    ["次要秘密", "模块内部如何实现可能改变", "List 改为 Set、MySQL 改为 SQL Server"],
], widths=[3.3 * cm, 6.0 * cm, 7.1 * cm]))
story.extend(slide("modular", 21, "课件截图：信息隐藏就是隔离变化、降低耦合。"))
story.append(h2("2. 封装的五种类型"))
story.append(table([
    ["类型", "隐藏内容", "核心手段"],
    ["A 数据类型", "内部数据表示", "private 字段和受控访问器"],
    ["B 内部结构", "集合、数组的组织方式", "不直接暴露内部容器"],
    ["C 其他对象引用", "内部持有哪些对象", "不返回可修改的内部引用"],
    ["D 类型信息", "具体运行时类型", "面向接口、多态调度"],
    ["E 潜在变更", "可能变化的算法或策略", "策略、工厂、依赖注入"],
], widths=[3.3 * cm, 6.2 * cm, 6.9 * cm]))
story.extend(slide("modular", 24, "课件截图：封装 A-E 覆盖当前实现细节和未来变化。"))

story.append(PageBreak())
story.append(h2("3. 封装潜在变更"))
story.append(code("""
interface SortStrategy {
    void sort(int[] values);
}

class Sorter {
    private final SortStrategy strategy;
    Sorter(SortStrategy strategy) { this.strategy = strategy; }
    void sort(int[] values) { strategy.sort(values); }
}
"""))
story.append(p("Sorter 不知道冒泡排序还是快速排序，只依赖 SortStrategy。算法改变时替换实现对象，稳定流程不变。这同时体现信息隐藏、组合、OCP 和 DIP。"))
story.extend(slide("modular", 29, "课件截图：类型 E 将算法变化隔离到策略实现中。"))

story.append(h1("七、类和方法设计原则"))
story.append(h2("1. 开闭原则 OCP"))
story.append(p("软件实体应对扩展开放、对修改关闭。新增变化类型时优先增加实现类，而不是修改稳定类中的 if/switch。OCP 不是禁止一切修改，而是建立稳定抽象，使常见变化通过扩展完成。"))
story.extend(slide("modular", 33, "课件截图：折扣策略通过接口和多态实现 OCP。"))
story.append(h2("2. 依赖倒置原则 DIP"))
story.append(p("高层模块不依赖低层具体实现，两者都依赖抽象；细节反过来实现高层定义的接口。常见实现手段是接口、构造器注入和工厂。"))
story.extend(slide("modular", 34, "课件截图：业务逻辑依赖 Database 接口，而不是 MySQLDatabase。"))

story.append(PageBreak())
story.append(h2("3. 单一职责原则 SRP"))
story.append(p("一个类应该只有一个变化原因。把薪资计算、数据库保存、报表生成放入 Employee，会受到 HR、IT、财务三类变化影响，应拆为不同职责对象。"))
story.extend(slide("modular", 35, "课件截图：SRP 把不同变化原因拆到独立类中。"))
story.append(h2("4. SOFA 方法级原则"))
story.append(table([
    ["字母", "原则", "判断方法"],
    ["S", "Short", "方法保持短小，过长则提取辅助方法"],
    ["O", "One thing", "方法只做一件事，名称不需要用 and 描述"],
    ["F", "Few arguments", "参数尽量少，避免调用者知道过多细节"],
    ["A", "Abstraction level consistency", "同一方法保持相同抽象层次"],
], widths=[1.7 * cm, 5.0 * cm, 9.7 * cm]))
story.extend(slide("modular", 36, "课件截图：SOFA 从方法粒度约束长度、职责、参数和抽象层次。"))

story.append(h2("5. P1-P14 总表"))
story.append(table([
    ["编号", "原则", "核心判断"],
    ["P1", "全局变量有害", "是否存在穿透模块的隐式共享状态"],
    ["P2", "优先显式表达", "约束是否依赖隐含约定"],
    ["P3", "DRY", "同一知识或决策是否重复编码"],
    ["P4", "面向接口", "调用方是否依赖具体实现"],
    ["P5", "迪米特法则", "是否通过消息链访问间接对象"],
    ["P6", "ISP", "客户端是否被迫依赖无关方法"],
    ["P7", "LSP", "子类能否无损替换父类"],
    ["P8", "组合优于继承", "能否用黑盒组合降低继承耦合"],
    ["P9", "封装变化", "可变部分是否与稳定部分隔离"],
    ["P10", "权限最小化", "成员是否从 private 开始按需开放"],
    ["P11", "OCP", "新增类型是否总要修改旧代码"],
    ["P12", "DIP", "高层是否依赖抽象而非低层细节"],
    ["P13", "SRP", "一个类是否有多个变化原因"],
    ["P14", "SOFA", "方法是否短、小职责、少参数、同抽象层"],
], widths=[1.7 * cm, 4.6 * cm, 10.1 * cm]))

story.append(PageBreak())
story.append(h1("八、往年题例题与答案"))
story.append(h2("例题 1：2020 耦合判断"))
story.append(code("""
int valid_month(Date date) {
    return date.month >= 1 && date.month <= 12;
}

int valid(String value, int type) {
    switch (type) {
        case STRING: ...
        case DATE: ...
    }
}
"""))
story.append(table([
    ["问法", "参考答案"],
    ["validate_request 与 valid_month 是什么耦合？", "印记耦合。valid_month 接收完整 Date，却只使用 month。改为 validMonth(int month)，只传必要数据。"],
    ["validate_request 与 valid 是什么耦合？", "控制耦合。调用者传 type 控制 valid 内部 switch，双方都依赖类型码语义。改为 validString、validDate 等专一方法，或定义 Validator 接口并用多态实现。"],
], widths=[6.0 * cm, 10.4 * cm]))

story.append(h2("例题 2：2022 循环依赖"))
story.append(p("题目：用户包持有优惠券包中的优惠券，优惠券包又查询用户包信息以发放优惠券。"))
story.append(table([
    ["问题", "参考答案"],
    ["违反什么原则？", "形成 UserPackage -> CouponPackage -> UserPackage 的循环依赖，违反无环依赖原则，也使两个包无法独立修改、测试和部署。"],
    ["如何修改？", "把发券用例协调职责放入独立 Application/Service 包；Coupon 只表达优惠券规则，User 只表达用户状态。或在稳定一侧定义接口，通过 DIP 让另一侧实现，打断反向具体依赖。"],
    ["类图方向", "IssueCouponService 依赖 UserRepository 与 CouponPolicy 接口；User 和具体 Coupon 不再双向查询。依赖箭头都指向抽象接口。"],
], widths=[4.0 * cm, 12.4 * cm]))
story.append(note("当前考试权重", "答疑明确包原则不是本次重点，但往年卷出现过，所以应会识别循环依赖。真正高优先级仍是类设计原则和基于代码的判断。"))

story.append(h2("例题 3：发券代码综合分析"))
story.append(table([
    ["现象", "原则分析", "改进"],
    ["type + switch 选择优惠券", "控制耦合；违反 OCP；调用者和方法共享类型码", "定义 CouponPolicy/Issuer 接口，用不同实现封装发券行为"],
    ["方法直接 new 具体 Coupon", "高层依赖具体类，违反 DIP", "通过工厂或依赖注入获得策略"],
    ["新增用户类型必须改 switch", "稳定类对修改开放，变化未封装", "新增实现类并注册，不修改核心流程"],
    ["多个分支重复 user.addCoupon", "重复表达相同操作，违反 DRY", "先得到 Coupon，再统一调用一次 addCoupon"],
], widths=[4.3 * cm, 6.1 * cm, 6.0 * cm]))

story.append(PageBreak())
story.append(h1("九、答题模板与速记"))
story.append(h2("1. 原则分析题模板"))
story.append(numbered([
    "指出代码或类图中的具体依赖、分支、字段暴露或职责混合。",
    "写出违反/体现的原则名称。",
    "解释变化会如何传播，或为何增加耦合、破坏替换。",
    "给出重构：拆职责、提接口、依赖注入、多态、委托、缩小参数。",
    "说明重构后新增需求需要增加什么、哪些稳定代码不必修改。",
]))
story.append(h2("2. 高频速记"))
story.append(table([
    ["看到什么", "优先想到"],
    ["flag/type + switch", "控制耦合、OCP、多态/策略"],
    ["传整个对象只用一项", "印记耦合、最小接口"],
    ["a.getB().getC()", "消息链、迪米特法则、委托"],
    ["public 字段/集合", "封装缺失、权限最小化、受控方法"],
    ["子类抛不支持异常", "LSP/ISP 违反，拆接口"],
    ["业务类直接 new 数据库实现", "DIP 违反，接口 + 注入"],
    ["一个类又计算又保存又报表", "SRP 违反，按变化原因拆分"],
    ["新增类型总改 if/switch", "OCP 违反，封装变化并用多态"],
], widths=[6.0 * cm, 10.4 * cm]))
story.append(note("最后检查", "答题不要只报原则名称。至少写出“代码证据 - 原则 - 影响 - 重构 - 扩展效果”五个环节。"))

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.8 * cm, leftMargin=1.8 * cm, topMargin=1.55 * cm, bottomMargin=1.55 * cm)
footer = header_footer("模块化与信息隐藏篇")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
