const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const OUT = path.resolve('tmp/pdfs/drawing_templates/pages');
fs.mkdirSync(OUT, { recursive: true });

const defs = `
<defs>
  <marker id="solid" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="#24324a"/></marker>
  <marker id="open" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto"><path d="M1,1 L11,6 L1,11" fill="none" stroke="#24324a" stroke-width="1.8"/></marker>
  <marker id="triangle" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto"><path d="M1,1 L15,8 L1,15 Z" fill="#fff" stroke="#6f42a0" stroke-width="1.8"/></marker>
  <style>
    text{font-family:"PingFang SC","Microsoft YaHei",sans-serif;fill:#172033}
    .title{font-size:42px;font-weight:800}.sub{font-size:23px;fill:#53627a}.h{font-size:27px;font-weight:700}.t{font-size:22px}.s{font-size:19px}.tiny{font-size:17px}
    .panel{fill:#fff;stroke:#d3dbea;stroke-width:2;rx:18}.node{fill:#fff;stroke:#2f4262;stroke-width:2.5;rx:8}.accent{fill:#e6eefb;stroke:#2f4262;stroke-width:2.5}
    .call{fill:none;stroke:#24324a;stroke-width:2.5;marker-end:url(#solid)}.ret{fill:none;stroke:#465773;stroke-width:2.2;stroke-dasharray:9 7;marker-end:url(#open)}
    .dep{fill:none;stroke:#314b70;stroke-width:2.2;stroke-dasharray:9 7;marker-end:url(#open)}.realize,.inherit{fill:none;stroke:#6f42a0;stroke-width:2.3;stroke-dasharray:9 7;marker-end:url(#triangle)}
    .line{fill:none;stroke:#3f506a;stroke-width:2.2}.dash{fill:none;stroke:#65728a;stroke-width:2;stroke-dasharray:9 8}
    .note{fill:#fff9e9;stroke:#d79b31;stroke-width:2;rx:12}.good{fill:#eef8f1;stroke:#4b8b5b;stroke-width:2;rx:12}
  </style>
</defs>`;

