"""Slide 3: salaries & wages per student iso-line chart."""
import math
import numpy as np
from nu_helpers import *
import overlay_labels as OL

FRAME_BOTTOM = 6.02
ISO_LEVELS = [40, 80, 120, 160, 200, 240, 280, 320, 400, 480, 560]   # $K of S&W per student
XMIN, XSTEP = 0, 10_000
YMIN, YMAX = 0.20, 0.70      # y axis range (S&W share of core operating expenses)


def fmt_k(v): return f"${v/1000:,.0f}K"


def build_slide3(prs, rows, fy_label, title, subtitle, notes_paras, source, draft_tag=None, notes_text=None,
                 focus=None, health_system=(), xmax=None, frame_bottom=FRAME_BOTTOM, iso_levels=ISO_LEVELS, foot_marks=None, hints=None, ymin=YMIN, ymax=YMAX, extend=True):   # extend: draw each iso-line to the right edge with true values; the chart clips at the axis limits (LibreOffice drops series that stop short of the edge)
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
    il, iw = 0.90, 11.55         # iso-line labels run along the top edge, so no right-hand label margin is needed
    it, ih = 0.28, fh - 0.28 - 0.72   # top inset leaves room for the iso-line labels above the plot
    IL, IT = fx + il, fy + it
    def X(v): return IL + (v - XMIN) / (xmax - XMIN) * iw
    def Y(v): return IT + (ymax - v) / (ymax - ymin) * ih

    cd = XyChartData()
    iso_series = []
    iso_levels = [L for L in iso_levels if L * 1000 / ymax <= xmax]      # every line must enter the plot through the top edge
    for L in iso_levels:
        s = cd.add_series(f"${L}K S&W per student iso-line")
        x0, x1 = L * 1000 / ymax, (float(xmax) if extend else min(float(xmax), L * 1000 / ymin))      # enters at the top (ymax); leaves at the floor (ymin) or the right edge
        xs = [x0]
        x = XSTEP
        while x < x1:
            if x > x0 + 1: xs.append(float(x))
            x += XSTEP
        xs.append(x1)
        for x in xs:
            s.add_data_point(x, min(ymax, L * 1000 / x) if extend else max(ymin, min(ymax, L * 1000 / x)))
        iso_series.append(L)
    ordered = sorted(rows, key=lambda r: r["x"])
    others = [r for r in ordered if r["name"] != focus]
    est = [r for r in others if r.get("basis") == "est"]
    grp_health = [r for r in others if r["name"] in health_system and r.get("basis") != "est"]
    grp_plain = [r for r in others if r["name"] not in health_system and r.get("basis") != "est"]
    # marker groups: black = no health system; royal blue = consolidates a health system; light blue = health system with estimated S&W
    groups = [(n, g_, c) for n, g_, c in (("Institutions", grp_plain, BLACK), ("Health system consolidated", grp_health, ROYAL),
                                         ("Health system consolidated, S&W estimated", est, LIGHT_BLUE)) if g_]
    for n, g_, c in groups:
        s_ = cd.add_series(n)
        for r in g_: s_.add_data_point(r["x"], r["y"])
    if focus:
        s_foc = cd.add_series(focus)
        fr = next(r for r in rows if r["name"] == focus)
        s_foc.add_data_point(fr["x"], fr["y"])

    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, Inches(fx), Inches(fy), Inches(fw), Inches(fh), cd)
    gf.name = "S&W per student iso-line chart"
    set_alt_text(gf, f"Scatter chart of {fy_label} core operating expense per student (x) against salaries and wages as a share of core operating expenses (y) "
                     f"for {len(rows)} universities, with dashed iso-lines of constant salaries and wages per student from ${iso_levels[0]}K to ${iso_levels[-1]}K; the y axis runs from {ymin:.0%} to {ymax:.0%}. Universities that consolidate a health system are blue; Northeastern is red.")
    ch = gf.chart
    chart_frame_style(ch, 9)
    ch.has_legend = False
    set_plot_layout(ch, il / fw, it / fh, iw / fw, ih / fh)
    plot = ch.plots[0]; plot.vary_by_categories = False
    style_axis(ch.category_axis, XMIN, xmax, 100_000, '"$"#,##0,"K"', grid=False, size=9)
    style_axis(ch.value_axis, ymin, ymax, 0.1, '0%', grid=True, grid_color="E4E4E6", size=9)
    axis_title(ch.category_axis, [("Core unlevered cash operating expenses (excluding depreciation, amortization and interest) per student ($K)", {})], size=10)
    axis_title(ch.value_axis, [("S&W as % of core operating expenses", {})], size=10, rot=-5400000)

    n_iso = len(iso_levels)
    for ser, L in zip(list(plot.series)[:n_iso], iso_series):
        series_line(ser, GREY, 1.0, dash="dash")
        ser.marker.style = XL_MARKER_STYLE.NONE
        set_label(ser.points[0], [[(f"${L}K", dict(color=MUTED, size=8.5, italic=True))]], XL_LABEL_POSITION.ABOVE, 8.5)   # top-edge entry point
        series_labels_off(ser)
    MS_DOT, MS_FOC = 9, 13          # marker sizes (points)
    nxt = n_iso
    for n, g_, c in groups:
        sg = plot.series[nxt]; nxt += 1
        style_series_markers(sg, c, MS_DOT); series_no_line(sg)
    if focus:
        sf = plot.series[nxt]
        style_series_markers(sf, RED, MS_FOC, line_color=WHITE, line_w=1.25); series_no_line(sf)

    # ---------------- institution labels (annotation layer)
    items, spec, pts = {}, {}, {}
    for r in rows:
        px, py = X(r["x"]), Y(r["y"])
        nm = r["name"] + (" (1)" if r["name"] in health_system else "") + ((foot_marks or {}).get(r["name"], ""))
        l2 = f"{fmt_k(r['swps'])}{' est.' if r.get('basis') == 'est' else ''} · {r['students']:,} students"
        is_f = (focus == r["name"])
        w = max(text_width_in(nm, 10 if is_f else 9, bold=True), text_width_in(l2, 8)) + 0.10
        items[r["name"]] = dict(px=px, py=py, w=w, h=0.33, ms=0.125 if not is_f else 0.18, max_r=(0.5 if is_f else 9))
        pts[r["name"]] = (px, py)
        col = RED if is_f else BLACK
        spec[r["name"]] = dict(paras=[[(nm, dict(bold=True, size=10 if is_f else 9, color=col))], [(l2, dict(size=8, color=MUTED if not is_f else RED))]],
                               px=px, py=py, leader_color=col, alpha=80, size=9)
    for k, it_ in items.items():
        near = [k2 for k2, (mx, my) in pts.items() if k2 != k and math.hypot(mx - it_['px'], my - it_['py']) < 0.16]
        it_['min_r'] = 0.30 if near else 0.16      # every label sits off its marker and is tied to it by a leader line
    for k, h in (hints or {}).items():      # per-label placement hints, e.g. {'Harvard': dict(dirs=[(0, 1)], max_r=0.45)}
        if k in items: items[k].update(h)
    bounds = (IL + 0.02, IT + 0.02, IL + iw - 0.02, IT + ih - 0.02)
    if focus and focus in items:        # focus label: below and to the left of its marker, clear of the neighbours' leaders
        fx_, fy_ = pts[focus]; fw_, fh_ = items[focus]["w"], items[focus]["h"]
        items[focus].update(dirs=[], extra=[(bounds[0] + sx, fy_ + dy, fw_, fh_) for dy in (0.30, 0.40, 0.52) for sx in (0.0, 0.06, 0.12)])
    RADII_ALL = [(0.06, 0.0), (0.22, 0.6), (0.42, 1.4), (0.65, 2.5), (0.95, 4.0), (1.3, 6.0)]
    if focus and focus in items:
        fi = {focus: dict(items[focus], max_r=9, min_r=0.20)}
        pf = OL.place(fi, np.zeros((0, 2)), bounds, fixed=[], marker_pts=pts, ms=0.11, marker_clear=0.13, allowed_radii=RADII_ALL)
        rest = {k: v for k, v in items.items() if k != focus}
        po = OL.place(rest, np.zeros((0, 2)), bounds, fixed=[OL.infl(pf[focus][0], 0.02)], marker_pts=pts, ms=0.11, marker_clear=0.10, allowed_radii=RADII_ALL)
        placed = dict(po); placed[focus] = pf[focus]
    else:
        placed = OL.place(items, np.zeros((0, 2)), bounds, fixed=[], marker_pts=pts, ms=0.11, marker_clear=0.10, allowed_radii=RADII_ALL)
    OL.draw_labels(slide, placed, spec, marker_r=0.055)
    add_legend_row(slide, [("dot", BLACK, "No health system", {"d": 0.115}), ("dot", ROYAL, "Health system consolidated (1)", {"d": 0.115}),
                           ("dot", LIGHT_BLUE, "Health system, S&W estimated (1) (4)", {"d": 0.115}), ("dot", RED, "Northeastern", {"d": 0.16})],
                   x_right=IL + iw, y=top + 0.03, size=9.5)
    cap_x = X(iso_levels[-1] * 1000 / ymax) + 0.42
    add_textbox(slide, cap_x, IT - 0.235, 2.3, 0.2, [[("S&W per student", {"bold": True}), (" (dashed iso-lines)", {})]],
                size=8.5, color=MUTED, wrap=False, name="Iso-line caption")
    blocks = [None] * n_iso + [[r["name"] for r in g_] for n, g_, c in groups] + ([[focus]] if focus else [])
    write_names_to_workbook(ch, blocks)
    annotate_workbook(ch, {"E1": "Reading guide: column A = core operating expense per student ($); column B = S&W as share of core operating expense; column C = institution. Iso-line blocks: S&W per student = A x B = constant."})
    return slide, ch, dict(xmax=xmax, costs={k: v[2] for k, v in placed.items()}, rows=rows)
