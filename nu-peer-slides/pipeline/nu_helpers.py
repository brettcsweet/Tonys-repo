"""Shared helpers for the Northeastern rebrand build (python-pptx + raw chart XML)."""
import copy, io, math
from lxml import etree
from pptx import Presentation
from pptx.chart.data import XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_MARKER_STYLE, XL_TICK_MARK
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu
from PIL import ImageFont

# ------------------------------------------------------------------ brand
RED = "C8102E"
BLACK = "000000"
WHITE = "FFFFFF"
GRAPHITE = "3A3A3F"
GREY = "8A8D8F"        # Husky Grey
MUTED = "6B6B70"
NAVY = "0C3354"        # navy from the NU template theme; used for private institutions per Brett
GRID = "D9D9DB"
FONT = "Lato"

NS = {
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
C = "{%s}" % NS["c"]
A = "{%s}" % NS["a"]

def rgb(h): return RGBColor.from_string(h)

# ------------------------------------------------------------------ fonts for label measurement
_FP = "/usr/share/fonts/truetype/lato/"
_FONTS = {}
def text_width_in(text, size_pt, bold=False, italic=False):
    key = (bold, italic)
    if key not in _FONTS:
        name = "Lato-" + ("BoldItalic" if bold and italic else "Bold" if bold else "Italic" if italic else "Regular") + ".ttf"
        _FONTS[key] = ImageFont.truetype(_FP + name, 200)
    return _FONTS[key].getlength(text) / 200.0 * size_pt / 72.0

# ------------------------------------------------------------------ deck scaffolding
def open_base(path):
    prs = Presentation(path)
    lst = prs.slides._sldIdLst
    for sldId in list(lst):
        prs.part.drop_rel(sldId.rId)
        lst.remove(sldId)
    return prs

def layout_by_name(prs, name):
    return [l for l in prs.slide_layouts if l.name == name][0]

def _fill_placeholder(ph, paras, size=None):
    """paras: list of paragraphs; each paragraph = list of (text, {opts}) runs or plain string."""
    tf = ph.text_frame
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        runs = [(para, {})] if isinstance(para, str) else para
        for text, o in runs:
            r = p.add_run()
            r.text = text
            if o.get("sup"):
                r.font._element.set("baseline", "30000")
            if o.get("bold") is not None: r.font.bold = o["bold"]
            if o.get("italic") is not None: r.font.italic = o["italic"]
            if size: r.font.size = Pt(size)

def title_lines(title, size_pt=24, width_in=12.0):
    return 1 if text_width_in(title, size_pt, bold=True) <= width_in * 0.97 else 2

def new_slide(prs, title, subtitle, notes_paras, source, draft_tag=None, notes_text=None):
    """returns (slide, content_top_in)."""
    s = prs.slides.add_slide(layout_by_name(prs, "NU chart slide"))
    s.shapes.title.text_frame.text = title
    nl = title_lines(title)
    sub = s.placeholders[13]
    if nl == 1:
        sub.left, sub.top, sub.width, sub.height = Inches(0.84), Inches(0.80), Inches(12.0), Inches(0.34)
        content_top = 1.32
    else:
        content_top = 1.62
    _fill_placeholder(sub, [subtitle] if isinstance(subtitle, str) else subtitle)
    _fill_placeholder(s.placeholders[14], notes_paras)
    _fill_placeholder(s.placeholders[15], [source])
    if draft_tag:
        tb = s.shapes.add_textbox(Inches(8.2), Inches(0.10), Inches(4.63), Inches(0.22))
        tb.name = "Draft tag"
        tf = tb.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
        r = p.add_run(); r.text = draft_tag
        r.font.size = Pt(8); r.font.bold = True; r.font.name = FONT; r.font.color.rgb = rgb(RED)
    add_slide_number(s)
    if notes_text:
        s.notes_slide.notes_text_frame.text = notes_text
    return s, content_top

def add_textbox(slide, x, y, w, h, paras, size=9, color=BLACK, bold=False, italic=False, align="l",
                anchor="t", rot=0, fill=None, name=None, font=FONT, wrap=True, fill_alpha=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str): paras = [paras]
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        runs = [(para, {})] if isinstance(para, str) else para
        for text, o in runs:
            r = p.add_run(); r.text = text
            f = r.font
            f.size = Pt(o.get("size", size)); f.name = o.get("font", font)
            f.bold = o.get("bold", bold); f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            if o.get("sup"): f._element.set("baseline", "30000")
    if rot: tb.rotation = rot
    if fill:
        tb.fill.solid(); tb.fill.fore_color.rgb = rgb(fill)
        if fill_alpha is not None:
            clr = tb.fill._xPr.find(A + "solidFill").find(A + "srgbClr")
            a = etree.SubElement(clr, A + "alpha"); a.set("val", str(int(fill_alpha * 1000)))
    return tb

def add_line(slide, x1, y1, x2, y2, color=GREY, width=0.5, dash=None, name=None):
    ln = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color); ln.line.width = Pt(width)
    if dash:
        lnEl = ln.line._get_or_add_ln()
        d = etree.SubElement(lnEl, A + "prstDash"); d.set("val", dash)
    if name: ln.name = name
    return ln