function page(title, subtitle, body, source, n) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1273" viewBox="0 0 1800 1273">
  ${defs}<rect width="1800" height="1273" fill="#f4f7fc"/>
  <rect x="0" y="0" width="1800" height="18" fill="#5b3f91"/>
  <text class="title" x="75" y="78">${title}</text><text class="sub" x="75" y="115">${subtitle}</text>
  ${body}
  <line x1="70" y1="1218" x2="1730" y2="1218" stroke="#ccd5e4" stroke-width="2"/>
  <text class="tiny" x="75" y="1250">课件依据：${source}</text><text class="tiny" x="1725" y="1250" text-anchor="end">${n} / 9</text>
  </svg>`;
}

function actor(x,y,label){return `<g transform="translate(${x},${y})"><circle cx="0" cy="-35" r="20" fill="none" stroke="#263750" stroke-width="3"/><path d="M0,-15 L0,55 M-38,10 L38,10 M0,55 L-30,98 M0,55 L30,98" fill="none" stroke="#263750" stroke-width="3" stroke-linecap="round"/><text class="h" x="0" y="135" text-anchor="middle">${label}</text></g>`;}
function cls(x,y,w,h,title,attrs=[]){return `<g><rect class="node" x="${x}" y="${y}" width="${w}" height="${h}"/><rect class="accent" x="${x}" y="${y}" width="${w}" height="48"/><text class="h" x="${x+w/2}" y="${y+33}" text-anchor="middle">${title}</text>${attrs.map((a,i)=>`<text class="t" x="${x+20}" y="${y+82+i*34}">${a}</text>`).join('')}</g>`;}
function usecase(x,y,rx,txt){return `<ellipse cx="${x}" cy="${y}" rx="${rx}" ry="48" fill="#fff" stroke="#334b70" stroke-width="2.5"/><text class="t" x="${x}" y="${y+8}" text-anchor="middle">${txt}</text>`;}
function pkg(x,y,w,h,title){return `<g><rect class="node" x="${x}" y="${y}" width="${w}" height="${h}"/><rect class="accent" x="${x}" y="${y-22}" width="${Math.min(w*.48,310)}" height="44"/><text class="h" x="${x+Math.min(w*.48,310)/2}" y="${y+9}" text-anchor="middle">${title}</text></g>`;}

const pages = [];

pages.push(page('软件工程 II 画图模板册','用课件一致的符号骨架，快速迁移到任意考试情景',`
  <rect class="panel" x="95" y="170" width="1610" height="910"/>
  <text x="900" y="300" text-anchor="middle" font-size="58" font-weight="800" fill="#4c347f">八类高频图，一册带走</text>
  <g class="t">
    <rect class="accent" x="210" y="390" width="360" height="105" rx="16"/><text x="390" y="455" text-anchor="middle">用例图</text>
    <rect class="accent" x="720" y="390" width="360" height="105" rx="16"/><text x="900" y="455" text-anchor="middle">系统顺序图</text>
    <rect class="accent" x="1230" y="390" width="360" height="105" rx="16"/><text x="1410" y="455" text-anchor="middle">概念类图</text>
    <rect class="accent" x="210" y="560" width="360" height="105" rx="16"/><text x="390" y="625" text-anchor="middle">详细顺序图</text>
    <rect class="accent" x="720" y="560" width="360" height="105" rx="16"/><text x="900" y="625" text-anchor="middle">物理包图</text>
    <rect class="accent" x="1230" y="560" width="360" height="105" rx="16"/><text x="1410" y="625" text-anchor="middle">4+1 视图</text>
    <rect class="accent" x="465" y="730" width="360" height="105" rx="16"/><text x="645" y="795" text-anchor="middle">状态图</text>
    <rect class="accent" x="975" y="730" width="360" height="105" rx="16"/><text x="1155" y="795" text-anchor="middle">程序流程图</text>
  </g>
  <rect class="good" x="330" y="910" width="1140" height="105"/><text class="t" x="900" y="955" text-anchor="middle">分析阶段：业务语言优先　　设计阶段：名称与代码一致</text><text class="s" x="900" y="990" text-anchor="middle">每页均为可直接临摹的“骨架图 + 得分检查表”</text>
`,'课程各相关章节综合',1));

pages.push(page('1. 用例图模板','回答“谁为了什么业务目标使用系统”',`
  <rect class="panel" x="65" y="150" width="1180" height="1010"/>
  <rect x="325" y="215" width="830" height="830" fill="#fbfcff" stroke="#263750" stroke-width="3" rx="12"/>
  <text class="h" x="740" y="260" text-anchor="middle">[系统名称]</text>
  ${actor(180,360,'[主要参与者]')}${actor(180,780,'[次要参与者]')}${actor(1325,560,'[外部系统]')}
  ${usecase(550,360,165,'[核心业务用例]')}${usecase(900,360,170,'[必做子用例]')}
  ${usecase(550,590,165,'[基础用例]')}${usecase(900,590,170,'[条件扩展用例]')}
  ${usecase(730,820,190,'[另一完整业务目标]')}
  <line class="line" x1="218" y1="370" x2="385" y2="360"/><line class="line" x1="218" y1="390" x2="565" y2="820"/>
  <line class="line" x1="218" y1="790" x2="565" y2="820"/><line class="line" x1="1155" y1="590" x2="1287" y2="570"/>
  <path class="dep" d="M715,360 L730,360"/><text class="s" x="720" y="335" text-anchor="middle">«include»</text>
  <path class="dep" d="M730,590 L715,590"/><text class="s" x="720" y="565" text-anchor="middle">«extend»</text>
  <rect class="note" x="1290" y="180" width="440" height="850"/>
  <text class="h" x="1510" y="235" text-anchor="middle">作图检查表</text>
  <text class="t" x="1325" y="300">□ 参与者始终在边界外</text><text class="t" x="1325" y="350">□ 用例始终在边界内</text>
  <text class="t" x="1325" y="400">□ 关联为无箭头实线</text><text class="t" x="1325" y="450">□ include：基础 → 被包含</text>
  <text class="t" x="1325" y="500">□ extend：扩展 → 基础</text><text class="t" x="1325" y="550">□ 用例是完整业务目标</text>
  <text class="t" x="1325" y="600">□ 不画数据库等内部组件</text><text class="t" x="1325" y="650">□ 不把单一步骤当用例</text>
  <line x1="1325" y1="700" x2="1695" y2="700" stroke="#d9a23a"/>
  <text class="h" x="1510" y="755" text-anchor="middle">语言</text><text class="t" x="1325" y="810">参与者、用例：中文</text><text class="t" x="1325" y="860">UML 关键字：英文</text>
