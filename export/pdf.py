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

PDF_PALETTES = {
    "classic":   {"paper": "#f6f0e1", "ink": "#111111", "accent": "#8b1a1a", "grey": "#555555", "rule": "#999999"},
    "dark":      {"paper": "#f4f6fa", "ink": "#0f172a", "accent": "#0284c7", "grey": "#64748b", "rule": "#cbd5e1"},
    "financial": {"paper": "#fbf0e4", "ink": "#0f1d2e", "accent": "#990000", "grey": "#475569", "rule": "#d4b89e"},
    "espresso":  {"paper": "#fbf8f1", "ink": "#2b1e16", "accent": "#b45309", "grey": "#6b5c52", "rule": "#d1bead"},
    "nordic":    {"paper": "#ffffff", "ink": "#0f172a", "accent": "#059669", "grey": "#64748b", "rule": "#e2e8f0"},
    "cyber":     {"paper": "#ffffff", "ink": "#0f172a", "accent": "#059669", "grey": "#475569", "rule": "#d1d5db"},
}

def _get_styles(palette):
    accent_c = colors.HexColor(palette["accent"])
    grey_c = colors.HexColor(palette["grey"])
    ink_c = colors.HexColor(palette["ink"])
    
    return {
        "lead":     ParagraphStyle("lead", fontName="Times-Bold", fontSize=26, leading=28, spaceAfter=4, textColor=ink_c),
        "lead_sum": ParagraphStyle("lead_sum", fontName="Times-Roman", fontSize=12, leading=15, spaceAfter=4, textColor=ink_c),
        "sec":      ParagraphStyle("sec", fontName="Times-Bold", fontSize=9, leading=11,
                                   textColor=accent_c, spaceBefore=8, spaceAfter=2),
        "title":    ParagraphStyle("title", fontName="Times-Bold", fontSize=12, leading=13.5,
                                   spaceBefore=4, spaceAfter=2, textColor=ink_c),
        "sum":      ParagraphStyle("sum", fontName="Times-Roman", fontSize=9, leading=11.5, textColor=ink_c),
        "meta":     ParagraphStyle("meta", fontName="Times-Italic", fontSize=7.5, leading=9, textColor=grey_c),
        "why":      ParagraphStyle("why", fontName="Times-Italic", fontSize=7.5, leading=9,
                                   textColor=accent_c, spaceAfter=5),
    }

def _clean(s):
    """Built-in PDF fonts only support Latin text, so drop emoji and other scripts."""
    return (s or "").encode("cp1252", "ignore").decode("cp1252")

def _t(s):
    return escape(_clean(s))

def _link(url):
    return escape(url or "", {'"': "&quot;"})

# ---------- page decoration ----------
def _decor(user, day, first, col_top, palette):
    interests = user.get("interests", {})
    focus = max(interests, key=interests.get) if interests else "General"
    title = _clean("THE DAILY BREW")
    nice = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y").upper()
    dateline = _clean(f"{nice}   |   {focus.upper()} EDITION   |   {user['persona'].upper()}")

    paper_c = colors.HexColor(palette["paper"])
    ink_c = colors.HexColor(palette["ink"])
    grey_c = colors.HexColor(palette["grey"])
    rule_c = colors.HexColor(palette["rule"])

    def draw(c, doc):
        c.saveState()
        c.setFillColor(paper_c)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(ink_c)
        c.setStrokeColor(ink_c)
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
        c.setStrokeColor(rule_c)
        c.setLineWidth(0.3)
        for k in range(1, COLS):
            x = M + k * (COL_W + GAP) - GAP / 2
            c.line(x, COL_BOTTOM, x, col_top)

        # footer
        c.setFillColor(grey_c)
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
def _lead_block(a, why, styles, link_color="#111111"):
    items = [
        Paragraph(f'<link href="{_link(a["url"])}" color="{link_color}">{_t(a["title"])}</link>', styles["lead"]),
        Paragraph(_t(f'{a["source"]}  |  {a["section"]}'), styles["meta"]),
        Spacer(1, 4),
        Paragraph(_t(a["summary"]), styles["lead_sum"]),
    ]
    if why:
        items.append(Paragraph(_t(why), styles["why"]))
    return KeepInFrame(W - 2 * M, LEAD_H, items, mode="shrink")

def _section(name, ids, arts, layout, hidden, styles, rule_color="#111111"):
    ids = [i for i in ids if i in arts and i not in hidden]
    if not ids:
        return []
    out = [Paragraph(_t(name.upper()), styles["sec"]),
           HRFlowable(width="100%", thickness=0.8, color=colors.HexColor(rule_color), spaceAfter=2)]
    for i in ids:
        a = arts[i]
        block = [
            Paragraph(f'<link href="{_link(a["url"])}" color="{rule_color}">{_t(a["title"])}</link>', styles["title"]),
            Paragraph(_t(a["source"]), styles["meta"]),
            Paragraph(_t(a["summary"]), styles["sum"]),
        ]
        why = layout["why"].get(str(i))
        if why:
            block.append(Paragraph(_t(why), styles["why"]))
        else:
            block.append(Spacer(1, 5))
        out.append(KeepTogether(block))
    return out

# ---------- public ----------
_PDF_CACHE = {}

def build_pdf(user, day, layout, arts, hidden=frozenset()):
    """Return the edition as PDF bytes matching user's theme palette."""
    cache_key = f"{user['id']}_{day}_{user.get('theme', 'classic')}_{len(hidden)}"
    if cache_key in _PDF_CACHE:
        return _PDF_CACHE[cache_key]

    user_theme = user.get("theme", "classic")
    palette = PDF_PALETTES.get(user_theme, PDF_PALETTES["classic"])
    styles = _get_styles(palette)
    
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=M, bottomMargin=M,
                          title=_clean(f"The Daily Brew - {day}"),
                          author="The Daily Brew")

    first_top = H - M - MAST_H - LEAD_H - 4 * mm
    later_top = H - M - 12 * mm
    lead_frame = _frame(M, H - M - MAST_H - LEAD_H, W - 2 * M, LEAD_H, "lead")

    doc.addPageTemplates([
        PageTemplate(id="first", frames=[lead_frame] + _col_frames(first_top, "f"),
                     onPage=_decor(user, day, True, first_top, palette)),
        PageTemplate(id="later", frames=_col_frames(later_top, "l"),
                     onPage=_decor(user, day, False, later_top, palette)),
    ])

    story = [NextPageTemplate("later")]
    lead = layout["lead"]
    if lead in arts and lead not in hidden:
        story.append(_lead_block(arts[lead], layout["why"].get(str(lead), ""), styles, palette["ink"]))
    story.append(FrameBreak())                      # jump from lead box to column 1

    story += _section("Front Page", [i for i in layout["front"] if i != lead],
                      arts, layout, hidden, styles, palette["ink"])
    for name in layout["section_order"]:
        story += _section(name, layout["sections"][name], arts, layout, hidden, styles, palette["ink"])

    doc.build(story)
    res = buf.getvalue()
    _PDF_CACHE[cache_key] = res
    return res