# ------------------------------------------------------------------ chart XML helpers
def cs(chart):  # chartSpace element
    return chart._chartSpace

def chart_frame_style(chart, font_size=9):
    """No chart border/fill, Lato text, no title."""
    chart.has_title = False
    chart.font.name = FONT
    chart.font.size = Pt(font_size)
    chart.font.color.rgb = rgb(BLACK)
    root = cs(chart)
    # round corners off
    rc = root.find(C + "roundedCorners")
    if rc is None:
        rc = etree.Element(C + "roundedCorners")
        root.insert(0, rc)
    rc.set("val", "0")
    spPr = root.find(C + "spPr")
    if spPr is None:
        spPr = etree.Element(C + "spPr")
        root.find(C + "chart").addnext(spPr)
    for ch in list(spPr): spPr.remove(ch)
    etree.SubElement(spPr, A + "noFill")
    ln = etree.SubElement(spPr, A + "ln"); etree.SubElement(ln, A + "noFill")

def set_plot_layout(chart, x, y, w, h):
    """inner plot area as fractions of the chart frame."""
    pa = cs(chart).find(C + "chart").find(C + "plotArea")
    old = pa.find(C + "layout")
    if old is not None: pa.remove(old)
    lay = etree.Element(C + "layout")
    ml = etree.SubElement(lay, C + "manualLayout")
    for tag, val in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"),
                     ("x", x), ("y", y), ("w", w), ("h", h)):
        e = etree.SubElement(ml, C + tag); e.set("val", str(val))
    pa.insert(0, lay)

def style_axis(axis, minv, maxv, major, numfmt, grid=True, line_color=BLACK, size=9, grid_color=GRID,
               tick_color=BLACK, grid_dash=None):
    axis.minimum_scale = minv; axis.maximum_scale = maxv; axis.major_unit = major
    axis.has_major_gridlines = grid
    if grid:
        gl = axis.major_gridlines.format.line
        gl.color.rgb = rgb(grid_color); gl.width = Pt(0.5)
        if grid_dash:
            d = etree.SubElement(gl._get_or_add_ln(), A + "prstDash"); d.set("val", grid_dash)
    axis.has_minor_gridlines = False
    axis.major_tick_mark = XL_TICK_MARK.OUTSIDE
    axis.minor_tick_mark = XL_TICK_MARK.NONE
    axis.format.line.color.rgb = rgb(line_color); axis.format.line.width = Pt(0.75)
    tl = axis.tick_labels
    tl.number_format = numfmt; tl.number_format_is_linked = False
    tl.font.size = Pt(size); tl.font.name = FONT; tl.font.color.rgb = rgb(tick_color)

def axis_title(axis, runs, size=10, rot=None):
    """runs: list of (text, {'sup':bool,'bold':bool})"""
    axis.has_title = True
    tf = axis.axis_title.text_frame
    p = tf.paragraphs[0]
    for text, o in runs:
        r = p.add_run(); r.text = text
        r.font.size = Pt(size); r.font.bold = o.get("bold", True); r.font.name = FONT
        r.font.color.rgb = rgb(BLACK)
        if o.get("sup"): r.font._element.set("baseline", "30000")
    if rot is not None:
        bp = axis.axis_title._element.find(".//" + A + "bodyPr")
        bp.set("rot", str(rot)); bp.set("vert", "horz")
    ov = axis.axis_title._element.find(C + "overlay")
    if ov is None:
        ov = etree.SubElement(axis.axis_title._element, C + "overlay")
    ov.set("val", "0")