`,'02-03-用例建模与用户故事，第 12-31 页',2));

pages.push(page('2. 系统顺序图模板','把待开发系统看成一个黑箱，只展开外部交互',`
  <rect class="panel" x="65" y="150" width="1260" height="1010"/>
  <rect class="node" x="120" y="195" width="230" height="70"/><rect class="node" x="555" y="195" width="230" height="70"/><rect class="node" x="990" y="195" width="250" height="70"/>
  <text class="h" x="235" y="240" text-anchor="middle">[参与者]</text><text class="h" x="670" y="240" text-anchor="middle">:系统</text><text class="h" x="1115" y="240" text-anchor="middle">[外部系统]</text>
  <line class="dash" x1="235" y1="265" x2="235" y2="1085"/><line class="dash" x1="670" y1="265" x2="670" y2="1085"/><line class="dash" x1="1115" y1="265" x2="1115" y2="1085"/>
  <line class="call" x1="235" y1="335" x2="670" y2="335"/><text class="s" x="452" y="318" text-anchor="middle">1. [提交业务请求（参数）]</text>
  <line class="ret" x1="670" y1="410" x2="235" y2="410"/><text class="s" x="452" y="392" text-anchor="middle">2. [返回业务结果]</text>
  <rect x="90" y="470" width="1170" height="520" fill="#fff" stroke="#263750" stroke-width="2.3"/>
  <path d="M90,470 H185 L210,495 L185,520 H90 Z" fill="#e6eefb" stroke="#263750" stroke-width="2.3"/><text class="h" x="140" y="505">alt</text>
  <text class="t" x="120" y="565">[条件一：成功]</text><line class="call" x1="235" y1="625" x2="670" y2="625"/><text class="s" x="452" y="607" text-anchor="middle">3. [系统操作]</text>
  <line class="call" x1="670" y1="690" x2="1115" y2="690"/><text class="s" x="892" y="672" text-anchor="middle">4. [调用外部服务]</text>
  <line x1="90" y1="745" x2="1260" y2="745" stroke="#77859b" stroke-dasharray="8 7" stroke-width="2"/>
  <text class="t" x="120" y="795">[条件二：失败]</text><line class="ret" x1="670" y1="860" x2="235" y2="860"/><text class="s" x="452" y="842" text-anchor="middle">5. [返回失败原因]</text>
  <rect class="note" x="1360" y="180" width="370" height="860"/>
  <text class="h" x="1545" y="235" text-anchor="middle">作图检查表</text>
  <text class="t" x="1390" y="300">□ 系统写成 :系统</text><text class="t" x="1390" y="350">□ 时间自上而下</text>
  <text class="t" x="1390" y="400">□ 请求：实线实心箭头</text><text class="t" x="1390" y="450">□ 返回：虚线箭头</text>
  <text class="t" x="1390" y="500">□ 异常用 alt / opt</text><text class="t" x="1390" y="550">□ 一张图覆盖多场景</text>
  <text class="t" x="1390" y="600">□ 不出现 Controller</text><text class="t" x="1390" y="650">□ 不出现 Service / DAO</text>
  <text class="t" x="1390" y="700">□ 不出现数据库</text><line x1="1390" y1="750" x2="1700" y2="750" stroke="#d9a23a"/>
  <text class="h" x="1545" y="805" text-anchor="middle">语言</text><text class="t" x="1390" y="860">全部中文可以</text><text class="s" x="1390" y="905">但命名必须清楚、统一</text>
