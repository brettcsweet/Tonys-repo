"""Slide 2: Inside Higher Ed business-officer survey - are groups 'realistic and aware of the financial challenges'."""
from nu_helpers import *

FRAME_BOTTOM = 6.02
LBL_W, LBL_H = 0.42, 0.17
MARK_R = {"F": 0.09, "T": 0.105, "S": 0.065}


def build_slide2(prs, data, years, title, subtitle, notes_paras, source, draft_tag=None, notes_text=None, frame_bottom=FRAME_BOTTOM,
                 statement="are aware of and understand the financial challenges confronting my institution", scale_note=None,
                 extra_label=None, star_years=None):
    """data = {'F': {year: pct}, 'T': {...}, 'S': {...}}; years = ordered list to plot."""
    slide, top = new_slide(prs, title, subtitle, notes_paras, source, draft_tag, notes_text)
    x0 = 0.84
    add_textbox(slide, x0, top, 12.0, 0.30,
                [[("_____ ", {"bold": True, "italic": True}),
                  (statement, {"bold": True, "italic": True})]],
                size=16, color=BLACK, name="Statement")
    add_textbox(slide, x0, top + 0.32, 12.0, 0.22,
                scale_note or "(percent of business officers answering 4 or 5 on a five-point scale, with 5 = strongly agree and 1 = strongly disagree)",
                size=10.5, color=MUTED, italic=True, name="Scale note")

    # legend row (drawn) - left aligned under the statement
    leg_y = top + 0.62
    lx = x0
    legend_items = [("Faculty", "F"), ("Trustees", "T"), ("Sr. Administrators", "S")]
    if data.get("T2"): legend_items.append((extra_label or "Trustees only (different item)", "T2"))
    for label, kind in legend_items:
        if kind == "F":
            o = slide.shapes.add_shape(9, Inches(lx), Inches(leg_y + 0.03), Inches(0.14), Inches(0.14))
            o.fill.solid(); o.fill.fore_color.rgb = rgb(RED); o.line.fill.background()
        elif kind in ("T", "T2"):
            d_ = 0.16 if kind == "T" else 0.12
            o = slide.shapes.add_shape(9, Inches(lx + (0.14 - d_) / 2), Inches(leg_y + 0.10 - d_ / 2), Inches(d_), Inches(d_))
            o.fill.solid(); o.fill.fore_color.rgb = rgb(GREY if kind == "T" else "C9C9CC")
            if kind == "T": o.line.fill.background()
            else: o.line.color.rgb = rgb(GREY); o.line.width = Pt(1.75)
        else:
            o = slide.shapes.add_shape(9, Inches(lx + 0.02), Inches(leg_y + 0.05), Inches(0.10), Inches(0.10))
            o.fill.solid(); o.fill.fore_color.rgb = rgb(BLACK); o.line.fill.background()
        o.name = "Legend " + label
        w = text_width_in(label, 10.5)
        add_textbox(slide, lx + 0.22, leg_y, w + 0.1, 0.2, label, size=10.5, anchor="m", wrap=False, name="Legend text " + label)
        lx += 0.22 + w + 0.45

    fy = leg_y + 0.30
    fh = frame_bottom - fy
    fx, fw = 0.35, 12.65
    ymin, ymax = min(years) - 1, max(years) + 1
    cd = XyChartData()
    order = [("F", "Faculty"), ("T", "Trustees"), ("S", "Sr. Administrators")]
    if data.get("T2"): order.append(("T2", extra_label or "Trustees only (different item)"))
    yrs_of = {k: [y for y in years if data[k].get(y) is not None] for k, _ in order}
    for key, name in order:
        s = cd.add_series(name)
        for yr in yrs_of[key]:
            s.add_data_point(float(data[key][yr]), float(yr))
    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES, Inches(fx), Inches(fy), Inches(fw), Inches(fh), cd)
    gf.name = "Perception dot plot"
    set_alt_text(gf, "Dot plot by year, " + f"{min(years)}–{max(years)}" + ": percent of business officers who agree that faculty, trustees and "
                     "senior administrators are realistic and aware of the institution's financial challenges. Faculty sit far below the other two groups in every year.")
    ch = gf.chart
    chart_frame_style(ch, 10)
    ch.has_legend = False
    il, iw = 0.70, 11.30      # inner plot in inches from the frame's left edge
    it, ih = 0.05, fh - 0.05 - 0.40
    set_plot_layout(ch, il / fw, it / fh, iw / fw, ih / fh)
    plot = ch.plots[0]; plot.vary_by_categories = False

    xa, ya = ch.category_axis, ch.value_axis
    style_axis(xa, 0, 100, 25, '0"%"', grid=True, grid_color="E4E4E6")
    style_axis(ya, ymin, ymax, 1, '[<%d]"";[>%d]"";0' % (min(years), max(years)), grid=True, grid_color="C9C9CC", size=11)
    ya.tick_labels.font.bold = True
    ya.major_tick_mark = XL_TICK_MARK.NONE
    ya.format.line.fill.background()
    # reversed year axis (earliest at top); x axis crosses at the bottom
    ya._element.find(C + "scaling").find(C + "orientation").set("val", "maxMin")
    xa_el = xa._element
    cr = xa_el.find(C + "crosses")
    cr.set("val", "max")

    styles = {"F": dict(color=RED, size=13, line=None), "T": dict(color=GREY, size=15, line=None), "S": dict(color=BLACK, size=9, line=None),
              "T2": dict(color="C9C9CC", size=11, line=GREY)}
    conn = {"F": RED, "T": GREY, "S": BLACK, "T2": GREY}
    P = {"r": XL_LABEL_POSITION.RIGHT, "l": XL_LABEL_POSITION.LEFT, "t": XL_LABEL_POSITION.ABOVE, "b": XL_LABEL_POSITION.BELOW}
    lab_pos = choose_positions(data, yrs_of, fx + il, fy + it, iw, ih, ymin, ymax)
    for ser, (key, name) in zip(plot.series, order):
        st = styles[key]
        style_series_markers(ser, st["color"], st["size"], line_color=st["line"], line_w=1.75)
        if key == "T2": series_no_line(ser)
        else: series_line(ser, conn[key], 0.75, dash="sysDash")
        for i, yr in enumerate(yrs_of[key]):
            v = data[key][yr]
            col = RED if key == "F" else BLACK
            set_label(ser.points[i], [[(f"{v}%" + ("*" if (star_years or {}).get(key) and yr in star_years[key] else ""), dict(bold=True, italic=True, color=col if key not in ("T", "T2") else GRAPHITE, size=10))]], P[lab_pos[(key, yr)]], 10)
        series_labels_off(ser)
    annotate_workbook(ch, {"E1": "Reading guide: column A = percent of business officers answering 4 or 5; column B = survey year. One block per group."})
    return slide, ch, dict(years=years)