def style_series_markers(series, color, size, style=XL_MARKER_STYLE.CIRCLE, alpha=None, line_color=None, line_w=0.75):
    m = series.marker
    m.style = style; m.size = size
    m.format.fill.solid(); m.format.fill.fore_color.rgb = rgb(color)
    if alpha is not None:
        clr = m.format.fill._xPr.find(A + "solidFill").find(A + "srgbClr")
        a = etree.SubElement(clr, A + "alpha"); a.set("val", str(int(alpha * 1000)))
    if line_color:
        m.format.line.color.rgb = rgb(line_color); m.format.line.width = Pt(line_w)
    else:
        m.format.line.fill.background()

def series_no_line(series):
    series.format.line.fill.background()

def series_line(series, color, width=1.0, dash=None):
    series.format.line.color.rgb = rgb(color); series.format.line.width = Pt(width)
    if dash:
        d = etree.SubElement(series.format.line._get_or_add_ln(), A + "prstDash"); d.set("val", dash)
    series.smooth = False

def set_label(point, runs_by_par, position, size=8):
    """custom rich-text data label. runs_by_par: list of paragraphs, each a list of (text, opts)."""
    dl = point.data_label
    tf = dl.text_frame
    first = True
    for para in runs_by_par:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        for text, o in para:
            r = p.add_run(); r.text = text
            f = r.font
            f.size = Pt(o.get("size", size)); f.name = FONT
            f.bold = o.get("bold", False); f.italic = o.get("italic", False)
            f.color.rgb = rgb(o.get("color", BLACK))
            if o.get("sup"): f._element.set("baseline", "30000")
    dl.position = position