`,'02-04-需求分析与AI辅助建模，第 30-32 页',3));

pages.push(page('3. 概念类图模板','描述问题域中的概念、重要属性和业务关系',`
  <rect class="panel" x="65" y="150" width="1260" height="1010"/>
  ${cls(120,220,300,180,'[角色概念]',['[业务标识]','[关键状态]'])}
  ${cls(540,220,330,215,'[核心事件/交易]',['[编号]','[发生时间]','[业务状态]'])}
  ${cls(975,220,280,180,'[实体概念]',['[编号]','[描述]'])}
  ${cls(540,620,330,180,'[明细/记录]',['[数量]','[结果]'])}
  ${cls(975,620,280,180,'[抽象概念]',['[类型]','[规则]'])}
  <line class="line" x1="420" y1="310" x2="540" y2="310"/><text class="s" x="480" y="292" text-anchor="middle">[发起]</text><text class="s" x="432" y="337">1</text><text class="s" x="500" y="337">0..*</text>
  <line class="line" x1="870" y1="310" x2="975" y2="310"/><text class="s" x="922" y="292" text-anchor="middle">[关联]</text><text class="s" x="885" y="337">*</text><text class="s" x="946" y="337">1</text>
  <line class="line" x1="705" y1="435" x2="705" y2="620"/><polygon points="705,435 718,450 705,465 692,450" fill="#263750"/><text class="s" x="760" y="535">组合</text><text class="s" x="720" y="485">1</text><text class="s" x="720" y="607">1..*</text>
  <path class="inherit" d="M1115,620 L1115,400"/><text class="s" x="1165" y="525">泛化</text>
  <line class="line" x1="420" y1="690" x2="540" y2="690"/><polygon points="420,690 435,680 450,690 435,700" fill="#fff" stroke="#263750" stroke-width="2"/><text class="s" x="480" y="672" text-anchor="middle">聚合</text>
  <rect class="good" x="130" y="885" width="1110" height="185"/><text class="h" x="685" y="930" text-anchor="middle">关系符号速记</text><text class="t" x="175" y="980">普通关联：实线</text><text class="t" x="480" y="980">聚合：空心菱形</text><text class="t" x="800" y="980">组合：实心菱形</text><text class="t" x="175" y="1025">继承：空心三角</text><text class="t" x="480" y="1025">多重性：1、0..1、*、1..*</text>
  <rect class="note" x="1360" y="180" width="370" height="860"/>
  <text class="h" x="1545" y="235" text-anchor="middle">作图检查表</text>
  <text class="t" x="1390" y="300">□ 从题干名词识别概念</text><text class="t" x="1390" y="350">□ 只有类、属性、关系</text>
  <text class="t" x="1390" y="400">□ 绝对不写方法</text><text class="t" x="1390" y="450">□ 不混入技术实现类</text>
  <text class="t" x="1390" y="500">□ 每条关联有语义</text><text class="t" x="1390" y="550">□ 两端标注多重性</text>
  <text class="t" x="1390" y="600">□ 生命周期绑定才组合</text><text class="t" x="1390" y="650">□ 属性支撑业务场景</text>
  <line x1="1390" y1="710" x2="1700" y2="710" stroke="#d9a23a"/><text class="h" x="1545" y="765" text-anchor="middle">语言</text><text class="t" x="1390" y="820">领域概念、属性：中文</text>
