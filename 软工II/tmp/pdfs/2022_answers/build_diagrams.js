const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const OUT = path.resolve('tmp/pdfs/2022_answers/diagrams');
fs.mkdirSync(OUT, {recursive: true});

const defs = `<defs>
  <marker id="solid" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="#24324a"/></marker>
  <marker id="open" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto"><path d="M1,1 L11,6 L1,11" fill="none" stroke="#24324a" stroke-width="2"/></marker>
  <marker id="tri" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto"><path d="M1,1 L15,8 L1,15 Z" fill="#fff" stroke="#5b3f91" stroke-width="2"/></marker>
  <style>
   text{font-family:"PingFang SC","Microsoft YaHei",Arial,sans-serif;fill:#172033}.title{font-size:38px;font-weight:800}.h{font-size:25px;font-weight:700}.t{font-size:21px}.s{font-size:18px}.tiny{font-size:16px}
   .panel{fill:#fff;stroke:#cbd5e1;stroke-width:2;rx:18}.node{fill:#fff;stroke:#2f4262;stroke-width:2.5;rx:8}.head{fill:#e8eef9;stroke:#2f4262;stroke-width:2.5}.note{fill:#fff8e8;stroke:#d99622;stroke-width:2;rx:12}
   .line{fill:none;stroke:#24324a;stroke-width:2.5}.call{fill:none;stroke:#24324a;stroke-width:2.5;marker-end:url(#solid)}.ret{fill:none;stroke:#465773;stroke-width:2.2;stroke-dasharray:9 7;marker-end:url(#open)}.dep{fill:none;stroke:#314b70;stroke-width:2.3;stroke-dasharray:9 7;marker-end:url(#open)}.real{fill:none;stroke:#5b3f91;stroke-width:2.3;stroke-dasharray:9 7;marker-end:url(#tri)}.inherit{fill:none;stroke:#5b3f91;stroke-width:2.3;marker-end:url(#tri)}
  </style>
</defs>`;

