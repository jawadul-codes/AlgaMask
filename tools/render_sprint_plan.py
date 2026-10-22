"""Render the revised Markdown sprint plan as a paginated, shareable PDF."""

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/RAG_SPRINT_PLAN.md"
OUTPUT = ROOT / "output/pdf/algamask-rag-sprint-plan.pdf"
FONT_ROOT = Path("/System/Library/Fonts/Supplemental")


def inline(text):
    value = escape(text)
    value = re.sub(r"`([^`]+)`", r'<font color="#215B68">\1</font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def render():
    pdfmetrics.registerFont(TTFont("Plan", str(FONT_ROOT / "Arial.ttf")))
    pdfmetrics.registerFont(TTFont("PlanBold", str(FONT_ROOT / "Arial Bold.ttf")))
    pdfmetrics.registerFontFamily("Plan", normal="Plan", bold="PlanBold")
    styles = {
        "title": ParagraphStyle("title", fontName="PlanBold", fontSize=23, leading=28,
                                textColor=colors.HexColor("#153D46"), spaceAfter=17),
        "h2": ParagraphStyle("h2", fontName="PlanBold", fontSize=11, leading=14,
                             textColor=colors.HexColor("#215B68"), spaceBefore=11,
                             spaceAfter=6, keepWithNext=True),
        "body": ParagraphStyle("body", fontName="Plan", fontSize=9.4, leading=13.5,
                               textColor=colors.HexColor("#26333B"), spaceAfter=7,
                               alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", fontName="Plan", fontSize=9.4, leading=13.5,
                                 textColor=colors.HexColor("#26333B"), leftIndent=11,
                                 firstLineIndent=0, bulletIndent=0, spaceAfter=6),
    }
    story = []
    buffer = []

    def flush():
        if buffer:
            story.append(Paragraph(inline(" ".join(buffer)), styles["body"]))
            buffer.clear()

    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if line == "---":
            flush()
            story.append(PageBreak())
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), styles["title"]))
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(inline(line[3:]), styles["h2"]))
        elif line.startswith("- "):
            flush()
            story.append(Paragraph(inline(line[2:]), styles["bullet"], bulletText="•"))
        elif not line.strip():
            flush()
        else:
            buffer.append(line.strip())
    flush()

    def decorate(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#BBD3D6"))
        canvas.setLineWidth(0.7)
        canvas.line(43, height - 37, width - 43, height - 37)
        canvas.setFont("PlanBold", 8)
        canvas.setFillColor(colors.HexColor("#215B68"))
        canvas.drawString(43, height - 28, "ALGAMASK / RAG IMPLEMENTATION")
        canvas.setFont("Plan", 7.5)
        canvas.drawRightString(width - 43, height - 28, "REV 1.1  |  22 OCT 2026")
        canvas.setFillColor(colors.HexColor("#63777B"))
        canvas.drawString(43, 24, "Task-based stages. Complete acceptance gates before dependent work.")
        canvas.drawRightString(width - 43, 24, str(doc.page))
        canvas.restoreState()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=43, leftMargin=43,
                            topMargin=55, bottomMargin=43, title="AlgaMask RAG Implementation Sprint",
                            author="AlgaMask", subject="Seven task-based stages with RAG acceptance gates")
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    print(OUTPUT)


if __name__ == "__main__":
    render()