`,'02-04-需求分析与AI辅助建模，第 11-25 页',4));

pages.push(page('4. 详细顺序图模板','展开系统内部对象如何通过消息协作完成职责',`
  <rect class="panel" x="55" y="150" width="1390" height="1010"/>
  ${['[参与者]','«boundary»\n[界面]','«control»\n[Controller]','[Service]','[DAO]','[实体/PO]'].map((v,i)=>{const x=95+i*225;const p=v.split('\n');return `<rect class="node" x="${x}" y="205" width="175" height="80"/><text class="s" x="${x+87}" y="238" text-anchor="middle">${p[0]}</text><text class="s" x="${x+87}" y="266" text-anchor="middle">${p[1]||''}</text><line class="dash" x1="${x+87}" y1="285" x2="${x+87}" y2="1080"/>`;}).join('')}
  <line class="call" x1="182" y1="360" x2="407" y2="360"/><text class="s" x="294" y="342" text-anchor="middle">1. 操作()</text>
  <line class="call" x1="407" y1="430" x2="632" y2="430"/><text class="s" x="520" y="412" text-anchor="middle">2. request()</text>
  <line class="call" x1="632" y1="500" x2="857" y2="500"/><text class="s" x="745" y="482" text-anchor="middle">3. execute()</text>
  <line class="call" x1="857" y1="570" x2="1082" y2="570"/><text class="s" x="970" y="552" text-anchor="middle">4. find(id)</text>
  <line class="ret" x1="1307" y1="640" x2="1082" y2="640"/><text class="s" x="1194" y="622" text-anchor="middle">5. EntityPO</text>
  <rect x="80" y="710" width="1320" height="300" fill="#fff" stroke="#263750" stroke-width="2.2"/><path d="M80,710 H165 L190,735 L165,760 H80 Z" fill="#e6eefb" stroke="#263750" stroke-width="2.2"/><text class="h" x="120" y="746">alt</text>
  <text class="t" x="110" y="805">[成功]</text><line class="ret" x1="857" y1="850" x2="407" y2="850"/><text class="s" x="632" y="832" text-anchor="middle">6. ResultVO</text>
  <line x1="80" y1="890" x2="1400" y2="890" stroke="#77859b" stroke-dasharray="8 7" stroke-width="2"/><text class="t" x="110" y="935">[失败]</text><line class="ret" x1="857" y1="975" x2="407" y2="975"/><text class="s" x="632" y="957" text-anchor="middle">7. Error</text>
  <rect class="note" x="1480" y="180" width="250" height="880"/>
  <text class="h" x="1605" y="235" text-anchor="middle">检查表</text>
  <text class="s" x="1505" y="295">□ 内部对象齐全</text><text class="s" x="1505" y="340">□ 消息自上而下</text>
  <text class="s" x="1505" y="385">□ 有调用与返回</text><text class="s" x="1505" y="430">□ 必要时画创建</text>
  <text class="s" x="1505" y="475">□ 用 alt / opt / loop</text><text class="s" x="1505" y="520">□ 对象源自类图</text>
  <text class="s" x="1505" y="565">□ VO/PO 使用合理</text><text class="s" x="1505" y="610">□ 不跨层乱调用</text>
  <line x1="1505" y1="675" x2="1705" y2="675" stroke="#d9a23a"/><text class="h" x="1605" y="730" text-anchor="middle">语言</text><text class="s" x="1505" y="785">对象、类、方法：</text><text class="s" x="1505" y="825">建议英文并与代码一致</text>
