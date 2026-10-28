from pathlib import Path
import re
from xml.sax.saxutils import escape

import pdfplumber
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
SRC = ROOT / "output/pdf/微观经济学选择题专项练习_第一二三四五六八章.pdf"
OUT = ROOT / "output/pdf/微观经济学选择题专项练习_第一二三四五六八章_章后答案版.pdf"

CHAPTERS = [
    "第一章 需求、供给和均衡价格",
    "第二章 消费者选择",
    "第三章 企业的生产和成本",
    "第四章 完全竞争市场",
    "第五章 不完全竞争市场",
    "第六章 生产要素市场与收入分配",
    "第八章 市场失灵和微观经济政策",
]


def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s.replace("\u3000", " ")).strip()
    return s


def extract_full_text() -> str:
    with pdfplumber.open(SRC) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def remove_running_lines(text: str) -> str:
    kept = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "微观经济学选择题专项练习":
            continue
        if re.fullmatch(r"第 \d+ 页", line):
            continue
        kept.append(line)
    return "\n".join(kept)


def split_sections(text: str, start_marker: str, end_marker: str | None = None) -> str:
    start = text.index(start_marker)
    if end_marker is None:
        return text[start:]
    end = text.index(end_marker, start)
    return text[start:end]


def split_by_chapter(text: str) -> dict[str, str]:
    positions = []
    for ch in CHAPTERS:
        m = re.search(re.escape(ch), text)
        if not m:
            raise RuntimeError(f"未找到章节：{ch}")
        positions.append((m.start(), ch))
    positions.sort()
    out = {}
    for i, (pos, ch) in enumerate(positions):
        next_pos = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        out[ch] = text[pos + len(ch):next_pos].strip()
    return out


def parse_questions(section: str) -> list[dict]:
    starts = list(re.finditer(r"(?m)^(\d+)\.\s*", section))
    items = []
    for idx, m in enumerate(starts):
        q_no = int(m.group(1))
        chunk = section[m.end(): starts[idx + 1].start() if idx + 1 < len(starts) else len(section)]
        choice_matches = list(re.finditer(r"(?m)^([ABCD])\.\s*", chunk))
        if len(choice_matches) != 4:
            raise RuntimeError(f"第{q_no}题选项解析失败，找到{len(choice_matches)}个选项")
        stem = clean_text(chunk[: choice_matches[0].start()])
        choices = {}
        for ci, cm in enumerate(choice_matches):
            end = choice_matches[ci + 1].start() if ci + 1 < len(choice_matches) else len(chunk)
            choices[cm.group(1)] = clean_text(chunk[cm.end():end])
        items.append({"no": q_no, "stem": stem, "choices": choices})
    return items


def parse_answers(text: str) -> dict[int, dict[str, str]]:
    start = text.index("二、逐题解析")
    body = text[start:]
    body = re.sub(r"\n本练习依据课程PPT知识范围编写.*", "", body, flags=re.S)
    pattern = re.compile(
        r"(?m)^(\d+)\. 答案：([A-D])\n解析：(.*?)(?=\n\d+\. 答案：|\n(?:第一章|第二章|第三章|第四章|第五章|第六章|第八章)|\Z)",
        re.S,
    )
    answers = {}
    for m in pattern.finditer(body):
        answers[int(m.group(1))] = {
            "answer": m.group(2),
            "explanation": clean_text(m.group(3)),
        }
    if len(answers) != 70:
        raise RuntimeError(f"答案解析数量异常：{len(answers)}")
    return answers


def build_data():
    full = remove_running_lines(extract_full_text())
    q_text = split_sections(full, "第一章 需求、供给和均衡价格", "答案与解析")
    questions_by_chapter = {
        ch: parse_questions(sec) for ch, sec in split_by_chapter(q_text).items()
    }
    answers = parse_answers(full)
    return questions_by_chapter, answers


def p(text, style):
    return Paragraph(escape(text), style)


