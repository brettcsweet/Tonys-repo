"""Slide 3: salaries & wages per student iso-line chart."""
import math
import numpy as np
from nu_helpers import *
import overlay_labels as OL

FRAME_BOTTOM = 6.02
ISO_LEVELS = [40, 80, 120, 160, 200, 240, 280, 320]   # $K of S&W per student
XMIN, XSTEP = 0, 10_000


def fmt_k(v): return f"${v/1000:,.0f}K"


def build_slide3(prs, rows, fy_label, title, subtitle, notes_paras, source, draft_tag=None, notes_text=None,
                 focus=None, health_system=(), xmax=None, frame_bottom=FRAME_BOTTOM, iso_levels=ISO_LEVELS):
    """rows: list of dict(name, sw, opex, students). SW/student, opex/student, SW% are derived here."""
    for r in rows:
        r["x"] = r["opex"] / r["students"]
        r["y"] = r["sw"] / r["opex"]
        r["swps"] = r["sw"] / r["students"]
    xmax = xmax or int(math.ceil(max(r["x"] for r in rows) * 1.03 / 100_000) * 100_000)
    slide, top = new_slide(prs, title, subtitle, notes_paras, source, draft_tag, notes_text)

    fx, fw = 0.35, 12.65
    add_textbox(slide, 0.84, top, 8.0, 0.26, f"{fy_label} salaries and wages per student", size=13, bold=True, name="Chart heading")
    fy = top + 0.32
    fh = frame_bottom - fy
    il, iw = 0.90, 10.75
    it, ih = 0.06, fh - 0.06 - 0.72
    IL, IT = fx + il, fy + it
    def X(v): return IL + (v - XMIN) / (xmax - XMIN) * iw
    def Y(v): return IT + (1 - v / 0.8) * ih

    cd = XyChartData()
    iso_series = []
    for L in iso_levels:
        s = cd.add_series(f"${L}K S&W per student iso-line")
        xs = [L * 1000 / 0.8]                       # where the line enters the 80% ceiling
        x = XSTEP
        while x <= xmax:
            if x > xs[0] + 1: xs.append(float(x))
            x += XSTEP
        if xs[-1] < xmax: xs.append(float(xmax))
        for x in xs:
            s.add_data_point(x, min(0.8, L * 1000 / x))
        iso_series.append(L)
    s_inst = cd.add_series("Institutions")
    ordered = sorted(rows, key=lambda r: r["x"])
    for r in ordered: s_inst.add_data_point(r["x"], r["y"])
    if focus:
        s_foc = cd.add_series(focus)
        fr = next(r for r in rows if r["name"] == focus)
        s_foc.add_data_point(fr["x"], fr["y"])

    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, Inches(fx), Inches(fy), Inches(fw), Inches(fh), cd)
    gf.name = "S&W per student iso-line chart"
    set_alt_text(gf, f"Scatter chart of {fy_label} core operating expense per student (x) against salaries and wages as a share of core operating expenses (y) "
                     f"for {len(rows)} universities, with dashed iso-lines of constant salaries and wages per student from $40K to $320K.")
    ch = gf.chart
    chart_frame_style(ch, 9)
    ch.has_legend = False
    set_plot_layout(ch, il / fw, it / fh, iw / fw, ih / fh)
    plot = ch.plots[0]; plot.vary_by_categories = False
    style_axis(ch.category_axis, XMIN, xmax, 100_000, '"$"#,##0,"K"', grid=False, size=9)
    style_axis(ch.value_axis, 0, 0.8, 0.1, '0%', grid=True, grid_color="E4E4E6", size=9)
    axis_title(ch.category_axis, [("Core unlevered cash operating expenses (excluding depreciation, amortization and interest) per student ($K)", {})], size=10)
    axis_title(ch.value_axis, [("S&W as % of core operating expenses", {})], size=10, rot=-5400000)

    n_iso = len(iso_levels)
    for ser, L in zip(list(plot.series)[:n_iso], iso_series):
        series_line(ser, GREY, 1.0, dash="dash")
        ser.marker.style = XL_MARKER_STYLE.NONE
        last = len(ser.values) - 1
        set_label(ser.points[last], [[(f"${L}K", dict(color=MUTED, size=8.5, italic=True))]], XL_LABEL_POSITION.RIGHT, 8.5)
        series_labels_off(ser)
    si = plot.series[n_iso]
    style_series_markers(si, BLACK, 8); series_no_line(si)
    if focus:
        sf = plot.series[n_iso + 1]
        style_series_markers(sf, RED, 12, line_color=WHITE, line_w=1.25); series_no_line(sf)

    # ---------------- institution labels (annotation layer)
    items, spec, pts = {}, {}, {}
    for r in rows:
        px, py = X(r["x"]), Y(r["y"])
        nm = r["name"] + (" (1)" if r["name"] in health_system else "")
        l2 = f"{fmt_k(r['swps'])} · {r['students']:,} students"
        is_f = (focus == r["name"])
        w = max(text_width_in(nm, 10 if is_f else 9, bold=True), text_width_in(l2, 8)) + 0.10
        items[r["name"]] = dict(px=px, py=py, w=w, h=0.33, ms=0.11 if not is_f else 0.17, max_r=(0.5 if is_f else 9))
        pts[r["name"]] = (px, py)
        col = RED if is_f else BLACK
        spec[r["name"]] = dict(paras=[[(nm, dict(bold=True, size=10 if is_f else 9, color=col))], [(l2, dict(size=8, color=MUTED if not is_f else RED))]],
                               px=px, py=py, leader_color=col, alpha=80, size=9)
    for k, it_ in items.items():
        near = [k2 for k2, (mx, my) in pts.items() if k2 != k and math.hypot(mx - it_['px'], my - it_['py']) < 0.16]
        if near: it_['min_r'] = 0.30
    bounds = (IL + 0.02, IT + 0.02, IL + iw - 0.02, IT + ih - 0.02)
    caption_box = (IL + iw + 0.05, Y(0.8) - 0.05, 1.25, 0.34)
    placed = OL.place(items, np.zeros((0, 2)), bounds, fixed=[], marker_pts=pts, ms=0.11,
                      allowed_radii=[(0.06, 0.0), (0.22, 0.6), (0.42, 1.4), (0.65, 2.5), (0.95, 4.0)])
    OL.draw_labels(slide, placed, spec, marker_r=0.055)
    add_textbox(slide, IL + iw + 0.07, Y(0.8), 1.2, 0.34, [[("S&W per student", {"bold": True})], [("iso-lines", {})]],
                size=8.5, color=MUTED, name="Iso-line caption")
    blocks = [None] * n_iso + [[r["name"] for r in ordered]] + ([[focus]] if focus else [])
    write_names_to_workbook(ch, blocks)
    annotate_workbook(ch, {"E1": "Reading guide: column A = core operating expense per student ($); column B = S&W as share of core operating expense; column C = institution. Iso-line blocks: S&W per student = A x B = constant."})
    return slide, ch, dict(xmax=xmax, costs={k: v[2] for k, v in placed.items()}, rows=rows)