`,'04-01-详细设计，第 20-21 页；第 11 章第 87-89 页',5));

pages.push(page('5. 物理包图模板','表达客户端/服务器、分层、接口实现以及 VO/PO 依赖',`
  <rect class="panel" x="55" y="150" width="1410" height="1015"/>
  <rect class="node" x="90" y="180" width="1315" height="135"/><text class="h" x="120" y="220">«device» Client / Browser</text>
  ${pkg(180,245,1100,45,'web')}<text class="t" x="730" y="292" text-anchor="middle">HTML　　CSS　　JavaScript</text>
  <path class="dep" d="M730,315 L730,385"/><text class="s" x="840" y="365">HTTP + REST API</text>
  <rect class="node" x="90" y="385" width="1315" height="755"/><text class="h" x="120" y="425">«node» Server</text>
  ${pkg(150,475,940,70,'presentation')}${pkg(150,610,940,70,'Service Interface')}${pkg(150,745,940,70,'Service Impl')}${pkg(150,880,940,70,'DAO Interface')}${pkg(150,1015,940,70,'DAO Impl')}
  <text class="s" x="620" y="525" text-anchor="middle">[domain1]　[domain2]　[domain3]　[domain4]　[domain5]</text>
  <text class="s" x="620" y="660" text-anchor="middle">IService　IService　IService ...</text><text class="s" x="620" y="795" text-anchor="middle">ServiceImpl　ServiceImpl ...</text><text class="s" x="620" y="930" text-anchor="middle">IDao　IDao　IDao ...</text><text class="s" x="620" y="1065" text-anchor="middle">DaoImpl　DaoImpl　DaoImpl ...</text>
  ${pkg(1140,535,210,200,'VO')}${pkg(1140,805,210,230,'PO')}
  <text class="s" x="1245" y="620" text-anchor="middle">Value Object</text><text class="s" x="1245" y="660" text-anchor="middle">面向展示</text><text class="s" x="1245" y="900" text-anchor="middle">Persistent Object</text><text class="s" x="1245" y="940" text-anchor="middle">面向持久化</text>
  <path class="dep" d="M430,545 L430,610"/><path class="realize" d="M650,745 L650,680"/><path class="dep" d="M430,815 L430,880"/><path class="realize" d="M650,1015 L650,950"/>
  <path class="dep" d="M1090,510 L1140,590"/><path class="dep" d="M1090,645 L1140,645"/><path class="dep" d="M1090,780 L1140,860"/><path class="dep" d="M1090,915 L1140,915"/><path class="dep" d="M1090,1050 L1140,990"/>
  <rect class="note" x="1490" y="180" width="240" height="900"/><text class="h" x="1610" y="235" text-anchor="middle">检查表</text>
  <text class="s" x="1515" y="295">□ 客户端/服务器</text><text class="s" x="1515" y="340">□ HTTP/REST</text>
  <text class="s" x="1515" y="385">□ 五个功能域</text><text class="s" x="1515" y="430">□ 接口独立成层</text>
  <text class="s" x="1515" y="475">□ 实现指向接口</text><text class="s" x="1515" y="520">□ 上层依赖接口</text>
  <text class="s" x="1515" y="565">□ VO/PO 分离</text><text class="s" x="1515" y="610">□ 依赖方向向下</text>
  <text class="s" x="1515" y="655">□ 展示层不碰 DAO</text><text class="s" x="1515" y="700">□ Service 不碰 DAO Impl</text>
  <line x1="1515" y1="760" x2="1705" y2="760" stroke="#d9a23a"/><text class="h" x="1610" y="815" text-anchor="middle">语言</text><text class="s" x="1515" y="865">包、接口、类：</text><text class="s" x="1515" y="905">使用英文代码命名</text>