def choose_positions(data, yrs_of, ox, oy, iw, ih, ymin, ymax):
    """pick l/r/t/b for each label to avoid markers, other labels and connector segments."""
    keys_all = [k for k in ("F", "T", "S", "T2") if k in yrs_of]
    MARK = dict(MARK_R); MARK.setdefault("T2", 0.08)
    pts = {}
    for key in keys_all:
        for yr in yrs_of[key]:
            pts[(key, yr)] = (ox + data[key][yr] / 100 * iw, oy + (yr - ymin) / (ymax - ymin) * ih)
    segs = []
    for key in keys_all:
        if key == "T2": continue
        for a, b in zip(yrs_of[key][:-1], yrs_of[key][1:]):
            segs.append((pts[(key, a)], pts[(key, b)]))
    def box(k, pos):
        px, py = pts[k]; r = MARK[k[0] if k[0] != "T2" else "T2"] + 0.02
        if pos == "r": return (px + r, py - LBL_H / 2, LBL_W, LBL_H)
        if pos == "l": return (px - r - LBL_W, py - LBL_H / 2, LBL_W, LBL_H)
        if pos == "t": return (px - LBL_W / 2, py - r - LBL_H, LBL_W, LBL_H)
        return (px - LBL_W / 2, py + r, LBL_W, LBL_H)
    def ov(a, b):
        x1 = max(a[0], b[0]); y1 = max(a[1], b[1]); x2 = min(a[0] + a[2], b[0] + b[2]); y2 = min(a[1] + a[3], b[1] + b[3])
        return max(0, x2 - x1) * max(0, y2 - y1)
    def seg_hits(b, s):
        (x1, y1), (x2, y2) = s; n = 12; hit = 0
        for i in range(n + 1):
            x = x1 + (x2 - x1) * i / n; y = y1 + (y2 - y1) * i / n
            if b[0] < x < b[0] + b[2] and b[1] < y < b[1] + b[3]: hit += 1
        return hit
    pref = {"F": {"r": 0, "l": .05, "t": .1, "b": .12}, "T": {"l": 0, "t": .05, "b": .08, "r": .3}, "S": {"r": 0, "t": .05, "b": .08, "l": .3},
            "T2": {"l": 0, "t": .05, "b": .08, "r": .3}}
    placed = {}
    def cost(k, pos):
        b = box(k, pos)
        if b[0] < ox - 0.5 or b[0] + b[2] > ox + iw + 0.6: return 1e6
        c = pref[k[0]][pos]
        for k2, (mx, my) in pts.items():
            r = MARK[k2[0]]
            c += ov(b, (mx - r, my - r, 2 * r, 2 * r)) * 800
        for k2, p2 in placed.items():
            if k2 != k: c += ov(b, box(k2, p2)) * 800
        for sgm in segs: c += seg_hits(b, sgm) * 0.25
        return c
    order_keys = sorted(pts, key=lambda k: (k[1], keys_all.index(k[0])))
    for k in order_keys: placed[k] = min("rltb", key=lambda p: cost(k, p))
    for _ in range(4):
        for k in order_keys: placed[k] = min("rltb", key=lambda p: cost(k, p))
    return placed
