"""Slide 1: College Scorecard scatter (net price vs median earnings 10 yrs after entry)."""
import math
import numpy as np
from nu_helpers import *

XMAX, YMAX = 60000, 150000   # defaults; build_slide1 may override
LBL_SIZE = 8
FOCUS_NEAR = {'Vanderbilt University', 'Boston University', 'Massachusetts Institute of Technology'}
PAD_W, LBL_H = 0.08, 0.165
MS = 0.06  # nominal marker diameter (in)
FRAME_BOTTOM = 6.00


class Geo:
    def __init__(self, content_top):
        self.FX, self.FW = 0.35, 12.65
        self.LEG_H = 0.30
        self.FY = content_top
        self.FH = FRAME_BOTTOM - content_top
        # inner plot in inches
        self.IL = self.FX + 0.082 * self.FW
        self.IW = 0.900 * self.FW
        self.IT = self.FY + self.LEG_H + 0.02
        self.IH = self.FH - self.LEG_H - 0.02 - 0.62      # 0.62in below plot for tick labels + axis title
        self.PX, self.PY = (self.IL - self.FX) / self.FW, (self.IT - self.FY) / self.FH
        self.PW, self.PH = self.IW / self.FW, self.IH / self.FH

    def X(self, v): return self.IL + v / XMAX * self.IW
    def Y(self, v): return self.IT + (1 - v / YMAX) * self.IH


def box_for(pos, px, py, w, h, ms=MS):
    g = 0.02 + ms / 2
    if pos == "r": return (px + g, py - h / 2, w, h)
    if pos == "l": return (px - g - w, py - h / 2, w, h)
    if pos == "t": return (px - w / 2, py - g - h, w, h)
    if pos == "b": return (px - w / 2, py + g, w, h)


def overlap(a, b):
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[0] + a[2], b[0] + b[2]); y2 = min(a[1] + a[3], b[1] + b[3])
    return max(0, x2 - x1) * max(0, y2 - y1)


def place_labels(g, items, cloud_xy, fixed_boxes, marker_xy, passes=6):
    pref = {"r": 0.0, "l": 0.25, "t": 0.45, "b": 0.6}
    placed = {}

    def cost(it, pos, others):
        b = box_for(pos, it["px"], it["py"], it["w"], it["h"])
        if b[0] < g.IL - 0.05 or b[0] + b[2] > g.IL + g.IW + 0.05 or b[1] < g.IT - 0.02 or b[1] + b[3] > g.IT + g.IH:
            return 1e6
        c = pref[pos]
        for fb in fixed_boxes: c += overlap(b, fb) * 400
        for k, (ob, _) in others.items(): c += overlap(b, ob) * 400
        for mk, (mx, my) in marker_xy.items():
            if mk == it["key"]: continue
            c += overlap(b, (mx - 0.03, my - 0.03, 0.06, 0.06)) * 250
        inside = ((cloud_xy[:, 0] > b[0]) & (cloud_xy[:, 0] < b[0] + b[2]) & (cloud_xy[:, 1] > b[1]) & (cloud_xy[:, 1] < b[1] + b[3])).sum()
        return c + inside * 0.06

    order = sorted(items, key=lambda it: (it["px"], it["py"]))
    for it in order:
        best = min("rltb", key=lambda p: cost(it, p, placed))
        placed[it["key"]] = (box_for(best, it["px"], it["py"], it["w"], it["h"]), best)
    for _ in range(passes):
        for it in order:
            others = {k: v for k, v in placed.items() if k != it["key"]}
            best = min("rltb", key=lambda p: cost(it, p, others))
            placed[it["key"]] = (box_for(best, it["px"], it["py"], it["w"], it["h"]), best)
    costs = {}
    for it in items:
        others = {k: v for k, v in placed.items() if k != it["key"]}
        costs[it["key"]] = cost(it, placed[it["key"]][1], others)
    return {k: v[1] for k, v in placed.items()}, costs


