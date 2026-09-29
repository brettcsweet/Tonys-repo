"""Collision-aware placement of annotation labels (text boxes + leader lines) over a native chart."""
import math
import numpy as np
from nu_helpers import *

DIRS = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, -1), (-1, -1), (1, 1), (-1, 1)]
DIR_PREF = {(1, 0): 0.0, (-1, 0): 0.10, (0, -1): 0.20, (0, 1): 0.30, (1, -1): 0.15, (-1, -1): 0.25, (1, 1): 0.35, (-1, 1): 0.40}
RADII = [(0.05, 0.0), (0.18, 0.7), (0.34, 1.6), (0.52, 2.8), (0.75, 4.5)]

def overlap(a, b):
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[0] + a[2], b[0] + b[2]); y2 = min(a[1] + a[3], b[1] + b[3])
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)

def infl(b, m):
    return (b[0] - m, b[1] - m, b[2] + 2 * m, b[3] + 2 * m)

def candidate(px, py, w, h, d, r, ms):
    sx, sy = d
    rr = r + ms / 2
    cx = px + (sx * (rr + w / 2) if sx else 0)
    cy = py + (sy * (rr + h / 2) if sy else 0)
    if sx and sy:  # diagonals: pull in a little so the box corner sits near the marker
        cx = px + sx * (rr * 0.7 + w / 2); cy = py + sy * (rr * 0.7 + h / 2)
    return (cx - w / 2, cy - h / 2, w, h)

def place(items, cloud_xy, bounds, fixed=(), marker_pts=None, ms=0.06, passes=10, allowed_radii=None, dens_w=0.02):
    """items: dict key -> dict(px,py,w,h[,ms]).  bounds=(x0,y0,x1,y1).  returns key -> (box, leader_needed, cost)."""
    keys = list(items)
    marker_pts = marker_pts or {k: (v["px"], v["py"]) for k, v in items.items()}
    radii = allowed_radii or RADII
    cand = {}
    for k in keys:
        it = items[k]; cl = []
        for (r, rp) in radii:
            if r > it.get("max_r", 9) or r < it.get("min_r", 0): continue
            for d in DIRS:
                b = candidate(it["px"], it["py"], it["w"], it["h"], d, r, it.get("ms", ms))
                if b[0] < bounds[0] or b[1] < bounds[1] or b[0] + b[2] > bounds[2] or b[1] + b[3] > bounds[3]:
                    continue
                cl.append((b, rp + DIR_PREF[d], r))
        cand[k] = cl
    dens = {}
    for k in keys:
        dd = []
        for (b, base, r) in cand[k]:
            inside = ((cloud_xy[:, 0] > b[0]) & (cloud_xy[:, 0] < b[0] + b[2]) & (cloud_xy[:, 1] > b[1]) & (cloud_xy[:, 1] < b[1] + b[3])).sum()
            dd.append(inside * dens_w)
        dens[k] = dd
    chosen = {}
    def seg_of(b, px, py):
        ex, ey = nearest_on_box(b, px, py)
        return (px, py, ex, ey)
    def seg_hits(seg, box, n=10):
        x1, y1, x2, y2 = seg; hit = 0
        for i in range(1, n):
            x = x1 + (x2 - x1) * i / n; y = y1 + (y2 - y1) * i / n
            if box[0] < x < box[0] + box[2] and box[1] < y < box[1] + box[3]: hit += 1
        return hit
    def cost_of(k, ci, placed):
        b, base, r = cand[k][ci]
        c = base + dens[k][ci]
        bi = infl(b, 0.012)
        for fb in fixed: c += overlap(bi, fb) * 3000
        for k2, (b2, _) in placed.items():
            if k2 == k: continue
            c += overlap(bi, b2) * 3000
        for k2, (mx, my) in marker_pts.items():
            if k2 == k: continue
            c += overlap(bi, (mx - 0.035, my - 0.035, 0.07, 0.07)) * 1500
        # leader lines must not cross other labels (either direction)
        mx0, my0 = marker_pts[k]
        if cand[k][ci][2] > 0.12:
            sg = seg_of(b, mx0, my0)
            for k2, (b2, _) in placed.items():
                if k2 != k: c += seg_hits(sg, b2) * 6.0
        for k2, (b2, ci2) in placed.items():
            if k2 == k or cand[k2][ci2][2] <= 0.12: continue
            sg2 = seg_of(b2, *marker_pts[k2])
            c += seg_hits(sg2, bi) * 6.0
        # own marker must not sit under the label
        mx, my = marker_pts[k]
        c += overlap(b, (mx - 0.03, my - 0.03, 0.06, 0.06)) * 4000
        return c
    # order: most constrained (fewest low-cost options) first ~ crowded first: by local marker density
    order = sorted(keys, key=lambda k: -sum(1 for k2, (mx, my) in marker_pts.items() if abs(mx - items[k]["px"]) < 0.6 and abs(my - items[k]["py"]) < 0.3))
    placed = {}
    for k in order:
        if not cand[k]: raise RuntimeError("no candidate for " + k)
        ci = min(range(len(cand[k])), key=lambda i: cost_of(k, i, placed))
        placed[k] = (cand[k][ci][0], ci)
    for _ in range(passes):
        changed = False
        for k in order:
            ci = min(range(len(cand[k])), key=lambda i: cost_of(k, i, placed))
            if ci != placed[k][1]:
                changed = True
            placed[k] = (cand[k][ci][0], ci)
        if not changed: break
    out = {}
    for k in keys:
        b, ci = placed[k]
        out[k] = (b, cand[k][ci][2] > 0.12, cost_of(k, ci, placed))
    return out

def nearest_on_box(b, px, py):
    x = min(max(px, b[0]), b[0] + b[2]); y = min(max(py, b[1]), b[1] + b[3])
    return x, y

def draw_labels(slide, placed, spec, marker_r=0.03, group_name="Institution labels"):
    """spec[key] = dict(paras, color, size, bold, italic, leader_color, px, py). Adds leaders first, then text boxes."""
    shapes = []
    for k, (b, lead, c) in placed.items():
        s = spec[k]
        if lead:
            ex, ey = nearest_on_box(b, s["px"], s["py"])
            dx, dy = ex - s["px"], ey - s["py"]
            L = math.hypot(dx, dy) or 1
            sx, sy = s["px"] + dx / L * marker_r, s["py"] + dy / L * marker_r
            shapes.append(add_line(slide, sx, sy, ex, ey, color=s.get("leader_color", GREY), width=0.5, name="Leader " + k))
    for k, (b, lead, c) in placed.items():
        s = spec[k]
        tb = add_textbox(slide, b[0], b[1], b[2], b[3], s["paras"], size=s.get("size", 8), color=s.get("color", BLACK),
                         bold=s.get("bold", False), italic=s.get("italic", False), align=s.get("align", "c"), anchor="m",
                         name="Label " + k, wrap=False, fill=s.get("fill", WHITE), fill_alpha=s.get("alpha", 72))
        tb.text_frame.margin_left = tb.text_frame.margin_right = Inches(0.03)
        shapes.append(tb)
    return shapes
