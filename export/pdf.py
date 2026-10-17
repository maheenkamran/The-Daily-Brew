import io
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, FrameBreak, NextPageTemplate, HRFlowable,
                                KeepTogether, KeepInFrame)

W, H = A4
M = 14 * mm            # page margin
GAP = 5 * mm           # gap between columns
COLS = 3
COL_W = (W - 2 * M - (COLS - 1) * GAP) / COLS
MAST_H = 30 * mm       # masthead height (page 1)
LEAD_H = 64 * mm       # lead story box (page 1)
COL_BOTTOM = 18 * mm

INK = colors.HexColor("#111111")
PAPER = colors.HexColor("#f6f0e1")
ACCENT = colors.HexColor("#8b1a1a")
GREY = colors.HexColor("#555555")

S = {
    "lead":     ParagraphStyle("lead", fontName="Times-Bold", fontSize=26, leading=28, spaceAfter=4),
    "lead_sum": ParagraphStyle("lead_sum", fontName="Times-Roman", fontSize=12, leading=15, spaceAfter=4),
    "sec":      ParagraphStyle("sec", fontName="Times-Bold", fontSize=9, leading=11,
                               textColor=ACCENT, spaceBefore=8, spaceAfter=2),
    "title":    ParagraphStyle("title", fontName="Times-Bold", fontSize=12, leading=13.5,
                               spaceBefore=4, spaceAfter=2),
    "sum":      ParagraphStyle("sum", fontName="Times-Roman", fontSize=9, leading=11.5),
    "meta":     ParagraphStyle("meta", fontName="Times-Italic", fontSize=7.5, leading=9, textColor=GREY),
    "why":      ParagraphStyle("why", fontName="Times-Italic", fontSize=7.5, leading=9,
                               textColor=ACCENT, spaceAfter=5),
}

def _clean(s):
    """Built-in PDF fonts only support Latin text, so drop emoji and other scripts."""
    return (s or "").encode("cp1252", "ignore").decode("cp1252")

def _t(s):
    return escape(_clean(s))

def _link(url):
    return escape(url or "", {'"': "&quot;"})

# ---------- page decoration ----------
def _decor(user, day, first, col_top):
    interests = user["interests"]
    focus = max(interests, key=interests.get) if interests else "General"
    title = _clean(f"THE {user['name'].upper()} CHRONICLE")
    nice = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y").upper()
    dateline = _clean(f"{nice}   |   {focus.upper()} EDITION   |   {user['persona'].upper()}")

    def draw(c, doc):
        c.saveState()
        c.setFillColor(PAPER)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setStrokeColor(INK)
        top = H - M

        if first:
            size = min(40, (W - 2 * M) / stringWidth(title, "Times-Bold", 1))
            c.setLineWidth(2.5); c.line(M, top, W - M, top)
            c.setLineWidth(0.5); c.line(M, top - 3, W - M, top - 3)
            c.setFont("Times-Bold", size)
            c.drawCentredString(W / 2, top - 12 - size * 0.72, title)
            c.setLineWidth(0.5); c.line(M, top - 56, W - M, top - 56)
            c.setFont("Times-Roman", 8)
            c.drawCentredString(W / 2, top - 67, dateline)
            c.setLineWidth(0.5); c.line(M, top - 73, W - M, top - 73)
            c.setLineWidth(2.5); c.line(M, top - 76, W - M, top - 76)
        else:
            c.setFont("Times-Bold", 10)
            c.drawString(M, top - 8, title)
            c.setFont("Times-Roman", 8)
            c.drawRightString(W - M, top - 8, _clean(nice))
            c.setLineWidth(1); c.line(M, top - 12, W - M, top - 12)

        # column rules
        c.setStrokeColor(colors.HexColor("#999999"))
        c.setLineWidth(0.3)
        for k in range(1, COLS):
            x = M + k * (COL_W + GAP) - GAP / 2
            c.line(x, COL_BOTTOM, x, col_top)

        # footer
        c.setFillColor(GREY)
        c.setFont("Times-Italic", 8)
        c.drawCentredString(W / 2, 9 * mm,
                            _clean(f"Compiled for {user['name']}  -  page {doc.page}"))
        c.restoreState()
    return draw

def _frame(x, y, w, h, fid):
    return Frame(x, y, w, h, id=fid, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

def _col_frames(top, prefix):
    return [_frame(M + k * (COL_W + GAP), COL_BOTTOM, COL_W, top - COL_BOTTOM, f"{prefix}{k}")
            for k in range(COLS)]

# ---------- content ----------
def _lead_block(a, why):
    items = [
        Paragraph(f'<link href="{_link(a["url"])}" color="#111111">{_t(a["title"])}</link>', S["lead"]),
        Paragraph(_t(f'{a["source"]}  |  {a["section"]}'), S["meta"]),
        Spacer(1, 4),
        Paragraph(_t(a["summary"]), S["lead_sum"]),
    ]
    if why:
        items.append(Paragraph(_t(why), S["why"]))
    return KeepInFrame(W - 2 * M, LEAD_H, items, mode="shrink")

def _section(name, ids, arts, layout, hidden):
    ids = [i for i in ids if i in arts and i not in hidden]
    if not ids:
        return []
    out = [Paragraph(_t(name.upper()), S["sec"]),
           HRFlowable(width="100%", thickness=0.8, color=INK, spaceAfter=2)]
    for i in ids:
        a = arts[i]
        block = [
            Paragraph(f'<link href="{_link(a["url"])}" color="#111111">{_t(a["title"])}</link>', S["title"]),
            Paragraph(_t(a["source"]), S["meta"]),
            Paragraph(_t(a["summary"]), S["sum"]),
        ]
        why = layout["why"].get(str(i))
        if why:
            block.append(Paragraph(_t(why), S["why"]))
        else:
            block.append(Spacer(1, 5))
        out.append(KeepTogether(block))
    return out

# ---------- public ----------
def build_pdf(user, day, layout, arts, hidden=frozenset()):
    """Return the edition as PDF bytes."""
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=M, bottomMargin=M,
                          title=_clean(f"The {user['name']} Chronicle - {day}"),
                          author="The Daily Brew")

    first_top = H - M - MAST_H - LEAD_H - 4 * mm
    later_top = H - M - 12 * mm
    lead_frame = _frame(M, H - M - MAST_H - LEAD_H, W - 2 * M, LEAD_H, "lead")

    doc.addPageTemplates([
        PageTemplate(id="first", frames=[lead_frame] + _col_frames(first_top, "f"),
                     onPage=_decor(user, day, True, first_top)),
        PageTemplate(id="later", frames=_col_frames(later_top, "l"),
                     onPage=_decor(user, day, False, later_top)),
    ])

    story = [NextPageTemplate("later")]
    lead = layout["lead"]
    if lead in arts and lead not in hidden:
        story.append(_lead_block(arts[lead], layout["why"].get(str(lead), "")))
    story.append(FrameBreak())                      # jump from lead box to column 1

    story += _section("Front Page", [i for i in layout["front"] if i != lead],
                      arts, layout, hidden)
    for name in layout["section_order"]:
        story += _section(name, layout["sections"][name], arts, layout, hidden)

    doc.build(story)
    return buf.getvalue()