`,'03-02-体系结构风格与设计过程，第 18、49-51 页',6));

pages.push(page('6. 4+1 视图模板','四个工程视图由场景视图驱动并相互验证',`
  <rect class="panel" x="70" y="150" width="1660" height="960"/>
  <rect x="700" y="480" width="400" height="220" rx="110" fill="#5b3f91"/><text x="900" y="565" text-anchor="middle" font-size="34" font-weight="800" fill="#fff">场景视图 +1</text><text x="900" y="610" text-anchor="middle" font-size="23" fill="#fff">用例图 / 用例场景</text><text x="900" y="648" text-anchor="middle" font-size="20" fill="#fff">驱动并验证其他四个视图</text>
  <rect class="accent" x="170" y="235" width="480" height="225" rx="20"/><text class="h" x="410" y="285" text-anchor="middle">逻辑视图</text><text class="t" x="410" y="335" text-anchor="middle">功能、类与包的组织</text><text class="t" x="410" y="380" text-anchor="middle">类图 / 包图</text><text class="s" x="410" y="420" text-anchor="middle">架构师、开发者</text>
  <rect class="accent" x="1150" y="235" width="480" height="225" rx="20"/><text class="h" x="1390" y="285" text-anchor="middle">开发视图</text><text class="t" x="1390" y="335" text-anchor="middle">代码组织、模块划分</text><text class="t" x="1390" y="380" text-anchor="middle">组件图</text><text class="s" x="1390" y="420" text-anchor="middle">开发者</text>
  <rect class="accent" x="170" y="760" width="480" height="225" rx="20"/><text class="h" x="410" y="810" text-anchor="middle">进程视图</text><text class="t" x="410" y="860" text-anchor="middle">并发、同步、性能</text><text class="t" x="410" y="905" text-anchor="middle">活动图 / 顺序图</text><text class="s" x="410" y="945" text-anchor="middle">系统集成者</text>
  <rect class="accent" x="1150" y="760" width="480" height="225" rx="20"/><text class="h" x="1390" y="810" text-anchor="middle">物理视图</text><text class="t" x="1390" y="860" text-anchor="middle">部署拓扑、硬件映射</text><text class="t" x="1390" y="905" text-anchor="middle">部署图</text><text class="s" x="1390" y="945" text-anchor="middle">运维工程师</text>
  <path class="dep" d="M720,510 L620,440"/><path class="dep" d="M1080,510 L1180,440"/><path class="dep" d="M720,670 L620,790"/><path class="dep" d="M1080,670 L1180,790"/>
  <rect class="good" x="600" y="1030" width="600" height="70"/><text class="t" x="900" y="1073" text-anchor="middle">同一系统的不同关注点，不是五张互不相干的图</text>
`,'03-03-体系结构设计实践与验证，第 27-28 页',7));

pages.push(page('7. 状态图模板','描述一个明确主体在其生命周期中的合法状态转换',`
  <rect class="panel" x="65" y="150" width="1250" height="1010"/>
  <circle cx="300" cy="260" r="20" fill="#263750"/><line class="call" x1="320" y1="260" x2="480" y2="330"/><text class="s" x="400" y="270">create</text>
  <rect class="node" x="480" y="300" width="260" height="100"/><text class="h" x="610" y="360" text-anchor="middle">State A</text>
  <rect class="node" x="900" y="300" width="260" height="100"/><text class="h" x="1030" y="360" text-anchor="middle">State B</text>
  <rect class="node" x="690" y="650" width="260" height="100"/><text class="h" x="820" y="710" text-anchor="middle">State C</text>
  <path class="call" d="M740,350 L900,350"/><text class="s" x="820" y="325" text-anchor="middle">event [guard] / action</text>
  <path class="call" d="M1030,400 C1040,530 930,600 860,650"/><text class="s" x="1015" y="545">event</text>
  <path class="call" d="M750,650 C650,565 590,500 610,400"/><text class="s" x="625" y="550">retry [condition]</text>
  <path class="call" d="M950,700 L1140,700"/><circle cx="1200" cy="700" r="27" fill="none" stroke="#263750" stroke-width="3"/><circle cx="1200" cy="700" r="18" fill="#263750"/><text class="s" x="1050" y="675">finish</text>
  <rect class="note" x="1360" y="180" width="370" height="860"/><text class="h" x="1545" y="235" text-anchor="middle">作图检查表</text>
  <text class="t" x="1390" y="300">□ 先写清状态机主体</text><text class="t" x="1390" y="350">□ 状态是稳定情形</text>
  <text class="t" x="1390" y="400">□ 操作写在转换线上</text><text class="t" x="1390" y="450">□ 有初态和终态</text>
  <text class="t" x="1390" y="500">□ 事件触发转换</text><text class="t" x="1390" y="550">□ 守卫条件写在 []</text>
  <text class="t" x="1390" y="600">□ 动作写在 / 后</text><text class="t" x="1390" y="650">□ 不画非法跨状态跳转</text>
  <line x1="1390" y1="710" x2="1700" y2="710" stroke="#d9a23a"/><text class="h" x="1545" y="765" text-anchor="middle">标准格式</text><text class="t" x="1390" y="820">事件 [守卫条件] / 动作</text><text class="s" x="1390" y="875">若需映射枚举和方法，</text><text class="s" x="1390" y="910">状态及事件建议用英文</text>
