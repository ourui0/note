from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / '机器学习-作业二.pdf'
OUT = ROOT / '欧睿_241870008_作业二.pdf'
TMP = ROOT / 'tmp_answers.pdf'
FONT = '/System/Library/Fonts/Supplemental/Songti.ttc'
registerFont(TTFont('Song', FONT, subfontIndex=3))
registerFont(TTFont('SongBold', FONT, subfontIndex=1))

styles = getSampleStyleSheet()
body = ParagraphStyle('body', fontName='Song', fontSize=9.2, leading=14, spaceAfter=5)
body_small = ParagraphStyle('small', fontName='Song', fontSize=8.4, leading=12.3, spaceAfter=3)
eq = ParagraphStyle('eq', fontName='Song', fontSize=9.1, leading=14, alignment=TA_CENTER, spaceAfter=5)
head = ParagraphStyle('head', fontName='SongBold', fontSize=15, leading=20, spaceBefore=2, spaceAfter=8)
sub = ParagraphStyle('sub', fontName='SongBold', fontSize=10.5, leading=15, spaceBefore=6, spaceAfter=4)
code = ParagraphStyle('code', fontName='Courier', fontSize=7.4, leading=9.5, leftIndent=8, rightIndent=8, backColor=colors.HexColor('#f4f4f4'), borderPadding=5, spaceAfter=6)

def P(t, s=body): return Paragraph(t, s)

def answer_page(canvas, doc):
    w,h=A4
    canvas.saveState()
    canvas.setFont('Song',9)
    canvas.drawString(2.1*cm,h-1.25*cm,'2026年秋季')
    canvas.drawCentredString(w/2,h-1.25*cm,'机器学习')
    canvas.drawRightString(w-2.1*cm,h-1.25*cm,'作业二')
    canvas.setLineWidth(.5); canvas.line(2.1*cm,h-1.43*cm,w-2.1*cm,h-1.43*cm)
    canvas.setFont('Times-Roman',9); canvas.drawCentredString(w/2,1.25*cm,str(doc.page))
    canvas.restoreState()

def tbl(rows, widths):
    t=Table(rows,colWidths=widths,hAlign='CENTER')
    t.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Song'),('FONTSIZE',(0,0),(-1,-1),8.4),('LEADING',(0,0),(-1,-1),11),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LINEABOVE',(0,0),(-1,0),.8,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black),
    ]))
    return t

doc=BaseDocTemplate(str(TMP),pagesize=A4,leftMargin=2.1*cm,rightMargin=2.1*cm,topMargin=1.8*cm,bottomMargin=1.7*cm)
frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='f')
doc.addPageTemplates(PageTemplate(id='p',frames=[frame],onPage=answer_page))