def series_labels_off(series):
    """series-level default: show nothing (only explicit per-point labels show)."""
    dls = series._element.find(C + "dLbls")
    if dls is None: return
    for tag in ("showLegendKey", "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
        e = dls.find(C + tag)
        if e is None:
            e = etree.SubElement(dls, C + tag)
        e.set("val", "0")
    sl = dls.find(C + "showLeaderLines")
    if sl is not None: dls.remove(sl)

def add_trendline(series, name, color=BLACK, width=1.25):
    ser = series._element
    tl = etree.Element(C + "trendline")
    n = etree.SubElement(tl, C + "name"); n.text = name
    sp = etree.SubElement(tl, C + "spPr")
    ln = etree.SubElement(sp, A + "ln"); ln.set("w", str(int(width * 12700))); ln.set("cap", "rnd")
    sf = etree.SubElement(ln, A + "solidFill"); c = etree.SubElement(sf, A + "srgbClr"); c.set("val", color)
    d = etree.SubElement(ln, A + "prstDash"); d.set("val", "solid")
    t = etree.SubElement(tl, C + "trendlineType"); t.set("val", "linear")
    e = etree.SubElement(tl, C + "dispRSqr"); e.set("val", "0")
    e = etree.SubElement(tl, C + "dispEq"); e.set("val", "0")
    ser.find(C + "xVal").addprevious(tl)

def legend_style(chart, delete_idx=(), pos=None, size=9, manual=None):
    chart.has_legend = True
    lg = chart.legend
    lg.position = pos or XL_LEGEND_POSITION.TOP
    lg.include_in_layout = False
    lg.font.size = Pt(size); lg.font.name = FONT; lg.font.color.rgb = rgb(BLACK)
    el = lg._element
    lp = el.find(C + "legendPos")
    for i in delete_idx:
        le = etree.Element(C + "legendEntry")
        ix = etree.SubElement(le, C + "idx"); ix.set("val", str(i))
        dl = etree.SubElement(le, C + "delete"); dl.set("val", "1")
        lp.addnext(le)
    if manual:
        old = el.find(C + "layout")
        if old is not None: el.remove(old)
        lay = etree.Element(C + "layout")
        ml = etree.SubElement(lay, C + "manualLayout")
        for tag, val in (("xMode", "edge"), ("yMode", "edge"), ("x", manual[0]), ("y", manual[1]), ("w", manual[2]), ("h", manual[3])):
            e = etree.SubElement(ml, C + tag); e.set("val", str(val))
        # layout goes after legendEntry* and before overlay
        ov = el.find(C + "overlay")
        ov.addprevious(lay)

def set_alt_text(graphic_frame, text):
    graphic_frame._element.xpath(".//p:cNvPr")[0].set("descr", text)

def rewrite_workbook(chart, extra_cols):
    """extra_cols: {series_name: [values...]} -> add a label column right after each series' Y column."""
    import openpyxl
    wbpart = chart.part.chart_workbook
    blob = wbpart.xlsx_part.blob
    wb = openpyxl.load_workbook(io.BytesIO(blob))
    ws = wb.active
    return wb, ws, wbpart


def add_legend_row(slide, items, x_right, y, size=9, gap=0.28, name="Legend"):
    """items: list of (kind, color, label, extra) kind in {'dot','line','ring'}; laid out right-aligned to x_right."""
    widths = []
    for kind, color, label, ex in items:
        sym = 0.14 if kind in ("dot", "ring") else 0.32
        widths.append(sym + 0.07 + text_width_in(label, size) + 0.04)
    total = sum(widths) + gap * (len(items) - 1)
    x = x_right - total
    shapes = []
    for (kind, color, label, ex), w in zip(items, widths):
        sym = 0.14 if kind in ("dot", "ring") else 0.32
        cy = y + 0.10
        if kind == "dot":
            d = ex.get("d", 0.10)
            o = slide.shapes.add_shape(9, Inches(x + (0.14 - d) / 2), Inches(cy - d / 2), Inches(d), Inches(d))
            o.fill.solid(); o.fill.fore_color.rgb = rgb(color); o.line.fill.background()
            shapes.append(o)
        elif kind == "line":
            shapes.append(add_line(slide, x, cy, x + sym, cy, color=color, width=ex.get("w", 1.5)))
        tb = add_textbox(slide, x + sym + 0.07, y, w - sym - 0.07, 0.2, label, size=size, color=BLACK, anchor="m", wrap=False)
        shapes.append(tb)
        x += w + gap
    for sh in shapes: sh.name = name
    return total

def write_names_to_workbook(chart, blocks):
    """blocks: list of lists of names, one per series in order; adds an 'Institution' column (C) to the embedded workbook."""
    import openpyxl
    wbpart = chart.part.chart_workbook
    wb = openpyxl.load_workbook(io.BytesIO(wbpart.xlsx_part.blob))
    ws = wb.active
    # locate series header rows: rows whose column A is empty and B has text
    header_rows = [r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value is None and ws.cell(r, 2).value is not None]
    assert len(header_rows) >= len(blocks), (header_rows, len(blocks))
    for hr, names in zip(header_rows, blocks):
        if names is None: continue
        ws.cell(hr, 3).value = "Institution"
        for i, nm in enumerate(names):
            ws.cell(hr + 1 + i, 3).value = nm
    bio = io.BytesIO(); wb.save(bio)
    wbpart.update_from_xlsx_blob(bio.getvalue())


def annotate_workbook(chart, notes):
    """notes: {'E1': 'text', ...} written into the embedded workbook (reading guide for 'Edit Data')."""
    import openpyxl
    wbpart = chart.part.chart_workbook
    wb = openpyxl.load_workbook(io.BytesIO(wbpart.xlsx_part.blob))
    ws = wb.active
    for addr, txt in notes.items(): ws[addr].value = txt
    bio = io.BytesIO(); wb.save(bio)
    wbpart.update_from_xlsx_blob(bio.getvalue())


def add_slide_number(slide):
    """Instantiate the layout's slide-number placeholder on the slide (python-pptx does not copy it)."""
    spTree = slide.shapes._spTree
    ids = [int(x) for x in spTree.xpath(".//p:cNvPr/@id")]
    nid = max(ids) + 1
    xml = (
        '<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:nvSpPr><p:cNvPr id="{nid}" name="Slide Number Placeholder"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr><p:spPr/>'
        '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum">'
        '<a:rPr lang="en-US"/><a:t>\u2039#\u203a</a:t></a:fld><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>')
    spTree.append(etree.fromstring(xml))