function canvas(title, subtitle, body, w=1800, h=1100) { return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${defs}<rect width="${w}" height="${h}" fill="#f4f7fc"/><rect width="${w}" height="16" fill="#5b3f91"/><text class="title" x="65" y="70">${title}</text><text class="s" x="65" y="106" fill="#52627a">${subtitle}</text>${body}</svg>`; }
function actor(x,y,label){return `<g transform="translate(${x},${y})"><circle cx="0" cy="-30" r="19" fill="none" stroke="#263750" stroke-width="3"/><path d="M0,-11 L0,53 M-34,10 L34,10 M0,53 L-28,92 M0,53 L28,92" fill="none" stroke="#263750" stroke-width="3"/><text class="h" x="0" y="130" text-anchor="middle">${label}</text></g>`;}
function cls(x,y,w,h,title,rows=[],st='class'){return `<g><rect class="node" x="${x}" y="${y}" width="${w}" height="${h}"/><rect class="head" x="${x}" y="${y}" width="${w}" height="55"/><text class="tiny" x="${x+w/2}" y="${y+20}" text-anchor="middle">${st==='interface'?'«interface»':''}</text><text class="h" x="${x+w/2}" y="${y+45}" text-anchor="middle">${title}</text>${rows.map((r,i)=>`<text class="s" x="${x+17}" y="${y+90+i*31}">${r}</text>`).join('')}</g>`;}
function pkg(x,y,w,h,title,fill='#fff'){let tab=Math.min(w*.48,300); return `<g><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="#2f4262" stroke-width="2.5" rx="6"/><rect x="${x}" y="${y-24}" width="${tab}" height="46" fill="#e8eef9" stroke="#2f4262" stroke-width="2.5"/><text class="h" x="${x+tab/2}" y="${y+9}" text-anchor="middle">${title}</text></g>`;}
function uc(x,y,rx,t){return `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="45" fill="#fff" stroke="#334b70" stroke-width="2.5"/><text class="t" x="${x}" y="${y+7}" text-anchor="middle">${t}</text>`;}

const diagrams = {};

diagrams['01-usecase'] = canvas('第 2 题答案：校园卡自助系统用例图','参与者在系统边界外；关联为无箭头实线；外部支付系统作为次要参与者',`
 <rect class="panel" x="285" y="145" width="1170" height="860"/><text class="h" x="870" y="190" text-anchor="middle">校园卡自助系统</text>
 ${actor(135,300,'师生')}${actor(1645,330,'银行/支付平台')}${actor(1645,760,'校园卡中心')}
 ${uc(560,280,165,'查询校园卡余额')}${uc(990,280,165,'校园卡充值')}${uc(560,430,165,'查询交易明细')}${uc(990,430,165,'查询充值记录')}
 ${uc(560,580,165,'绑定/解绑银行卡')}${uc(990,580,165,'校园卡挂失')}${uc(560,730,165,'解除挂失')}${uc(990,730,165,'修改支付密码')}${uc(775,880,185,'查看/下载校园码')}
 <path class="line" d="M175,310 L395,280 M175,330 L395,430 M175,350 L395,580 M175,370 L395,730 M175,390 L590,880 M175,410 L825,280 M175,430 L825,430 M175,450 L825,580 M175,470 L825,730"/>
 <path class="line" d="M1155,280 L1605,330 M1155,580 L1605,350 M1155,280 L1605,760 M1155,430 L1605,780 M1155,730 L1605,800"/>
 <rect class="note" x="315" y="940" width="1110" height="48"/><text class="s" x="870" y="971" text-anchor="middle">可按题干取舍：核心至少包括充值、余额、银行卡绑定、明细查询；截图中的挂失、密码、校园码可作为补充。</text>`);

diagrams['02-concept'] = canvas('第 3 题答案：校园卡自助系统概念类图','只画领域概念、重要属性、业务关系和多重性，不写方法',`
 ${cls(80,180,265,175,'用户',['用户编号','姓名','用户类型'])}${cls(80,500,265,130,'学生',['学号'])}${cls(80,730,265,130,'教师',['工号'])}
 ${cls(465,180,300,205,'校园卡',['卡号','余额','卡状态','支付密码'])}${cls(880,155,315,215,'交易明细',['明细编号','交易类型','金额','发生时间'])}
 ${cls(880,500,315,185,'充值记录',['充值编号','充值金额','充值时间','充值状态'])}${cls(1380,180,300,180,'银行卡',['银行卡号','银行名称','绑定状态'])}
 <path class="inherit" d="M212,500 L212,355"/><path class="inherit" d="M212,730 L212,355"/>
 <line class="line" x1="345" y1="265" x2="465" y2="265"/><polygon points="465,265 447,253 429,265 447,277" fill="#24324a"/><text class="s" x="355" y="245">1</text><text class="s" x="438" y="245">0..1</text><text class="s" x="405" y="300" text-anchor="middle">拥有</text>
 <line class="line" x1="765" y1="260" x2="880" y2="260"/><polygon points="765,260 783,248 801,260 783,272" fill="#24324a"/><text class="s" x="775" y="240">1</text><text class="s" x="835" y="240">0..*</text><text class="s" x="820" y="295" text-anchor="middle">产生</text>
 <path class="inherit" d="M1037,500 L1037,370"/><text class="s" x="1085" y="445">是其中一种</text>
 <line class="line" x1="345" y1="300" x2="1380" y2="300"/><polygon points="345,300 363,288 381,300 363,312" fill="#fff" stroke="#24324a" stroke-width="2"/><text class="s" x="365" y="325">1</text><text class="s" x="1335" y="325">0..*</text><text class="s" x="860" y="325" text-anchor="middle">绑定（聚合）</text>
 <line class="line" x1="1195" y1="580" x2="1530" y2="360"/><text class="s" x="1325" y="460">支付来源 0..1</text>
 <path class="dep" d="M880,610 C750,650 680,590 680,385"/><text class="s" x="690" y="580">充值后更新余额</text>
 <rect class="note" x="415" y="900" width="1010" height="120"/><text class="s" x="445" y="940">关系：学生、教师继承用户；用户与校园卡为强拥有关系；校园卡组合交易明细；充值记录继承交易明细；</text><text class="s" x="445" y="975">用户聚合银行卡；充值记录可关联付款银行卡，并依赖校园卡完成余额更新。</text>`);

diagrams['03-physical-package'] = canvas('第 4 题答案：校园卡自助系统物理包图','客户端与服务器端具有清晰物理边界；展示层不能直接访问 DAO',`
 <rect class="node" x="60" y="145" width="640" height="850"/><text class="h" x="90" y="185">«device» Client / Browser</text>
 ${pkg(110,250,540,155,'web')}<text class="t" x="380" y="325" text-anchor="middle">HTML　CSS　JavaScript</text>
 ${pkg(110,500,540,300,'presentation')}<text class="s" x="380" y="575" text-anchor="middle">user　card　recharge</text><text class="s" x="380" y="620" text-anchor="middle">bankcard　record</text><text class="s" x="380" y="680" text-anchor="middle">VO / Controller</text>
 <path class="dep" d="M650,380 L940,380"/><text class="t" x="795" y="350" text-anchor="middle">HTTP + REST API</text>
 <rect class="node" x="940" y="145" width="800" height="850"/><text class="h" x="970" y="185">«node» Server</text>
 ${pkg(990,250,700,135,'service.interface')}<text class="s" x="1340" y="330" text-anchor="middle">RechargeService　CardService　UserService</text>
 ${pkg(990,470,700,135,'service.impl')}<text class="s" x="1340" y="550" text-anchor="middle">RechargeServiceImpl　CardServiceImpl ...</text>
 ${pkg(990,690,700,120,'dao.interface')}<text class="s" x="1340" y="765" text-anchor="middle">RechargeRecordDAO　CampusCardDAO ...</text>
 ${pkg(990,895,700,70,'dao.impl / PO')}<text class="s" x="1340" y="950" text-anchor="middle">DAO 实现与持久化对象</text>
 <path class="dep" d="M1340,385 L1340,470"/><path class="real" d="M1470,470 L1470,385"/><path class="dep" d="M1340,605 L1340,690"/><path class="real" d="M1470,895 L1470,810"/>
 <text class="tiny" x="1020" y="625">五个功能域贯穿 service / dao：user、card、recharge、bankcard、record</text>`);

diagrams['04-detail-class'] = canvas('第 5 题答案：优惠券与第三方支付详细设计类图','Coupon 与 ThirdPayment 均使用多态；新增折扣或支付方式不修改充值主流程',`
 ${cls(70,180,260,185,'User',['- userId: String','+ getCard(): Card','+ getCoupon(id): Coupon'])}
 ${cls(70,560,260,155,'Card',['- cardId: String','- balance: Money','+ increaseBalance(amount)'])}
 ${cls(440,160,330,185,'Coupon',['- couponId: String','- used: boolean','+ calculatePayable(amount)','+ markUsed()'],'interface')}
 ${cls(410,500,270,150,'FixedAmountCoupon',['- discount: Money','+ calculatePayable(amount)'])}${cls(735,500,285,150,'PercentageCoupon',['- rate: Decimal','+ calculatePayable(amount)'])}
 ${cls(1080,160,320,150,'ThirdPayment',['+ pay(amount): PaymentResult'],'interface')}${cls(1040,500,265,135,'AlipayPayment',['+ pay(amount)'])}${cls(1380,500,265,135,'WechatPayment',['+ pay(amount)'])}
 ${cls(720,805,390,205,'PaymentRecord',['- recordId: String','- originalAmount: Money','- paidAmount: Money','- status: PaymentStatus'])}
 <line class="line" x1="200" y1="365" x2="200" y2="560"/><text class="s" x="220" y="470">拥有 1</text>
 <line class="line" x1="330" y1="245" x2="440" y2="245"/><text class="s" x="350" y="225">持有 0..*</text>
 <path class="real" d="M545,500 L560,345"/><path class="real" d="M870,500 L650,345"/>
 <path class="real" d="M1170,500 L1210,310"/><path class="real" d="M1510,500 L1290,310"/>
 <line class="line" x1="330" y1="635" x2="720" y2="880"/><text class="s" x="460" y="740">充值后更新</text>
 <line class="line" x1="605" y1="345" x2="840" y2="805"/><text class="s" x="650" y="700">使用 0..1</text>
 <line class="line" x1="1240" y1="310" x2="1010" y2="805"/><text class="s" x="1080" y="700">生成结果</text>`);

diagrams['05-cycle-package'] = canvas('第 6 题答案：消除用户包与优惠券包的循环依赖','把发券用例编排移入 application 包，并抽取稳定的用户接口',`
 ${pkg(90,200,400,240,'user')}<text class="t" x="290" y="300" text-anchor="middle">User</text><text class="s" x="290" y="350" text-anchor="middle">实现 CouponRecipient</text>
 ${pkg(700,200,400,240,'coupon')}<text class="t" x="900" y="300" text-anchor="middle">Coupon</text><text class="s" x="900" y="350" text-anchor="middle">Fixed / Percentage</text>
 ${pkg(1310,200,400,240,'user.api')}<text class="t" x="1510" y="300" text-anchor="middle">CouponRecipient</text><text class="s" x="1510" y="350" text-anchor="middle">getType / addCoupon</text>
 ${pkg(485,670,830,250,'coupon.application')}<text class="t" x="900" y="770" text-anchor="middle">CouponIssuanceService</text><text class="s" x="900" y="820" text-anchor="middle">只负责编排“查询资格 - 创建优惠券 - 发放”</text>
 <path class="dep" d="M490,310 L700,310"/><text class="s" x="595" y="285" text-anchor="middle">持有 Coupon</text>
 <path class="real" d="M490,360 L1310,360"/><text class="s" x="900" y="405" text-anchor="middle">User 实现稳定接口</text>
 <path class="dep" d="M760,670 L900,440"/><path class="dep" d="M1040,670 L1510,440"/>
 <rect class="note" x="380" y="980" width="1040" height="70"/><text class="t" x="900" y="1025" text-anchor="middle">依赖图无闭环：coupon 不再反向查询 user；新增发券规则只影响 application / policy。</text>`);

diagrams['06-cycle-class'] = canvas('第 6 题答案：消除循环后的类协作','应用服务依赖抽象接口，User 通过实现接口接收 Coupon',`
 ${cls(100,200,330,190,'CouponRecipient',['+ getType(): UserType','+ addCoupon(coupon)'],'interface')}
 ${cls(100,610,330,190,'User',['- type: UserType','- coupons: List&lt;Coupon&gt;','+ addCoupon(coupon)'])}
 ${cls(610,180,350,180,'CouponIssuanceService',['- factory: CouponFactory','+ issueCoupon(recipients)'])}
 ${cls(610,610,350,160,'CouponFactory',['+ createFor(type): Coupon'])}
 ${cls(1190,180,330,160,'Coupon',['+ calculateDiscount(amount)'],'interface')}
 ${cls(1080,610,280,140,'FiveYuanCoupon',['+ calculateDiscount(amount)'])}${cls(1435,610,280,140,'TenYuanCoupon',['+ calculateDiscount(amount)'])}
 <path class="real" d="M265,610 L265,390"/><path class="dep" d="M610,260 L430,260"/><path class="dep" d="M785,360 L785,610"/>
 <path class="dep" d="M960,690 L1190,270"/><path class="real" d="M1220,610 L1290,340"/><path class="real" d="M1575,610 L1420,340"/>
 <path class="line" d="M430,720 L520,850 L1030,850 L1030,270 L1190,270"/><text class="s" x="690" y="835">User 持有 Coupon 0..*</text>
 <rect class="note" x="510" y="900" width="780" height="95"/><text class="s" x="900" y="940" text-anchor="middle">原 issueCoupon(type) → addCoupon 的控制耦合由多态工厂消除；</text><text class="s" x="900" y="972" text-anchor="middle">创建 Coupon 后只调用一次 recipient.addCoupon(coupon)。</text>`);

diagrams['07-isp'] = canvas('第 7 题（1）答案：按接口隔离原则拆分支付接口','每个交易类只依赖自己真正使用的付款能力',`
 ${cls(650,140,500,125,'Transaction',['+ execute()'],'interface')}
 ${cls(120,420,360,135,'ElectricTransaction',['+ execute()'])}${cls(720,420,360,135,'WaterTransaction',['+ execute()'])}${cls(1320,420,360,135,'DinnerTransaction',['+ execute()'])}
 ${cls(120,780,360,130,'ElectricPayment',['+ electricPayment()'],'interface')}${cls(720,780,360,130,'WaterPayment',['+ waterPayment()'],'interface')}${cls(1320,780,360,130,'DinnerPayment',['+ dinnerPayment()'],'interface')}
 <path class="real" d="M300,420 L730,265"/><path class="real" d="M900,420 L900,265"/><path class="real" d="M1500,420 L1070,265"/>
 <path class="real" d="M300,555 L300,780"/><path class="real" d="M900,555 L900,780"/><path class="real" d="M1500,555 L1500,780"/>
 <rect class="note" x="390" y="970" width="1020" height="70"/><text class="t" x="900" y="1015" text-anchor="middle">原 Payment 把三种无关操作放在同一接口，迫使实现类依赖不用的方法，违反 ISP，并削弱单一职责。</text>`);

diagrams['08-strategy'] = canvas('第 7 题（2）答案：第三方支付策略模式','Context 持有 Strategy，微信与支付宝可在运行时替换',`
 ${cls(120,320,410,220,'RechargeService',['- payment: PaymentStrategy','+ setPayment(strategy)','+ recharge(amount)'])}
 ${cls(710,180,420,160,'PaymentStrategy',['+ pay(amount): PaymentResult'],'interface')}
 ${cls(600,630,360,155,'AlipayPayment',['+ pay(amount): PaymentResult'])}${cls(1120,630,360,155,'WechatPayment',['+ pay(amount): PaymentResult'])}
 ${cls(1290,180,350,170,'PaymentResult',['- success: boolean','- transactionNo: String'])}
 <line class="line" x1="530" y1="405" x2="710" y2="260"/><polygon points="530,405 548,393 566,405 548,417" fill="#fff" stroke="#24324a" stroke-width="2"/><text class="s" x="600" y="335">组合策略 1</text>
 <path class="real" d="M780,630 L850,340"/><path class="real" d="M1300,630 L1010,340"/><path class="dep" d="M1130,260 L1290,260"/>
 <rect class="note" x="240" y="900" width="1320" height="100"/><text class="s" x="900" y="940" text-anchor="middle">新增支付方式：增加一个 PaymentStrategy 实现并注册即可，RechargeService 不修改。</text><text class="s" x="900" y="975" text-anchor="middle">体现开闭原则、依赖倒置、单一职责、里氏替换和组合优于继承。</text>`);

diagrams['09-cfg'] = canvas('第 10 题答案：短路条件控制流骨架','A、B、C、D 为外层四个原子条件，E 为 loginUser 条件',`
 <circle cx="130" cy="520" r="28" fill="#24324a"/><text class="t" x="130" y="580" text-anchor="middle">开始</text>
 ${['A','B','C','D','E'].map((v,i)=>{const x=330+i*270;return `<polygon points="${x},430 ${x+95},520 ${x},610 ${x-95},520" fill="#fff" stroke="#2f4262" stroke-width="2.5"/><text class="h" x="${x}" y="528" text-anchor="middle">${v}?</text>`;}).join('')}
 <rect class="node" x="1510" y="340" width="200" height="90"/><text class="h" x="1610" y="395" text-anchor="middle">输出 yes</text><rect class="node" x="1510" y="760" width="200" height="90"/><text class="h" x="1610" y="815" text-anchor="middle">输出 no</text>
 <path class="call" d="M158,520 L235,520"/>${[330,600,870,1140].map(x=>`<path class="call" d="M${x+95},520 L${x+175},520"/><text class="s" x="${x+130}" y="495">T</text>`).join('')}
 <path class="call" d="M1410,480 L1510,395"/><text class="s" x="1445" y="425">T</text><path class="call" d="M1410,560 L1510,805"/><text class="s" x="1450" y="620">F</text>
 ${[330,600,870,1140].map(x=>`<path class="call" d="M${x},610 L${x},805 L1510,805"/><text class="s" x="${x+12}" y="650">F</text>`).join('')}
 <rect class="note" x="300" y="930" width="1200" height="85"/><text class="t" x="900" y="968" text-anchor="middle">短路展开后共有 5 个判定节点，因此 V(G) = 5 + 1 = 6。</text><text class="s" x="900" y="1000" text-anchor="middle">要让后续条件取到假值，前面的 A、B、C 必须先为真。</text>`);

(async()=>{for(const [name,svg] of Object.entries(diagrams)){fs.writeFileSync(path.join(OUT,`${name}.svg`),svg);await sharp(Buffer.from(svg)).png().toFile(path.join(OUT,`${name}.png`));}})();