`,'02-04-需求分析与AI辅助建模，第 38-43 页',8));

pages.push(page('8. 程序流程图模板','描述一个方法内部的输入、处理、判断、循环与输出',`
  <rect class="panel" x="65" y="150" width="1230" height="1010"/>
  <rect class="node" x="520" y="190" width="300" height="80" rx="40"/><text class="h" x="670" y="240" text-anchor="middle">Start</text>
  <polygon points="500,330 840,330 800,420 460,420" fill="#fff" stroke="#263750" stroke-width="2.5"/><text class="h" x="650" y="385" text-anchor="middle">READ input</text>
  <rect class="node" x="500" y="480" width="340" height="90"/><text class="h" x="670" y="535" text-anchor="middle">process / initialize</text>
  <polygon points="670,640 850,740 670,840 490,740" fill="#fff" stroke="#263750" stroke-width="2.5"/><text class="h" x="670" y="735" text-anchor="middle">condition?</text>
  <polygon points="500,900 840,900 800,990 460,990" fill="#fff" stroke="#263750" stroke-width="2.5"/><text class="h" x="650" y="955" text-anchor="middle">PRINT result</text>
  <rect class="node" x="520" y="1040" width="300" height="80" rx="40"/><text class="h" x="670" y="1090" text-anchor="middle">End</text>
  <line class="call" x1="670" y1="270" x2="670" y2="330"/><line class="call" x1="670" y1="420" x2="670" y2="480"/><line class="call" x1="670" y1="570" x2="670" y2="640"/>
  <line class="call" x1="670" y1="840" x2="670" y2="900"/><text class="t" x="700" y="875">Yes</text><line class="call" x1="670" y1="990" x2="670" y2="1040"/>
  <path class="call" d="M490,740 L300,740 L300,525 L500,525"/><text class="t" x="345" y="715">No</text><text class="s" x="315" y="625">update / loop</text>
  <rect class="note" x="1360" y="180" width="370" height="860"/><text class="h" x="1545" y="235" text-anchor="middle">作图检查表</text>
  <text class="t" x="1390" y="300">□ 圆角框：开始/结束</text><text class="t" x="1390" y="350">□ 平行四边形：输入/输出</text>
  <text class="t" x="1390" y="400">□ 矩形：处理</text><text class="t" x="1390" y="450">□ 菱形：判断</text>
  <text class="t" x="1390" y="500">□ 分支标 Yes / No</text><text class="t" x="1390" y="550">□ 循环有返回边</text>
  <text class="t" x="1390" y="600">□ 循环有退出条件</text><text class="t" x="1390" y="650">□ 不混入跨对象消息</text>
  <line x1="1390" y1="710" x2="1700" y2="710" stroke="#d9a23a"/><text class="h" x="1545" y="765" text-anchor="middle">语言</text><text class="t" x="1390" y="820">变量、表达式、方法：</text><text class="t" x="1390" y="860">使用英文并与代码一致</text>
`,'代码设计，第 44-46 页',9));

(async () => {
  for (let i = 0; i < pages.length; i++) {
    const stem = String(i + 1).padStart(2, '0');
    const svgPath = path.join(OUT, `${stem}.svg`);
    const pngPath = path.join(OUT, `${stem}.png`);
    fs.writeFileSync(svgPath, pages[i]);
    await sharp(Buffer.from(pages[i])).png().toFile(pngPath);
  }
})();