def make_styles():
    font_name = "STHeitiEmbedded"
    pdfmetrics.registerFont(TTFont(font_name, "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=0))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "CoverTitle", fontName=font_name, fontSize=26, leading=34,
        alignment=TA_CENTER, textColor=colors.HexColor("#1f2937"), spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        "CoverSub", fontName=font_name, fontSize=15, leading=24,
        alignment=TA_CENTER, textColor=colors.HexColor("#374151"),
    ))
    styles.add(ParagraphStyle(
        "H1", fontName=font_name, fontSize=15.5, leading=22,
        textColor=colors.HexColor("#111827"), spaceBefore=8, spaceAfter=8,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        "H2", fontName=font_name, fontSize=12.5, leading=18,
        textColor=colors.HexColor("#111827"), spaceBefore=7, spaceAfter=5,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        "BodyCN", fontName=font_name, fontSize=10.5, leading=16,
        alignment=TA_LEFT, wordWrap="CJK", spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "SmallCN", fontName=font_name, fontSize=9.2, leading=13.5,
        alignment=TA_LEFT, wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        "TinyCN", fontName=font_name, fontSize=8.5, leading=12,
        alignment=TA_CENTER, wordWrap="CJK",
    ))
    return styles


class NumberedDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=22 * mm,
            rightMargin=22 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="微观经济学选择题专项练习",
            author="Codex",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self.header_footer)])

    def header_footer(self, canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont("STHeitiEmbedded", 9)
            canvas.setFillColor(colors.HexColor("#6b7280"))
            canvas.drawString(doc.leftMargin, A4[1] - 12 * mm, "微观经济学选择题专项练习")
            canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()


def answer_table(chapter_questions, answers, styles):
    nums = [q["no"] for q in chapter_questions]
    data = [
        [p("题号", styles["TinyCN"])] + [p(str(n), styles["TinyCN"]) for n in nums],
        [p("答案", styles["TinyCN"])] + [p(answers[n]["answer"], styles["TinyCN"]) for n in nums],
    ]
    table = Table(data, colWidths=[14 * mm] + [12 * mm] * len(nums), hAlign="LEFT")
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#f9fafb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_pdf():
    questions_by_chapter, answers = build_data()
    styles = make_styles()
    story = []

    story.extend([
        Spacer(1, 46 * mm),
        p("微观经济学", styles["CoverTitle"]),
        p("选择题专项练习", styles["CoverTitle"]),
        Spacer(1, 8 * mm),
        p("第一、二、三、四、五、六、八章", styles["CoverSub"]),
        Spacer(1, 18 * mm),
    ])

    meta = [
        ["题型", "单项选择题"],
        ["题量", "70题，每章10题"],
        ["结构", "每章题目后紧跟本章答案与解析"],
        ["参考资料", "对应七章课程PPT及《作业答案汇总》"],
    ]
    meta_table = Table(
        [[p(a, styles["BodyCN"]), p(b, styles["BodyCN"])] for a, b in meta],
        colWidths=[28 * mm, 105 * mm],
        hAlign="CENTER",
    )
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10 * mm))
    story.append(p("建议先独立完成每章题目，再核对该章答案与解析。", styles["CoverSub"]))
    story.append(PageBreak())

    story.append(p("作答说明", styles["H1"]))
    story.append(p("每题只有一个最符合题意的选项。题目按章节编排，每章10题；为便于复习与订正，本版将答案速查和逐题解析直接放在对应章节之后。计算题建议保留关键式，便于核对概念与方法。", styles["BodyCN"]))
    story.append(Spacer(1, 4 * mm))

    for ci, ch in enumerate(CHAPTERS):
        if ci:
            story.append(PageBreak())
        story.append(p(ch, styles["H1"]))
        for q in questions_by_chapter[ch]:
            block = [p(f"{q['no']}. {q['stem']}", styles["BodyCN"])]
            for opt in "ABCD":
                block.append(p(f"{opt}. {q['choices'][opt]}", styles["BodyCN"]))
            block.append(Spacer(1, 2 * mm))
            story.append(KeepTogether(block))

        story.append(Spacer(1, 3 * mm))
        story.append(p(f"{ch} 答案与解析", styles["H1"]))
        story.append(p("答案速查", styles["H2"]))
        story.append(answer_table(questions_by_chapter[ch], answers, styles))
        story.append(Spacer(1, 3 * mm))
        story.append(p("逐题解析", styles["H2"]))
        for q in questions_by_chapter[ch]:
            n = q["no"]
            item = answers[n]
            story.append(KeepTogether([
                p(f"{n}. 答案：{item['answer']}", styles["BodyCN"]),
                p(f"解析：{item['explanation']}", styles["SmallCN"]),
                Spacer(1, 1.5 * mm),
            ]))

    story.append(Spacer(1, 4 * mm))
    story.append(p("本练习依据课程PPT知识范围编写，题型表达参照《作业答案汇总》的单项选择题格式。", styles["SmallCN"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = NumberedDoc(str(OUT))
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build_pdf()