def build_slide1(prs, df, label_map, focus="Northeastern University", title=None, subtitle=None,
                 notes_paras=None, source=None, draft_tag=None, notes_text=None, overrides=None, xmax=None, ymax=None):
    global XMAX, YMAX
    if xmax: XMAX = xmax
    if ymax: YMAX = ymax
    df = df.copy()
    df = df.sort_values(["y", "x"], ascending=[True, True]).reset_index(drop=True)   # alignment rule from the original workbook
    df_all = df
    df = df[(df.x >= 0) & (df.x <= XMAX) & (df.y <= YMAX)].reset_index(drop=True)   # off-axis points are counted upstream, not drawn
    pub = df[df.control == 1].reset_index(drop=True)
    pri = df[df.control == 2].reset_index(drop=True)
    focus_row = df[df.name == focus].iloc[0]

    slide, content_top = new_slide(prs, title, subtitle, notes_paras, source, draft_tag, notes_text)
    g = Geo(content_top)

    # series order matters for LibreOffice rendering: private first, then public, then highlight
    cd = XyChartData()
    s_pri = cd.add_series("Private institutions")
    for _, r in pri.iterrows(): s_pri.add_data_point(float(r.x), float(r.y))
    s_pub = cd.add_series("Public institutions")
    for _, r in pub.iterrows(): s_pub.add_data_point(float(r.x), float(r.y))
    s_foc = cd.add_series("Northeastern")
    s_foc.add_data_point(float(focus_row.x), float(focus_row.y))

    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(g.FX), Inches(g.FY), Inches(g.FW), Inches(g.FH), cd)
    gf.name = "Scorecard scatter"
    set_alt_text(gf, "Scatter chart: median earnings ten years after entry versus average annual net cost of attendance for "
                     f"{len(df):,} institutions ({len(pub)} public, {len(pri)} private). Northeastern is highlighted in red; "
                     "the private-institution trendline slopes upward.")
    ch = gf.chart
    chart_frame_style(ch, 9)
    set_plot_layout(ch, g.PX, g.PY, g.PW, g.PH)
    plot = ch.plots[0]; plot.vary_by_categories = False
    ch.has_legend = False

    style_axis(ch.category_axis, 0, XMAX, 10000, '"$"#,##0', grid=True, grid_color="E4E4E6")
    style_axis(ch.value_axis, 0, YMAX, 10000, '"$"#,##0', grid=True, grid_color="E4E4E6")
    axis_title(ch.category_axis, [("Average annual net cost of attendance (2)", {})], size=10)
    axis_title(ch.value_axis, [("Median earnings ten years after entry (1)", {})], size=10, rot=-5400000)

    sv, sp, sf = plot.series[0], plot.series[1], plot.series[2]
    style_series_markers(sv, ROYAL, 4, alpha=85); series_no_line(sv)                                   # private: bright royal blue
    style_series_markers(sp, GREY, 3, alpha=80, line_color=BLACK, line_w=0.25); series_no_line(sp)   # public: one size smaller, hairline black border
    style_series_markers(sf, RED, 11, line_color=WHITE, line_w=1.25); series_no_line(sf)
    add_trendline(sv, "Private college trendline", BLACK, 1.25)

    # ---------------- labels: annotation layer (text boxes + leaders), collision-checked
    import overlay_labels as OL
    cloud = np.array([[g.X(r.x), g.Y(r.y)] for _, r in df.iterrows()])
    items, spec = {}, {}
    for short, (full, *_rest) in label_map.items():
        if full == focus: continue
        row = df[df.name == full]
        if row.empty: continue
        r = row.iloc[0]
        text, sup = short, ""
        if short.startswith("Landmark College"): text, sup = "Landmark College", " (3)"
        w = text_width_in(text + sup, LBL_SIZE, italic=True) + 0.09
        px, py = g.X(r.x), g.Y(r.y)
        items[full] = dict(px=px, py=py, w=w, h=0.15, max_r=(0.20 if full in FOCUS_NEAR else 9))
        color = NAVY if r.control == 2 else MUTED
        spec[full] = dict(paras=[[(text + sup, {})]], color=color, size=LBL_SIZE, italic=True, px=px, py=py, leader_color=color)
    bounds = (g.IL + 0.02, g.IT + 0.02, g.IL + g.IW - 0.02, g.IT + g.IH - 0.02)
    fpx, fpy = g.X(focus_row.x), g.Y(focus_row.y)
    foc_w = text_width_in("Northeastern", 12, bold=True) + 0.10
    marker_pts = {k: (v["px"], v["py"]) for k, v in items.items()}
    marker_pts["__focus__"] = (fpx, fpy)

    # "Better deal / Worse deal": pick the emptiest spot above / below the trendline near its right end
    pri_fit = np.polyfit(pri.x, pri.y, 1)
    slope_deg = math.degrees(math.atan2(pri_fit[0] * g.IH / YMAX, g.IW / XMAX))
    def best_spot(sign):
        best = None
        for xv in range(int(XMAX * 0.70), int(XMAX * 0.93), 500):
            for off in (7000, 9000, 11000, 13000):
                cx, cy = g.X(xv), g.Y(pri_fit[1] + pri_fit[0] * xv + sign * off)
                bx = (cx - 0.5, cy - 0.15, 1.0, 0.3)
                if bx[1] < g.IT or bx[1] + bx[3] > g.IT + g.IH or bx[0] + bx[2] > g.IL + g.IW: continue
                n = ((cloud[:, 0] > bx[0]) & (cloud[:, 0] < bx[0] + bx[2]) & (cloud[:, 1] > bx[1]) & (cloud[:, 1] < bx[1] + bx[3])).sum()
                lbl = sum(OL.overlap(bx, (v["px"] - 0.2, v["py"] - 0.1, 0.4, 0.2)) > 0 for v in items.values())
                c = n * 1.0 + lbl * 6 + off / 4000
                if best is None or c < best[0]: best = (c, cx, cy)
        return best[1], best[2]
    better_c = best_spot(+1)
    worse_c = best_spot(-1)
    deal_boxes = [(better_c[0] - 0.5, better_c[1] - 0.15, 1.0, 0.3), (worse_c[0] - 0.5, worse_c[1] - 0.15, 1.0, 0.3)]

    foc_items = {"__focus__": dict(px=fpx, py=fpy, w=foc_w, h=0.23, ms=0.16)}
    foc_placed = OL.place(foc_items, cloud, bounds, fixed=deal_boxes,
                          marker_pts={k: v for k, v in marker_pts.items()}, ms=0.16,
                          allowed_radii=[(0.05, 0.0), (0.12, 0.3)], dens_w=0.0)
    foc_box = foc_placed["__focus__"][0]
    placed = OL.place(items, cloud, bounds, fixed=deal_boxes + [OL.infl(foc_box, 0.02)], marker_pts=marker_pts)
    if overrides:
        for k, v in overrides.items():
            if k in placed: placed[k] = (v, True, 0.0)
    spec["__focus__"] = dict(paras=[[("Northeastern", {})]], color=RED, size=12, bold=True, px=fpx, py=fpy, leader_color=RED, alpha=82)
    allp = dict(placed); allp["__focus__"] = foc_placed["__focus__"]
    lab_shapes = OL.draw_labels(slide, allp, spec, marker_r=0.03)
    costs = {k: v[2] for k, v in allp.items()}

    write_names_to_workbook(ch, [list(pri.name), list(pub.name), [focus]])

    # ---------------- annotations + legend (drawn shapes so order/placement is deterministic)
    for label, c in (("Better deal", better_c), ("Worse deal", worse_c)):
        add_textbox(slide, c[0] - 0.5, c[1] - 0.12, 1.0, 0.24, label, size=10, color=GREY, italic=True,
                    align="c", anchor="m", rot=-slope_deg, name=label)
    add_legend_row(slide, [("dot", GREY, "Public institutions", {"d": 0.085, "outline": BLACK, "outline_w": 0.25}), ("dot", ROYAL, "Private institutions", {}),
                           ("line", BLACK, "Private college trendline", {"w": 1.5}), ("dot", RED, "Northeastern", {"d": 0.13})],
                   x_right=g.IL + g.IW, y=g.FY + 0.02)
    return slide, ch, dict(costs=costs, slope_deg=slope_deg, pri_fit=list(pri_fit),
                           counts=(len(pub), len(pri)), n_drawn=len(df), n_all=len(df_all), focus=focus_row.to_dict(), geo=g.__dict__)