sections=[]
# Q1
s=[P('姓名：欧睿　　学号：241870008　　日期：2026年10月20日', ParagraphStyle('id',parent=body,fontName='SongBold',fontSize=11,textColor=colors.blue,spaceAfter=10)),
P('一. 线性回归与冗余属性：解',head),
P('1. 由 <i>J</i>(<i>w</i>,<i>b</i>)=1/2 Σ(y<sub>i</sub>−wx<sub>i</sub>−b)<super>2</super>，有：'),
P('∂J/∂b = −Σ(y<sub>i</sub>−wx<sub>i</sub>−b)=0，因此 b = ȳ − w x̄。',eq),
P('将其代回 ∂J/∂w=−Σx<sub>i</sub>(y<sub>i</sub>−wx<sub>i</sub>−b)=0，得到：'),
P('<i>w</i><super>*</super> = Σ(x<sub>i</sub>−x̄)(y<sub>i</sub>−ȳ) / Σ(x<sub>i</sub>−x̄)<super>2</super>，　<i>b</i><super>*</super>=ȳ−<i>w</i><super>*</super>x̄。',eq),
P('2. 训练集 x̄=1.5，ȳ=2，Σ(x−x̄)(y−ȳ)=3，Σ(x−x̄)<super>2</super>=5，所以 w*=0.6，b*=1.1。'),
P('测试预测：ŷ(4)=3.5，ŷ(5)=4.1。测试均方误差：MSE=[(4−3.5)<super>2</super>+(4−4.1)<super>2</super>]/2=0.13。'),
P('3. 因为 x<sub>2</sub>=2x，模型实际只由组合 w<sub>1</sub>+2w<sub>2</sub> 决定，因此 (w<sub>1</sub>,w<sub>2</sub>) 不唯一，只需满足 w<sub>1</sub>+2w<sub>2</sub>=0.6。两组可行参数例如：'),
P('(w<sub>1</sub>,w<sub>2</sub>,b)=(0.6,0,1.1)，或 (0,0.3,1.1)。两组参数对训练集和测试集给出完全相同的预测。'),
P('4. NumPy 实现：',sub),
P('def linear_regression(X_train, y_train):<br/>　x = X_train[:, 0]<br/>　xb, yb = x.mean(), y_train.mean()<br/>　w = ((x-xb)*(y_train-yb)).sum() / ((x-xb)**2).sum()<br/>　b = yb - w*xb<br/>　return w, b<br/><br/>def MSE(y_true, y_pred):<br/>　return np.mean((y_true-y_pred)**2)',code),
P('输出为：w=0.6，b=1.1，y_pred=[3.5,4.1]，MSE=0.13。')]
sections.append(s)
# Q2
s=[P('二. 对数几率回归与类别不平衡：解',head),
P('1. 当 t=0.5 时，p≥0.5 等价于 w<sup>T</sup>x+b≥0，因为 sigmoid 函数单调递增。决策边界 w<sup>T</sup>x+b=0 是特征空间中的超平面：二维时为直线，三维时为平面。'),
P('2. 逐个阈值统计：',body),
tbl([['阈值','TP','FP','TN','FN','准确率','查准率','查全率'],['0.5','1','1','7','1','0.80','0.50','0.50'],['0.3','2','3','5','0','0.70','0.40','1.00']], [1.4*cm,1.1*cm,1.1*cm,1.1*cm,1.1*cm,1.5*cm,1.5*cm,1.5*cm]),
P('降低阈值后，更多样本被判为正类：TP 从1升至2、FN 从1降至0，查全率提高；但 FP 从1升至3，查准率下降，准确率由0.80降至0.70。'),
P('3. p/(1−p)≥m<sup>+</sup>/m<sup>−</sup>。由 p/(1−p)≥r 可得 p≥r/(1+r)。本题 m+=20，m−=80，r=0.25，因此等价概率阈值为：'),
P('t = (m+/m−)/(1+m+/m−) = m+/(m++m−) = 20/100 = 0.20。',eq),
P('固定模型只改变决策阈值，不改变已学习的 w、b 和概率输出；欠采样则改变训练数据分布并重新训练，因而会改变模型参数，二者效果不必相同。'),
P('4. 代码实现：',sub),
P('def evaluate(y, p, threshold):<br/>　pred = (p >= threshold).astype(int)<br/>　TP = np.sum((y==1)&(pred==1)); FP = np.sum((y==0)&(pred==1))<br/>　TN = np.sum((y==0)&(pred==0)); FN = np.sum((y==1)&(pred==0))<br/>　n = len(y)<br/>　acc = (TP+TN)/n if n else 0<br/>　pre = TP/(TP+FP) if TP+FP else 0<br/>　rec = TP/(TP+FN) if TP+FN else 0<br/>　return TP,FP,TN,FN,acc,pre,rec',code)]
sections.append(s)
# Q3
s=[P('三. 连续属性划分与缺失值：解',head),
P('1. 相邻不同属性值为 1,2,3,4,5,6，因此候选阈值为 1.5、2.5、3.5、4.5、5.5。非缺失样本标签为 [0,0,1,1,0,1]，正负各3个，所以 H(D~)=1.000。'),
P('2. t=2.5：左支 [0,0]，熵为0；右支 [1,1,0,1]，熵为 −(1/4)log₂(1/4)−(3/4)log₂(3/4)=0.811。'),
P('Gain(2.5)=1−(2/6)×0−(4/6)×0.811=0.459。'),
P('t=4.5：左支 [0,0,1,1]，右支 [0,1]，两支熵均为1，因此 Gain(4.5)=1−(4/6)×1−(2/6)×1=0。选 t=2.5。'),
P('3. 缺失值修正比例 ρ=|D~|/|D|=6/8=0.75。故 Gain(D,x,2.5)=0.75×0.459=0.344；Gain(D,x,4.5)=0。修正后选择不变，仍为2.5。'),
P('4. 采用 t=2.5，非缺失样本左支有2个、右支有4个，因此每个缺失样本按 1/3 与 2/3 的权重下传到左、右支。样本7和8的左右权重均为：左 1/3，右 2/3。'),
P('样本7(y=0)：左支增加负类 1/3，右支增加负类 2/3；样本8(y=1)：左支增加正类 1/3，右支增加正类 2/3。分配后：左支正类 1+1/3=4/3，负类 2+1/3=7/3；右支正类 2+2/3=8/3，负类 1+2/3=5/3。')]
sections.append(s)
# Q4
s=[P('四. 决策树的预剪枝与后剪枝：解',head),
P('1. 根节点训练集 y=0 有9个、y=1 有7个，故不划分时预测0。按 A 划分后：A=0 子节点训练集为(7,3)，预测0；A=1 子节点为(2,4)，预测1。完整两层树四个叶节点分别为： (A=0,B=0)预测0，(A=0,B=1)预测1，(A=1,B=0)预测1，(A=1,B=1)预测0。'),
P('2. 根节点不划分时，验证集多数类为0，准确率为6/10=0.60。根节点按 A 划分后，A=0 预测0，对应3个正确；A=1 预测1，对应2个正确，准确率为5/10=0.50。由于没有严格提高，预剪枝拒绝根节点划分，预剪枝结果为单叶节点预测0。'),
P('3. 从完整两层树开始：'),
tbl([['候选操作','验证集正确数','验证准确率','处理'],['剪 A=0 子树为叶0','8','0.80','拒绝'],['剪 A=1 子树为叶1','7','0.70','拒绝'],['剪根节点为叶0','6','0.60','拒绝']], [4.3*cm,2.7*cm,2.7*cm,2.6*cm]),
P('完整两层树的验证准确率为10/10=1.00。剪 A=0 子树后，A=0 验证样本中3个0正确、2个1错误，加上 A=1 子树5个正确，共8/10=0.80，拒绝；剪 A=1 子树后，共7/10=0.70，拒绝；最后剪根节点后为6/10=0.60，拒绝。因此最终树保留完整两层结构：根按 A 划分，两个子节点再按 B 划分。'),
P('4. 预剪枝在树生长过程中提前停止，可能因当前划分在验证集上暂未带来提升而阻止后续有用划分；后剪枝先生成完整树，再从子树向上检查，能够利用后续划分带来的组合效果。本题中预剪枝直接得到单叶树，而后剪枝保留完整树。验证集用于剪枝决策和模型选择，不能当作最终无偏性能报告；测试集应在所有训练、剪枝和参数选择完成后只使用一次，用于最终泛化性能评估。')]
sections.append(s)

def build_answer(i, items):
    p=BaseDocTemplate(str(ROOT/f'ans{i}.pdf'),pagesize=A4,leftMargin=2.1*cm,rightMargin=2.1*cm,topMargin=1.8*cm,bottomMargin=1.7*cm)
    p.addPageTemplates(PageTemplate(id='p',frames=[Frame(p.leftMargin,p.bottomMargin,p.width,p.height,id='f')],onPage=answer_page))
    p.build(items)
    return PdfReader(str(ROOT/f'ans{i}.pdf'))

read=PdfReader(str(SOURCE)); writer=PdfWriter()
for i,page in enumerate(read.pages):
    writer.add_page(page)
    ans=build_answer(i+1,sections[i])
    for ap in ans.pages: writer.add_page(ap)
with OUT.open('wb') as f: writer.write(f)
print(OUT)
