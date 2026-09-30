import math, random, base64, os

random.seed(11)
W, H = 2880, 1620
SP = os.path.dirname(os.path.abspath(__file__))

# ---------- palette ----------
RED = "#C8102E"; DRED = "#8E0B21"; DDRED = "#5E0716"
CH = "#2B2E33"; CH2 = "#3A3F45"; CH3 = "#4F555C"
B1 = "#5E7A92"; B2 = "#8FA6B8"; B3 = "#B9C8D4"; B4 = "#DDE5EC"
GOLD = "#A4804A"; GOLD2 = "#C9A66B"; GOLD3 = "#7C5F34"
G1 = "#F4F5F6"; G2 = "#E3E6E9"; G3 = "#C6CBD0"; G4 = "#9AA1A8"; G5 = "#6E757C"
FONT = "Lato, 'Helvetica Neue', Arial, sans-serif"


def mix(a, b, t):
    a = a.lstrip('#'); b = b.lstrip('#')
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(round(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))


def catmull(points, n=24):
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def qb(p0, c, p1, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]
    return x, y


def qb_tan(p0, c, p1, t):
    dx = 2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0])
    dy = 2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1])
    return math.degrees(math.atan2(dy, dx))


def pts_str(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


P = []
add = P.append


def txt(x, y, s, size=24, fill=CH, weight=700, anchor="start", ls=0, op=1, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}" {extra}>{s}</text>')


def label(x, y, title, sub, anchor="middle", tcol=RED, scol=G5, rule="#000", size=27):
    if anchor == "middle":
        rx = x - 27
    elif anchor == "start":
        rx = x
    else:
        rx = x - 54
    s = f'<rect x="{rx}" y="{y - 40}" width="54" height="5" fill="{rule}"/>'
    s += txt(x, y, title.upper(), size, tcol, 900, anchor, 3.4)
    s += txt(x, y + 32, sub, 22, scol, 400, anchor, 0.3)
    return s


def husky(cx, cy, s=1.0):
    """Stylized husky head (front view) - an illustration, not the official mark."""
    g = f'<g transform="translate({cx},{cy}) scale({s})" stroke-linejoin="round">'
    g += f'<path d="M-52,-6 L-49,-64 L-16,-40 Q0,-46 16,-40 L49,-64 L52,-6 Q60,32 32,54 Q0,68 -32,54 Q-60,32 -52,-6 Z" fill="{CH}" stroke="#fff" stroke-width="4"/>'
    g += '<path d="M-42,-14 L-41,-48 L-24,-34 Z M42,-14 L41,-48 L24,-34 Z" fill="#E3E6E9"/>'
    g += '<path d="M0,-34 L-9,-14 Q-36,-6 -37,20 Q-36,46 -16,54 Q0,60 16,54 Q36,46 37,20 Q36,-6 9,-14 Z" fill="#fff"/>'
    g += f'<ellipse cx="-21" cy="-2" rx="15" ry="12" fill="{CH}"/><ellipse cx="21" cy="-2" rx="15" ry="12" fill="{CH}"/>'
    for ex in (-21, 21):
        g += f'<circle cx="{ex}" cy="-2" r="7.5" fill="#fff"/><circle cx="{ex}" cy="-2" r="5" fill="{B1}"/><circle cx="{ex}" cy="-2" r="2.4" fill="#000"/>'
    g += '<path d="M-9,26 Q0,20 9,26 Q6,36 0,38 Q-6,36 -9,26 Z" fill="#000"/>'
    g += f'<path d="M0,38 L0,46 M-11,49 Q0,56 11,49" stroke="{CH}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    return g + '</g>'


def label2(x, y, lines, sub, tcol=RED, scol=G5, rule="#000", size=27):
    s = f'<rect x="{x - 27}" y="{y - 40}" width="54" height="5" fill="{rule}"/>'
    for i, ln in enumerate(lines):
        s += txt(x, y + i * 34, ln.upper(), size, tcol, 900, "middle", 3.4)
    s += txt(x, y + (len(lines) - 1) * 34 + 32, sub, 22, scol, 400, "middle", 0.3)
    return s


# =====================================================================
# defs
# =====================================================================
font_css = ""
for w in (400, 700, 900):
    p = os.path.join(SP, "node_modules/@fontsource/lato/files", f"lato-latin-{w}-normal.woff2")
    b = base64.b64encode(open(p, "rb").read()).decode()
    font_css += ("@font-face{font-family:'Lato';font-weight:%d;font-style:normal;src:url(data:font/woff2;base64,%s) format('woff2');}\n" % (w, b))

add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<defs><style>{font_css}</style>')
add(f'''
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#AEBECC"/><stop offset=".32" stop-color="#D0DAE3"/>
  <stop offset=".56" stop-color="#EDF0F3"/><stop offset="1" stop-color="{G1}"/>
</linearGradient>
<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#D3D9DF"/><stop offset="1" stop-color="#EEF0F2"/>
</linearGradient>
<linearGradient id="cliff" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#23262A"/><stop offset=".7" stop-color="#34383E"/><stop offset="1" stop-color="#43484F"/>
</linearGradient>
<radialGradient id="ocean" cx=".36" cy=".32" r=".8">
  <stop offset="0" stop-color="#8CA6BA"/><stop offset=".6" stop-color="#557089"/><stop offset="1" stop-color="#34495E"/>
</radialGradient>
<radialGradient id="shine" cx=".3" cy=".25" r=".6">
  <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<linearGradient id="dome" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{GOLD2}"/><stop offset=".45" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD3}"/>
</linearGradient>
<linearGradient id="stone" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#F1F3F5"/><stop offset="1" stop-color="#D9DDE2"/>
</linearGradient>
<linearGradient id="fadeR" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/>
</linearGradient>
<linearGradient id="mist" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".55"/>
</linearGradient>
<pattern id="tiepat" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(12)">
  <rect width="18" height="18" fill="#4A86DB"/>
  <path d="M2,9 a5,5 0 1 1 10,0 v5 h-5" fill="none" stroke="#EAF1FA" stroke-width="2.6" opacity=".9"/>
  <path d="M11,3 h6" stroke="#B7CAE6" stroke-width="2.2" opacity=".8"/>
</pattern>
<pattern id="stripe" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="16" height="16" fill="#fff"/><rect width="8" height="16" fill="{RED}"/>
</pattern>
<clipPath id="globeclip"><circle cx="0" cy="0" r="150"/></clipPath>
<clipPath id="tieclip"><path d="M-14,-482 L14,-482 L11,-460 L32,-352 L0,-316 L-32,-352 L-11,-460 Z"/></clipPath>
<clipPath id="shieldclip"><path d="M-350,-500 L-180,-500 L-180,-390 Q-180,-300 -265,-258 Q-350,-300 -350,-390 Z"/></clipPath>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="soft2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
''')
add('</defs>')

# =====================================================================
# background: sky, hills
# =====================================================================
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
add(f'<path d="M0,860 L0,770 Q160,700 330,752 T640,744 T980,770 T1420,748 T1780,736 T2100,742 T2400,712 T2640,730 T2880,702 L2880,860 Z" fill="#C3D0DB"/>')
add(f'<path d="M0,860 L0,806 Q220,760 420,800 T820,790 T1250,808 T1650,782 T2050,800 T2400,770 T2640,784 T2880,764 L2880,860 Z" fill="#AEBFCD"/>')

# =====================================================================
# institutional uncertainty : storm clouds
# =====================================================================
def cloud(cx, cy, sx, sy, fill, op=1):
    circles = [(-120, 10, 55), (-60, -25, 70), (20, -40, 85), (100, -15, 68), (150, 15, 50), (0, 20, 70)]
    g = f'<g transform="translate({cx},{cy}) scale({sx},{sy})" fill="{fill}" opacity="{op}">'
    for x, y, r in circles:
        g += f'<circle cx="{x}" cy="{y}" r="{r}"/>'
    g += '<rect x="-170" y="8" width="360" height="62" rx="31"/></g>'
    return g

add(cloud(830, 150, 1.25, 1.0, "#8996A2", .75))
add(cloud(1570, 140, 1.35, 1.05, "#8996A2", .75))
add(cloud(1200, 95, 2.4, 1.15, "#7A8792", .85))
add(cloud(960, 128, 1.7, 1.1, "#575F68", .95))
add(cloud(1450, 122, 1.75, 1.12, "#575F68", .95))
add(cloud(1200, 118, 2.3, 1.12, "#30353B", 1))
# rain
rain = ""
for i in range(22):
    x = 740 + i * 8 + random.random() * 4
    y = 250 + random.random() * 24
    rain += f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 14:.0f}" y2="{y + 50 + random.random() * 24:.0f}"/>'
for i in range(22):
    x = 1500 + i * 8 + random.random() * 4
    y = 250 + random.random() * 24
    rain += f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 14:.0f}" y2="{y + 50 + random.random() * 24:.0f}"/>'
add(f'<g stroke="{B1}" stroke-width="3" stroke-linecap="round" opacity=".55">{rain}</g>')
# lightning
add(f'<path d="M1010,214 L972,292 L1000,292 L962,376 L1052,270 L1022,270 L1056,214 Z" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2.5" stroke-linejoin="round"/>')
add(f'<path d="M1428,222 L1398,282 L1420,282 L1394,346 L1462,268 L1440,268 L1466,222 Z" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2.5" stroke-linejoin="round" opacity=".85"/>')
add('<rect x="880" y="82" width="640" height="68" fill="#fff"/>')
add('<rect x="880" y="82" width="640" height="5" fill="#000"/>')
add(txt(1200, 128, "INSTITUTIONAL UNCERTAINTY", 31, RED, 900, "middle", 5))

# =====================================================================
# ground, cliff, road
# =====================================================================
add(f'<rect x="0" y="850" width="{W}" height="{H - 850}" fill="url(#ground)"/>')
add(f'<rect x="0" y="850" width="{W}" height="3" fill="{G3}"/>')
# faint ground planes for perspective
for i, yy in enumerate((905, 985, 1085, 1215, 1370, 1500)):
    add(f'<rect x="0" y="{yy}" width="{W}" height="2" fill="{G3}" opacity="{0.35 - i * .05:.2f}"/>')

# ----- cliff -----
cliff_edge = [(585, 850), (566, 900), (603, 962), (574, 1030), (612, 1112), (584, 1194), (622, 1282), (594, 1364), (632, 1500), (602, 1562), (640, 1620)]
cliff_pts = [(0, 850)] + cliff_edge + [(0, H)]
add(f'<polygon points="{pts_str([(x + 26, y) for x, y in cliff_edge] + [(x + 60, y + 30) for x, y in reversed(cliff_edge)])}" fill="#000" opacity=".10" filter="url(#soft2)"/>')
add(f'<polygon points="{pts_str(cliff_pts)}" fill="url(#cliff)"/>')
# strata
strata = ""
for i, yy in enumerate((925, 985, 1050, 1120, 1185, 1255, 1330, 1410)):
    xe = 560 + random.random() * 40
    pts = [(0, yy + random.random() * 6)]
    for k in range(1, 8):
        pts.append((xe * k / 7, yy + random.random() * 14 - 7))
    strata += f'<polyline points="{pts_str(pts)}" fill="none" stroke="{mix("#3A3F45", "#6E757C", .35 + .06 * (i % 3))}" stroke-width="{2 + (i % 3)}" opacity=".7"/>'
add(strata)
add(f'<path d="M0,850 L585,850 L582,866 L0,866 Z" fill="{G5}"/>')
add(f'<path d="M0,850 L585,850" stroke="{G4}" stroke-width="3"/>')
# label on the cliff face
add('<rect x="50" y="916" width="440" height="130" fill="#fff"/>')
add('<rect x="50" y="916" width="440" height="5" fill="#000"/>')
add(txt(74, 972, "DEMOGRAPHIC CLIFF", 27, RED, 900, "start", 3.4))
add(txt(74, 1006, "Fewer college-age students each year", 22, G5, 400, "start", .3))
# mist at the cliff base
add(f'<clipPath id="cliffclip"><polygon points="{pts_str(cliff_pts)}"/></clipPath><rect x="0" y="{H - 140}" width="700" height="140" fill="url(#mist)" clip-path="url(#cliffclip)"/>')

# ----- pictogram columns (students) -----
def student(x, y, s=1.0, fill=B1, op=1.0, ghost=False, bag=False):
    if ghost:
        st = f'fill="none" stroke="{G4}" stroke-width="2.4" stroke-dasharray="4 4" stroke-linejoin="round"'
    else:
        st = f'fill="{fill}"'
    g = f'<g transform="translate({x:.1f},{y:.1f}) scale({s})" opacity="{op}" {st}>'
    g += '<circle cx="0" cy="-41" r="8.5"/>'
    g += '<path d="M-10,-28 Q-10,-32.5 -6,-32.5 L6,-32.5 Q10,-32.5 10,-28 L10,-11 L-10,-11 Z"/>'
    g += '<rect x="-9" y="-11" width="8" height="11" rx="1.5"/><rect x="1" y="-11" width="8" height="11" rx="1.5"/>'
    g += '<rect x="-16" y="-30" width="7.5" height="17" rx="3"/>'
    if bag:
        g += f'<rect x="12" y="-14" width="15" height="13" rx="2" fill="{CH2}" stroke="none"/><rect x="15" y="-18" width="9" height="4" rx="1.5" fill="none" stroke="{CH2}" stroke-width="2"/>'
    g += '</g>'
    return g

counts = [5, 5, 4, 4, 3, 2, 1]
slot = 50; base = 850 - 8
tops = []
for i, c in enumerate(counts):
    x = 92 + 68 * i
    col = mix(B1, DRED, i / 6.0)
    for j in range(5):
        y = base - j * slot
        if j < c:
            add(student(x, y, 1.0, col))
        else:
            add(student(x, y, 1.0, ghost=True, op=.85))
    tops.append((x, base - c * slot + 6))
# trend line falling off the cliff
tl = tops + [(586, tops[-1][1] + 34)]
add(f'<polyline points="{pts_str(tl)}" fill="none" stroke="{RED}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="2 12"/>')
add(f'<path d="M{tl[-1][0]},{tl[-1][1]} Q660,{tl[-1][1] + 20} 668,1000" fill="none" stroke="{RED}" stroke-width="6" stroke-linecap="round" stroke-dasharray="2 12"/>')
add(f'<polygon points="668,1046 646,1002 690,1002" fill="{RED}"/>')
add(txt(92, 566, "PEAK", 19, G5, 700, "middle", 3))

# ----- road -----
center = catmull([(1200, 1700), (1200, 1545), (1120, 1440), (940, 1345), (930, 1240), (1130, 1170), (1420, 1140), (1500, 1050),
                  (1330, 985), (1110, 950), (1120, 900), (1200, 862)], 30)
def hw(y):
    return 34 + (y - 862) / (1545 - 862) * 92
left, right = [], []
for i, (x, y) in enumerate(center):
    a = center[max(i - 1, 0)]; b = center[min(i + 1, len(center) - 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    w = hw(y)
    left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))

def idx_at_y(yy):
    return min(range(len(center)), key=lambda i: abs(center[i][1] - yy) + (0 if i > 20 else 500))

# dead-end branches (drawn under the main road)
def branch(pts, width, barrier_at=None, sign=None):
    c = catmull(pts, 16)
    add(f'<polyline points="{pts_str(c)}" fill="none" stroke="{CH3}" stroke-width="{width}" stroke-linejoin="round"/>')
    add(f'<polyline points="{pts_str(c)}" fill="none" stroke="{GOLD2}" stroke-width="3.5" stroke-dasharray="14 12" opacity=".7"/>')

branch([(950, 1250), (830, 1235), (770, 1170), (790, 1100)], 46)
add(f'<g transform="translate(790,1082) rotate(-8)"><rect x="-34" y="-9" width="68" height="18" fill="url(#stripe)" stroke="{CH}" stroke-width="2.5"/><rect x="-30" y="9" width="5" height="22" fill="{CH}"/><rect x="25" y="9" width="5" height="22" fill="{CH}"/></g>')
branch([(1500, 1050), (1590, 1018), (1650, 968)], 40)
add(f'<g transform="translate(1668,952) rotate(-40)"><rect x="-32" y="-9" width="64" height="18" fill="url(#stripe)" stroke="{CH}" stroke-width="2.5"/><rect x="-28" y="9" width="5" height="22" fill="{CH}"/><rect x="23" y="9" width="5" height="22" fill="{CH}"/></g>')

road_poly = left + right[::-1]
add(f'<polygon points="{pts_str(road_poly)}" fill="{CH3}" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<polyline points="{pts_str(center)}" fill="none" stroke="{GOLD2}" stroke-width="5" stroke-dasharray="24 20" stroke-linecap="butt" opacity=".9"/>')
# curb highlights
add(f'<polyline points="{pts_str(left)}" fill="none" stroke="{G5}" stroke-width="3" opacity=".6"/>')

# cracks across the road
def crack(i, reach=0.9, seed=0):
    rnd = random.Random(seed)
    x, y = center[i]
    a = center[max(i - 1, 0)]; b = center[min(i + 1, len(center) - 1)]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    tx, ty = dx / L, dy / L
    nx, ny = -ty, tx
    w = hw(y)
    pts = []
    n = 7
    for k in range(n + 1):
        f = -0.95 + (reach + 0.95) * k / n
        j = (rnd.random() - .5) * 16 * (w / 100)
        pts.append((x + nx * w * f + tx * j, y + ny * w * f + ty * j + (10 if k % 2 else -4)))
    s = f'<polyline points="{pts_str(pts)}" fill="none" stroke="#141618" stroke-width="{3.2 + w / 60:.1f}" stroke-linejoin="miter" stroke-linecap="round"/>'
    bx, by = pts[3]
    s += f'<polyline points="{bx:.1f},{by:.1f} {bx + tx * 26 + nx * 8:.1f},{by + ty * 26 + ny * 8:.1f} {bx + tx * 40 - nx * 6:.1f},{by + ty * 40 - ny * 6:.1f}" fill="none" stroke="#141618" stroke-width="2.6" stroke-linecap="round"/>'
    return s

for yy, sd in ((1400, 3), (1290, 8), (1175, 5), (1030, 2)):
    add(crack(idx_at_y(yy), 0.85, sd))
# a little road sign with a question mark
add(f'<g transform="translate(690,1160)"><rect x="-4" y="0" width="8" height="80" fill="{CH}"/><rect x="-36" y="-52" width="72" height="56" fill="{GOLD2}" stroke="{CH}" stroke-width="4"/>{txt(0, -8, "?", 46, CH, 900, "middle")}</g>')

# =====================================================================
# international enrollment : globe + flight paths + arrivals
# =====================================================================
gx, gy = 365, 275
ring = f'transform="translate({gx},{gy}) rotate(-20)"'
add(f'<g {ring}><path d="M-218,0 A218,52 0 0 1 218,0" fill="none" stroke="{GOLD}" stroke-width="5"/></g>')
g = f'<g transform="translate({gx},{gy})">'
g += '<ellipse cx="6" cy="172" rx="120" ry="14" fill="#000" opacity=".08" filter="url(#soft)"/>'
g += '<circle r="150" fill="url(#ocean)"/>'
g += '<g clip-path="url(#globeclip)">'
land = [
    "M-118,-62 Q-98,-114 -44,-104 Q-6,-98 -20,-62 Q-34,-30 -58,-8 Q-74,12 -90,-4 Q-112,-26 -118,-62 Z",
    "M-34,24 Q-6,16 6,38 Q18,64 2,100 Q-10,122 -24,104 Q-36,72 -38,46 Z",
    "M52,-92 Q88,-104 106,-76 Q100,-48 78,-44 Q86,-10 74,32 Q62,72 40,78 Q24,46 36,10 Q30,-22 46,-44 Z",
    "M92,-58 Q134,-86 168,-52 Q176,-14 146,-6 Q116,4 104,-22 Q92,-34 92,-58 Z",
    "M104,52 Q132,44 146,64 Q140,88 116,86 Q98,76 104,52 Z",
]
for d in land:
    g += f'<path d="{d}" fill="{B4}" opacity=".92"/>'
g += '</g>'
for rx in (46, 100):
    g += f'<ellipse rx="{rx}" ry="150" fill="none" stroke="#fff" stroke-width="1.6" opacity=".28"/>'
g += '<line x1="0" y1="-150" x2="0" y2="150" stroke="#fff" stroke-width="1.6" opacity=".28"/>'
for yy in (-90, -45, 0, 45, 90):
    hw_ = math.sqrt(150 ** 2 - yy ** 2)
    g += f'<path d="M{-hw_:.1f},{yy} Q0,{yy + 12} {hw_:.1f},{yy}" fill="none" stroke="#fff" stroke-width="1.6" opacity=".28"/>'
g += '<circle r="150" fill="url(#shine)"/>'
g += f'<circle r="150" fill="none" stroke="{CH2}" stroke-width="4"/>'
# origin pins
for px, py in ((100, -40), (118, 16), (96, 64)):
    g += f'<circle cx="{px}" cy="{py}" r="9" fill="{GOLD2}" stroke="{CH2}" stroke-width="2.5"/>'
g += '</g>'
add(g)
add(f'<g {ring}><path d="M-218,0 A218,52 0 0 0 218,0" fill="none" stroke="{GOLD}" stroke-width="5"/></g>')

def plane(x, y, ang, s=1.0, fill=CH2, op=1):
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang + 90:.1f}) scale({s})" opacity="{op}" fill="{fill}">'
            '<path d="M0,-20 L5,-6 L26,8 L26,13 L5,7 L4,17 L11,23 L11,27 L0,24 L-11,27 L-11,23 L-4,17 L-5,7 L-26,13 L-26,8 L-5,-6 Z"/></g>')

arcs = [
    ((470, 235), (700, 150), (850, 690), 1.0, "16 11", 6),
    ((482, 291), (690, 330), (830, 735), .52, "11 15", 5),
    ((462, 339), (660, 480), (808, 782), .26, "6 18", 4),
]
for (s0, c0, e0, op, dash, sw) in arcs:
    add(f'<path d="M{s0[0]},{s0[1]} Q{c0[0]},{c0[1]} {e0[0]},{e0[1]}" fill="none" stroke="{RED}" stroke-width="{sw}" stroke-dasharray="{dash}" stroke-linecap="round" opacity="{op}"/>')
    ang = qb_tan(s0, c0, e0, 1.0)
    add(f'<g transform="translate({e0[0]},{e0[1]}) rotate({ang:.1f})" opacity="{op}"><polygon points="4,0 -20,-11 -20,11" fill="{RED}"/></g>')
for (s0, c0, e0, op, dash, sw), t, sc in zip(arcs, (.46, .5, .5), (1.0, .8, .62)):
    x, y = qb(s0, c0, e0, t)
    add(plane(x, y, qb_tan(s0, c0, e0, t), sc, CH2, op if op > .3 else .35))

# arriving students (fewer / fading)
for x, s, op, bag in ((600, .8, .25, True), (668, .92, .45, True), (740, 1.02, .75, False), (816, 1.12, 1.0, True)):
    add(student(x, 928, s * 1.25, B1, op, bag=bag))

add(label(335, 500, "International Enrollment", "Fewer students arriving from abroad"))

# =====================================================================
# central university
# =====================================================================
add(f'<ellipse cx="1200" cy="858" rx="560" ry="20" fill="#000" opacity=".13" filter="url(#soft)"/>')
def window(x, y, w=30, h=56):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{B1}" stroke="{CH3}" stroke-width="3"/>'
            f'<polygon points="{x + 3},{y + h - 3} {x + 3},{y + h * .55} {x + w - 3},{y + 3} {x + w - 3},{y + h * .3}" fill="#fff" opacity=".18"/>'
            f'<line x1="{x + w / 2}" y1="{y}" x2="{x + w / 2}" y2="{y + h}" stroke="{CH3}" stroke-width="2"/>')

for wx in (780, 1460):
    add(f'<rect x="{wx}" y="600" width="160" height="250" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
    add(f'<rect x="{wx - 8}" y="584" width="176" height="20" fill="{CH3}"/>')
    add(f'<rect x="{wx - 8}" y="604" width="176" height="6" fill="#000" opacity=".12"/>')
    add(f'<rect x="{wx}" y="826" width="160" height="24" fill="{G3}"/>')
    for cxx in (wx + 26, wx + 104):
        for cy_ in (632, 712, 784):
            add(window(cxx, cy_, 30, 52 if cy_ < 780 else 36))

# central block
add(f'<rect x="960" y="548" width="480" height="240" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
# drum + dome
add(f'<rect x="1098" y="360" width="204" height="200" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
add(f'<rect x="1088" y="350" width="224" height="16" fill="{CH3}"/>')
for wx_ in (1132, 1188, 1244):
    add(f'<path d="M{wx_},430 v-34 a12,12 0 0 1 24,0 v34 z" fill="{B1}" stroke="{CH3}" stroke-width="3"/>')
add(f'<path d="M1094,352 A106,102 0 0 1 1306,352 Z" fill="url(#dome)" stroke="{GOLD3}" stroke-width="3"/>')
for k in (-64, -32, 0, 32, 64):
    add(f'<path d="M{1200 + k * .55},351 Q{1200 + k * .55 + k * .1},{300 - abs(k) * .1} 1200,252" fill="none" stroke="#fff" stroke-width="2" opacity=".28"/>')
add(f'<rect x="1184" y="222" width="32" height="34" fill="{G2}" stroke="{G4}" stroke-width="2"/>')
add(f'<path d="M1180,224 a20,16 0 0 1 40,0 z" fill="url(#dome)" stroke="{GOLD3}" stroke-width="2"/>')
add(f'<line x1="1200" y1="208" x2="1200" y2="166" stroke="{CH}" stroke-width="4"/>')
add(f'<circle cx="1200" cy="208" r="6" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2"/>')
add(f'<polygon points="1202,168 1256,182 1202,196" fill="{RED}"/>')
# pediment
add(f'<polygon points="946,552 1200,438 1454,552" fill="url(#stone)" stroke="{G4}" stroke-width="3" stroke-linejoin="round"/>')
add(f'<polygon points="984,544 1200,458 1416,544" fill="{G2}" stroke="{G3}" stroke-width="2"/>')
add(f'<circle cx="1200" cy="510" r="18" fill="{B1}" stroke="{GOLD}" stroke-width="5"/>')
# entablature
add(f'<rect x="950" y="552" width="500" height="44" fill="{G2}" stroke="{G4}" stroke-width="2.5"/>')
for tx_ in range(970, 1440, 24):
    add(f'<rect x="{tx_}" y="562" width="10" height="24" fill="{G3}"/>')
# recessed portico
add(f'<rect x="976" y="596" width="448" height="166" fill="#4A5058"/>')
add(f'<rect x="976" y="596" width="448" height="20" fill="#000" opacity=".22"/>')
for wx_ in (1030, 1120, 1250, 1340):
    add(f'<rect x="{wx_}" y="640" width="30" height="100" fill="{B1}" opacity=".75" stroke="{CH}" stroke-width="2"/>')
add(f'<path d="M1166,762 v-104 a34,34 0 0 1 68,0 v104 z" fill="{GOLD3}" stroke="{CH}" stroke-width="3"/>')
add(f'<line x1="1200" y1="624" x2="1200" y2="762" stroke="{CH}" stroke-width="3"/>')
for cx_ in (1000, 1080, 1160, 1240, 1320, 1400):
    add(f'<rect x="{cx_ - 22}" y="596" width="44" height="14" fill="{G2}" stroke="{G4}" stroke-width="2"/>')
    add(f'<rect x="{cx_ - 17}" y="610" width="34" height="140" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
    add(f'<line x1="{cx_ - 6}" y1="612" x2="{cx_ - 6}" y2="748" stroke="{G3}" stroke-width="2"/><line x1="{cx_ + 6}" y1="612" x2="{cx_ + 6}" y2="748" stroke="{G3}" stroke-width="2"/>')
    add(f'<rect x="{cx_ - 24}" y="748" width="48" height="16" fill="{G2}" stroke="{G4}" stroke-width="2"/>')
# steps
for i, (x0, x1) in enumerate(((1000, 1400), (980, 1420), (960, 1440), (940, 1460))):
    y0 = 762 + i * 22
    add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="22" fill="{G2 if i % 2 == 0 else G1}" stroke="{G4}" stroke-width="2"/>')
    add(f'<rect x="{x0}" y="{y0 + 16}" width="{x1 - x0}" height="6" fill="#000" opacity=".10"/>')
# crack in the steps
add(f'<polyline points="1128,784 1140,796 1130,806 1146,818 1138,830 1152,848" fill="none" stroke="#141618" stroke-width="3" stroke-linejoin="miter"/>')

# =====================================================================
# value question : balance scale
# =====================================================================
sx0 = 2010
add(f'<g transform="translate({sx0},0)">')
add(f'<ellipse cx="0" cy="478" rx="90" ry="12" fill="#000" opacity=".10" filter="url(#soft)"/>')
add(f'<path d="M-72,470 L72,470 L52,446 L-52,446 Z" fill="{CH2}"/>')
add(f'<rect x="-11" y="200" width="22" height="250" fill="{CH2}"/>')
add(f'<rect x="-22" y="430" width="44" height="18" fill="{CH}"/>')
ang = 7
ex = 200 * math.cos(math.radians(ang)); ey = 200 * math.sin(math.radians(ang))
lx, ly = -ex, 200 - ey
rx_, ry_ = ex, 200 + ey
pl = (lx, ly + 150); pr = (rx_, ry_ + 150)
# strings
for (bx, by, px, py) in ((lx, ly, pl[0], pl[1]), (rx_, ry_, pr[0], pr[1])):
    add(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{px - 78:.1f}" y2="{py:.1f}" stroke="{CH2}" stroke-width="3"/>')
    add(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{px + 78:.1f}" y2="{py:.1f}" stroke="{CH2}" stroke-width="3"/>')
add(f'<g transform="rotate({ang} 0 200)"><rect x="-206" y="192" width="412" height="16" rx="8" fill="{CH}"/><circle cx="-200" cy="200" r="11" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="3"/><circle cx="200" cy="200" r="11" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="3"/></g>')
add(f'<circle cx="0" cy="200" r="19" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="4"/>')

def pan(cx, cy):
    return (f'<path d="M{cx - 90:.1f},{cy:.1f} Q{cx:.1f},{cy + 62:.1f} {cx + 90:.1f},{cy:.1f} Z" fill="{CH2}"/>'
            f'<rect x="{cx - 94:.1f}" y="{cy - 5:.1f}" width="188" height="8" rx="4" fill="{GOLD}"/>')

# left pan (value): diploma + cap
add(f'<g transform="translate({pl[0]:.1f},{pl[1]:.1f})">')
add(f'<g transform="translate(-4,-22) rotate(-14)"><rect x="-58" y="-14" width="116" height="28" rx="14" fill="#F8F6F0" stroke="{CH2}" stroke-width="3"/><rect x="-14" y="-14" width="14" height="28" fill="{RED}"/><ellipse cx="58" cy="0" rx="8" ry="14" fill="#E8E4D6" stroke="{CH2}" stroke-width="3"/></g>')
add(f'<g transform="translate(-14,-70)"><polygon points="-44,0 0,-20 44,0 0,20" fill="{CH}"/><path d="M-24,8 v16 q24,14 48,0 v-16 l-24,12 z" fill="{CH2}"/><line x1="30" y1="-1" x2="30" y2="26" stroke="{GOLD2}" stroke-width="3"/><circle cx="30" cy="28" r="4" fill="{GOLD2}"/></g>')
add('</g>')
add(pan(pl[0], pl[1]))
# right pan (cost): coins + bills
add(f'<g transform="translate({pr[0]:.1f},{pr[1]:.1f})">')
for k in range(4):
    add(f'<g transform="translate(-50,{-14 - k * 15})"><ellipse cx="0" cy="8" rx="30" ry="10" fill="{GOLD3}"/><ellipse cx="0" cy="0" rx="30" ry="10" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2.5"/></g>')
for k in range(4):
    add(f'<g transform="translate({26 + k * 2},{-10 - k * 17})"><rect x="-6" y="-14" width="76" height="34" fill="{mix(B3, B2, k / 3)}" stroke="{CH2}" stroke-width="3"/><circle cx="32" cy="3" r="9" fill="none" stroke="{CH2}" stroke-width="2.5"/></g>')
add(txt(64, -52.5, "$", 15, CH, 900, "middle"))
add(f'<g transform="translate(-58,-92)"><circle r="19" fill="{RED}" stroke="{DDRED}" stroke-width="3"/>{txt(0, 9, "$", 26, "#fff", 900, "middle")}</g>')
add('</g>')
add(pan(pr[0], pr[1]))
add(txt(pl[0], pl[1] + 92, "VALUE", 20, G5, 900, "middle", 4))
add(txt(pr[0], pr[1] + 92, "COST", 20, G5, 900, "middle", 4))
add('</g>')

def bubble(x, y, w, h, text, tail="down", size=27, fill="#fff"):
    if tail == "down":
        tp = f"{x + w * .25:.0f},{y + h - 2} {x + w * .18:.0f},{y + h + 26} {x + w * .48:.0f},{y + h - 2}"
    else:
        tp = f"{x + w * .75:.0f},{y + h - 2} {x + w * .82:.0f},{y + h + 26} {x + w * .52:.0f},{y + h - 2}"
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{CH}" stroke-width="3.5"/>'
    s += f'<polygon points="{tp}" fill="{fill}" stroke="{CH}" stroke-width="3.5" stroke-linejoin="round"/>'
    mx = x + w * (.25 if tail == "down" else .52) + 3
    s += f'<rect x="{mx:.1f}" y="{y + h - 4}" width="{w * .23 - 6:.1f}" height="7.5" fill="{fill}"/>'
    s += txt(x + w / 2, y + h / 2 + size * .35, text, size, CH, 900, "middle")
    return s

add(bubble(1690, 92, 176, 58, "Worth it?", "down", 28))
add(bubble(2256, 168, 112, 56, "?!", "up", 32))
add(txt(1900, 236, "?", 74, DRED, 900, "middle", 0, .9, 'transform="rotate(-14 1900 236)"'))
add(txt(2118, 92, "?", 56, B1, 900, "middle", 0, .9, 'transform="rotate(12 2118 92)"'))
add(label(2010, 565, "Value Question", "Is a degree worth the price?"))

# =====================================================================
# rising costs
# =====================================================================
base_y = 900
# tuition statement
add(f'<g transform="translate(1690,{base_y - 250})">')
add(f'<rect x="6" y="8" width="176" height="250" fill="#000" opacity=".10" filter="url(#soft)"/>')
add(f'<rect width="176" height="250" fill="#fff" stroke="{CH2}" stroke-width="3.5"/>')
add(f'<rect width="176" height="38" fill="{RED}"/>')
add(txt(16, 26, "TUITION", 19, "#fff", 900, "start", 3))
for k in range(5):
    add(f'<rect x="16" y="{58 + k * 20}" width="{[120, 96, 128, 84, 110][k]}" height="6" fill="{G3}"/>')
    add(f'<rect x="{16 + [120, 96, 128, 84, 110][k] + 8}" y="{58 + k * 20}" width="22" height="6" fill="{G3}"/>')
add(f'<line x1="16" y1="170" x2="160" y2="170" stroke="{CH2}" stroke-width="3"/>')
add(txt(16, 214, "$", 46, CH, 900))
add(f'<rect x="60" y="192" width="70" height="8" fill="{CH2}"/><rect x="60" y="208" width="46" height="8" fill="{G3}"/>')
add(f'<polygon points="146,224 158,204 170,224" fill="{RED}"/>')
add('</g>')
# bills + coins
for k in range(5):
    yy = base_y - 24 - k * 20
    add(f'<g transform="translate({1890 + (k % 2) * 6},{yy}) skewX(-8)"><rect width="150" height="46" fill="{mix(B3, B2, k / 4)}" stroke="{CH2}" stroke-width="3"/><rect x="8" y="8" width="134" height="30" fill="none" stroke="{CH2}" stroke-width="1.6" opacity=".6"/><circle cx="75" cy="23" r="12" fill="none" stroke="{CH2}" stroke-width="2.6"/>{txt(75, 32, "$", 19, CH, 900, "middle")}</g>')
for k in range(5):
    add(f'<g transform="translate(1965,{base_y - 118 - k * 12})"><ellipse cx="0" cy="8" rx="34" ry="11" fill="{GOLD3}"/><ellipse cx="0" cy="0" rx="34" ry="11" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2.5"/></g>')
# rising bar chart
bx0 = 2110
add(f'<line x1="{bx0 - 10}" y1="{base_y}" x2="{bx0 + 240}" y2="{base_y}" stroke="{CH}" stroke-width="4"/>')
for i, h_ in enumerate((52, 84, 122, 170, 226)):
    add(f'<rect x="{bx0 + i * 48}" y="{base_y - h_}" width="36" height="{h_}" fill="{mix(B2, RED, i / 4)}" stroke="{CH2}" stroke-width="2.5"/>')
add(f'<path d="M{bx0 - 8},{base_y - 96} L{bx0 + 96},{base_y - 178} L{bx0 + 176},{base_y - 216} L{bx0 + 240},{base_y - 292}" fill="none" stroke="{RED}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round"/>')
add(f'<polygon points="{bx0 + 252},{base_y - 310} {bx0 + 212},{base_y - 296} {bx0 + 246},{base_y - 262}" fill="{RED}"/>')
add(label(2010, 1000, "Rising Costs", "Tuition and fees keep climbing"))

# =====================================================================
# alternative pathways
# =====================================================================
alt = catmull([(1440, 1150), (1540, 1185), (1650, 1190), (1730, 1150)], 16)
add(f'<polyline points="{pts_str(alt)}" fill="none" stroke="{GOLD}" stroke-width="7" stroke-dasharray="2 15" stroke-linecap="round"/>')
add(f'<g transform="translate(1744,1142) rotate(-28)"><polygon points="12,0 -14,-13 -14,13" fill="{GOLD}"/></g>')

def badge(cx, cy, icon, cap):
    s = f'<circle cx="{cx}" cy="{cy}" r="68" fill="#000" opacity=".08" filter="url(#soft)" transform="translate(4,6)"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="66" fill="#fff" stroke="{CH2}" stroke-width="4"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" stroke="{G3}" stroke-width="2"/>'
    s += f'<g transform="translate({cx},{cy})">{icon}</g>'
    s += txt(cx, cy + 102, cap, 23, CH, 700, "middle", .3)
    return s

cert = (f'<rect x="-38" y="-28" width="76" height="52" fill="#fff" stroke="{CH2}" stroke-width="3.5"/>'
        f'<rect x="-28" y="-18" width="56" height="32" fill="none" stroke="{GOLD}" stroke-width="2"/>'
        f'<rect x="-20" y="-8" width="30" height="5" fill="{G3}"/><rect x="-20" y="2" width="20" height="5" fill="{G3}"/>'
        f'<polygon points="12,14 22,14 26,38 17,32 8,38" fill="{DRED}"/><circle cx="17" cy="12" r="10" fill="{RED}" stroke="{DDRED}" stroke-width="2.5"/>')
laptop = (f'<rect x="-40" y="-32" width="80" height="52" rx="4" fill="{CH2}" stroke="{CH}" stroke-width="3"/>'
          f'<rect x="-33" y="-25" width="66" height="38" fill="{B3}"/>'
          f'<polygon points="-8,-20 -8,8 16,-6" fill="{RED}"/>'
          f'<path d="M-52,24 L52,24 L44,32 L-44,32 Z" fill="{CH2}" stroke="{CH}" stroke-width="3" stroke-linejoin="round"/>')
hat = (f'<path d="M-40,12 A40,40 0 0 1 40,12 Z" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="3.5" stroke-linejoin="round"/>'
       f'<rect x="-8" y="-30" width="16" height="42" fill="{GOLD}" stroke="{GOLD3}" stroke-width="3"/>'
       f'<rect x="-50" y="10" width="100" height="14" rx="6" fill="{GOLD}" stroke="{GOLD3}" stroke-width="3.5"/>'
       f'<path d="M-34,-4 Q-26,-22 -10,-26" fill="none" stroke="#fff" stroke-width="4" opacity=".5" stroke-linecap="round"/>')
add(badge(1820, 1138, cert, "Certificates"))
add(badge(2010, 1138, laptop, "Online learning"))
add(badge(2200, 1138, hat, "Apprenticeships"))
add(label(2010, 1322, "Alternative Pathways", "Credentials, online learning, trades"))

# =====================================================================
# federal research funding landscape
# =====================================================================
fx, by = 2630, 560
add(f'<ellipse cx="{fx}" cy="{by + 8}" rx="180" ry="13" fill="#000" opacity=".12" filter="url(#soft)"/>')
for x0 in (fx - 178, fx + 100):
    add(f'<rect x="{x0}" y="{by - 88}" width="78" height="76" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
    add(f'<rect x="{x0 - 6}" y="{by - 96}" width="90" height="10" fill="{CH3}"/>')
    for wx in (x0 + 14, x0 + 46):
        add(f'<rect x="{wx}" y="{by - 72}" width="18" height="34" fill="{B1}" stroke="{CH3}" stroke-width="2"/>')
add(f'<rect x="{fx - 40}" y="{by - 196}" width="80" height="92" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
add(f'<path d="M{fx - 48},{by - 196} A48,50 0 0 1 {fx + 48},{by - 196} Z" fill="url(#dome)" stroke="{GOLD3}" stroke-width="2.5"/>')
add(f'<rect x="{fx - 6}" y="{by - 262}" width="12" height="20" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2"/>')
add(f'<circle cx="{fx}" cy="{by - 268}" r="6" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2"/>')
add(f'<rect x="{fx - 100}" y="{by - 108}" width="200" height="96" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
add(f'<polygon points="{fx - 112},{by - 106} {fx},{by - 146} {fx + 112},{by - 106}" fill="url(#stone)" stroke="{G4}" stroke-width="2.5" stroke-linejoin="round"/>')
add(f'<rect x="{fx - 94}" y="{by - 104}" width="188" height="88" fill="#4A5058"/>')
for i in range(6):
    cxx = fx - 80 + i * 32
    add(f'<rect x="{cxx - 7}" y="{by - 102}" width="14" height="86" fill="url(#stone)" stroke="{G4}" stroke-width="2"/>')
add(f'<rect x="{fx - 112}" y="{by - 14}" width="224" height="14" fill="{G2}" stroke="{G4}" stroke-width="2"/>')
add(f'<rect x="{fx - 124}" y="{by}" width="248" height="12" fill="{G3}" stroke="{G4}" stroke-width="2"/>')
# the pipeline: valve nearly closed, funding reduced to drips
py0 = by + 12
add(f'<rect x="{fx - 11}" y="{py0}" width="22" height="122" fill="{CH2}" stroke="{CH}" stroke-width="3"/>')
for fy in (py0, py0 + 112):
    add(f'<rect x="{fx - 19}" y="{fy}" width="38" height="10" fill="{CH}"/>')
add(f'<rect x="{fx - 17}" y="{py0 + 44}" width="34" height="26" rx="4" fill="{CH}"/>')
add(f'<line x1="{fx + 17}" y1="{py0 + 57}" x2="{fx + 44}" y2="{py0 + 57}" stroke="{CH}" stroke-width="7"/>')
add(f'<g transform="translate({fx + 56},{py0 + 57})"><circle r="21" fill="none" stroke="{RED}" stroke-width="7"/><line x1="-21" y1="0" x2="21" y2="0" stroke="{RED}" stroke-width="5"/><line x1="0" y1="-21" x2="0" y2="21" stroke="{RED}" stroke-width="5"/><circle r="5" fill="{RED}"/></g>')
add(f'<path d="M{fx - 11},{py0 + 122} L{fx - 4},{py0 + 146} L{fx + 4},{py0 + 146} L{fx + 11},{py0 + 122} Z" fill="{CH}"/>')
for dy, r, op in ((py0 + 172, 12, .95), (py0 + 216, 9.5, .6), (py0 + 250, 7.5, .35)):
    add(f'<g opacity="{op}"><circle cx="{fx}" cy="{dy}" r="{r}" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="2.5"/><circle cx="{fx}" cy="{dy}" r="{r * .62:.1f}" fill="none" stroke="{GOLD3}" stroke-width="1.6"/></g>')
# the lab: beaker with a low level against the dashed prior level, flask, microscope
bt, bb = 858, 1000
add(f'<ellipse cx="{fx}" cy="{bb + 5}" rx="200" ry="12" fill="#000" opacity=".12" filter="url(#soft)"/>')
add(f'<path d="M{fx - 52},{bt} L{fx - 52},{bb - 10} Q{fx - 52},{bb} {fx - 42},{bb} L{fx + 42},{bb} Q{fx + 52},{bb} {fx + 52},{bb - 10} L{fx + 52},{bt}" fill="#fff" fill-opacity=".45" stroke="{B1}" stroke-width="5" stroke-linecap="round"/>')
add(f'<path d="M{fx - 47},{bb - 40} L{fx + 47},{bb - 40} L{fx + 47},{bb - 11} Q{fx + 47},{bb - 5} {fx + 41},{bb - 5} L{fx - 41},{bb - 5} Q{fx - 47},{bb - 5} {fx - 47},{bb - 11} Z" fill="{GOLD2}" opacity=".85"/>')
for ty in range(bt + 40, bb - 44, 24):
    add(f'<line x1="{fx - 47}" y1="{ty}" x2="{fx - 32}" y2="{ty}" stroke="{B1}" stroke-width="3"/>')
add(f'<line x1="{fx - 68}" y1="{bt + 26}" x2="{fx + 68}" y2="{bt + 26}" stroke="{RED}" stroke-width="4" stroke-dasharray="10 7"/>')
add(f'<line x1="{fx + 84}" y1="{bt + 26}" x2="{fx + 84}" y2="{bb - 52}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>')
add(f'<polygon points="{fx + 84},{bb - 32} {fx + 72},{bb - 54} {fx + 96},{bb - 54}" fill="{RED}"/>')
fk = fx - 142
add(f'<path d="M{fk - 12},{bb - 100} L{fk + 12},{bb - 100} L{fk + 12},{bb - 62} L{fk + 46},{bb - 8} Q{fk + 50},{bb} {fk + 40},{bb} L{fk - 40},{bb} Q{fk - 50},{bb} {fk - 46},{bb - 8} L{fk - 12},{bb - 62} Z" fill="#fff" fill-opacity=".45" stroke="{B1}" stroke-width="5" stroke-linejoin="round"/>')
add(f'<path d="M{fk - 28},{bb - 30} L{fk + 28},{bb - 30} L{fk + 41},{bb - 8} Q{fk + 44},{bb - 4} {fk + 36},{bb - 4} L{fk - 36},{bb - 4} Q{fk - 44},{bb - 4} {fk - 41},{bb - 8} Z" fill="{RED}" opacity=".75"/>')
add(f'<rect x="{fk - 16}" y="{bb - 106}" width="32" height="8" rx="3" fill="{B1}"/>')
mx = fx + 138
g = f'<g transform="translate({mx},{bb})">'
g += f'<rect x="-36" y="-12" width="72" height="12" rx="3" fill="{CH2}"/>'
g += f'<path d="M18,-12 C46,-34 46,-92 10,-122" fill="none" stroke="{CH2}" stroke-width="13" stroke-linecap="round"/>'
g += f'<rect x="-30" y="-40" width="44" height="7" rx="2" fill="{CH2}"/>'
g += f'<g transform="rotate(-22 -6 -100)"><rect x="-13" y="-128" width="26" height="70" rx="4" fill="{B1}" stroke="{CH}" stroke-width="3"/><rect x="-9" y="-146" width="18" height="20" rx="3" fill="{CH2}"/><rect x="-7" y="-58" width="14" height="14" fill="{CH}"/></g>'
add(g + '</g>')
add(label2(fx, 1078, ["Federal Research", "Funding Landscape"], "Research dollars under pressure"))

# =====================================================================
# Northeastern wordmark (supplied by Brett, placed unmodified on white with clear space)
# =====================================================================
logo_b64 = base64.b64encode(open(os.path.join(SP, "northeastern-wordmark.png"), "rb").read()).decode()
LOGO_W = 300; LOGO_H = LOGO_W * 84 / 500
LOGO_P = []
PW, PH = 380, 102
PX, PY = W - 30 - PW, H - 20 - PH
LOGO_P.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="#fff" stroke="{G3}" stroke-width="2"/>')
LOGO_P.append(f'<image x="{PX + (PW - LOGO_W) / 2:.1f}" y="{PY + (PH - LOGO_H) / 2:.1f}" width="{LOGO_W}" height="{LOGO_H:.1f}" href="data:image/png;base64,{logo_b64}"/>')

# =====================================================================
# THE PRESIDENT (cartoon)
# =====================================================================
add('<g transform="translate(1195,1472) scale(.82)">')
add('<ellipse cx="0" cy="6" rx="215" ry="26" fill="#000" opacity=".22" filter="url(#soft)"/>')
NAVY = "#1B2C4E"; NAVY2 = "#243B66"; SKIN = "#EDC5A9"; SKIN2 = "#D9A88B"
# legs and shoes
add(f'<path d="M-82,-235 L-8,-235 L-14,-24 L-74,-24 Z" fill="#16233F" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M8,-235 L82,-235 L74,-24 L14,-24 Z" fill="#16233F" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M-92,-26 Q-96,-6 -76,-2 L-4,-2 Q4,-12 -8,-26 Z" fill="{CH}"/>')
add(f'<path d="M92,-26 Q96,-6 76,-2 L4,-2 Q-4,-12 8,-26 Z" fill="{CH}"/>')
add(f'<path d="M-84,-14 Q-56,-8 -12,-12" stroke="#fff" stroke-width="3" opacity=".25" fill="none" stroke-linecap="round"/>')
# right arm (image right) raised, behind torso edge
add(f'<polyline points="118,-452 206,-406 252,-482" fill="none" stroke="{CH}" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>')
add(f'<polyline points="118,-452 206,-406 252,-482" fill="none" stroke="{NAVY}" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/>')
add(f'<polyline points="130,-458 204,-420" fill="none" stroke="{NAVY2}" stroke-width="10" stroke-linecap="round" opacity=".6"/>')
# left arm (image left) — behind shield
add(f'<polyline points="-118,-452 -186,-372 -206,-420" fill="none" stroke="{CH}" stroke-width="58" stroke-linecap="round" stroke-linejoin="round"/>')
add(f'<polyline points="-118,-452 -186,-372 -206,-420" fill="none" stroke="{NAVY}" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/>')
# torso
add(f'<path d="M-142,-436 Q-142,-492 -92,-500 L92,-500 Q142,-492 142,-436 L124,-196 Q0,-170 -124,-196 Z" fill="{NAVY}" stroke="{CH}" stroke-width="5" stroke-linejoin="round"/>')
add(f'<path d="M-124,-196 Q0,-170 124,-196 L120,-222 Q0,-198 -120,-222 Z" fill="#000" opacity=".14"/>')
# shirt V
add(f'<path d="M-52,-505 L0,-330 L52,-505 Z" fill="#FFFFFF" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
# collar
add(f'<path d="M-54,-512 L-10,-482 L-38,-444 L-62,-490 Z" fill="#fff" stroke="{CH}" stroke-width="3.5" stroke-linejoin="round"/>')
add(f'<path d="M54,-512 L10,-482 L38,-444 L62,-490 Z" fill="#fff" stroke="{CH}" stroke-width="3.5" stroke-linejoin="round"/>')
# lapels
add(f'<path d="M-62,-500 L-126,-472 L-98,-392 L-2,-326 L-40,-400 Z" fill="{NAVY2}" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M62,-500 L126,-472 L98,-392 L2,-326 L40,-400 Z" fill="{NAVY2}" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M-2,-326 L-6,-240 M2,-326 L6,-240" stroke="{CH}" stroke-width="4" fill="none" stroke-linecap="round"/>')
# tie
add(f'<g><path d="M-14,-482 L14,-482 L11,-460 L32,-352 L0,-316 L-32,-352 L-11,-460 Z" fill="url(#tiepat)"/>')
add(f'<path d="M-14,-482 L14,-482 L11,-460 L32,-352 L0,-316 L-32,-352 L-11,-460 Z" fill="none" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
add(f'<path d="M-17,-486 L17,-486 L14,-462 L-14,-462 Z" fill="#3F78C6" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/></g>')
# lapel pin (flower)
fx, fy = 96, -424
add(f'<g transform="translate({fx},{fy})">')
for a_ in range(0, 360, 72):
    add(f'<ellipse cx="0" cy="-15" rx="11" ry="16" transform="rotate({a_ + 18})" fill="{"#A9BDD0" if a_ % 144 == 0 else "#DCE6F0"}" stroke="{B1}" stroke-width="2.5"/>')
add(f'<circle r="7" fill="#fff" stroke="{B1}" stroke-width="2.5"/></g>')
# neck
add(f'<path d="M-34,-520 L-34,-486 Q0,-462 34,-486 L34,-520 Z" fill="{SKIN2}" stroke="{CH}" stroke-width="4" stroke-linejoin="round"/>')
# head
add('<g transform="translate(0,-480) scale(1.1) translate(0,480)">')
add(f'<ellipse cx="-100" cy="-590" rx="15" ry="28" fill="{SKIN}" stroke="{CH}" stroke-width="4"/>')
add(f'<ellipse cx="100" cy="-590" rx="15" ry="28" fill="{SKIN}" stroke="{CH}" stroke-width="4"/>')
add(f'<path d="M-100,-598 q-8,10 0,26 M100,-598 q8,10 0,26" stroke="{SKIN2}" stroke-width="4" fill="none" stroke-linecap="round"/>')
add(f'<path d="M-99,-592 C-99,-694 -56,-716 0,-716 C56,-716 99,-694 99,-592 C99,-536 70,-476 0,-472 C-70,-476 -99,-536 -99,-592 Z" fill="{SKIN}" stroke="{CH}" stroke-width="5" stroke-linejoin="round"/>')
add(f'<path d="M-99,-560 C-90,-500 -50,-478 0,-474 C50,-478 90,-500 99,-560 C86,-514 50,-492 0,-490 C-50,-492 -86,-514 -99,-560 Z" fill="{SKIN2}" opacity=".55"/>')
add(f'<ellipse cx="-34" cy="-672" rx="38" ry="15" transform="rotate(-24 -34 -672)" fill="#fff" opacity=".45"/>')
# cheeks
add(f'<ellipse cx="-62" cy="-528" rx="16" ry="9" fill="#E59A8B" opacity=".35"/><ellipse cx="62" cy="-528" rx="16" ry="9" fill="#E59A8B" opacity=".35"/>')
# eyebrows (determined)
add(f'<path d="M-86,-650 Q-56,-668 -16,-644" stroke="#4E3F37" stroke-width="10" fill="none" stroke-linecap="round"/>')
add(f'<path d="M86,-650 Q56,-668 16,-644" stroke="#4E3F37" stroke-width="10" fill="none" stroke-linecap="round"/>')
# eyes
for ex_, sgn in ((-44, 1), (44, 1)):
    add(f'<ellipse cx="{ex_}" cy="-592" rx="19" ry="14" fill="#fff"/>')
    add(f'<circle cx="{ex_ - 5}" cy="-591" r="9.5" fill="#6B4423"/><circle cx="{ex_ - 5}" cy="-591" r="4.6" fill="#120c08"/><circle cx="{ex_ - 8}" cy="-595" r="2.6" fill="#fff"/>')
    add(f'<path d="M{ex_ - 20},-598 Q{ex_},-614 {ex_ + 20},-598" stroke="{CH}" stroke-width="4" fill="none" stroke-linecap="round"/>')
# glasses
for gx_ in (-44, 44):
    add(f'<circle cx="{gx_}" cy="-592" r="41" fill="#fff" fill-opacity=".14" stroke="#6F5F35" stroke-width="10"/>')
    add(f'<circle cx="{gx_}" cy="-592" r="41" fill="none" stroke="#A8935C" stroke-width="3" stroke-dasharray="14 7" opacity=".9"/>')
    add(f'<path d="M{gx_ - 26},-620 Q{gx_ - 8},-628 {gx_ + 8},-624" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" opacity=".55"/>')
add(f'<path d="M-6,-598 Q0,-606 6,-598" stroke="#7F92A8" stroke-width="7" fill="none" stroke-linecap="round"/>')
add(f'<path d="M-85,-598 L-101,-594 M85,-598 L101,-594" stroke="#7F92A8" stroke-width="7" stroke-linecap="round"/>')
# nose & mouth
add(f'<path d="M-4,-574 Q-16,-540 -6,-528 Q6,-520 18,-530" stroke="#C99476" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
add(f'<path d="M-34,-504 Q0,-486 36,-510" stroke="#8A4A3A" stroke-width="6" fill="none" stroke-linecap="round"/>')
add(f'<path d="M-40,-508 Q-44,-514 -42,-520 M42,-514 Q46,-520 44,-526" stroke="#C99476" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
add(f'<path d="M-66,-548 Q-62,-520 -40,-508" stroke="#C99476" stroke-width="3.5" fill="none" stroke-linecap="round" opacity=".7"/>')

add('</g>')
# ----- shield (in front of left arm) -----
add(f'<path d="M-350,-500 L-180,-500 L-180,-390 Q-180,-300 -265,-258 Q-350,-300 -350,-390 Z" fill="{RED}" stroke="{CH}" stroke-width="6" stroke-linejoin="round"/>')
add('<g clip-path="url(#shieldclip)">')
add(f'<path d="M-350,-500 L-180,-500 L-180,-462 L-350,-424 Z" fill="#fff" opacity=".10"/>')
add(f'<path d="M-265,-505 L-180,-505 L-180,-300 L-265,-258 Z" fill="#000" opacity=".10"/>')
add('</g>')
add(f'<path d="M-338,-488 L-192,-488 L-192,-392 Q-192,-312 -265,-274 Q-338,-312 -338,-392 Z" fill="none" stroke="{GOLD2}" stroke-width="5" stroke-linejoin="round"/>')
add(husky(-274, -418, 0.9))
# hand on the shield
add(f'<circle cx="-196" cy="-408" r="21" fill="{SKIN}" stroke="{CH}" stroke-width="4"/>')
add(f'<path d="M-208,-420 q-2,10 4,18 M-198,-424 q-2,12 4,22" stroke="{SKIN2}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
# white cuff
add(f'<path d="M-214,-386 L-180,-376" stroke="#fff" stroke-width="9" stroke-linecap="round"/>')

# ----- diploma "sword" -----
add('<g transform="translate(252,-482) rotate(-52)">')
add(f'<rect x="-84" y="-19" width="330" height="38" rx="19" fill="#F8F6F0" stroke="{CH}" stroke-width="5"/>')
add(f'<rect x="-84" y="4" width="330" height="15" rx="8" fill="#000" opacity=".08"/>')
add(f'<ellipse cx="246" cy="0" rx="10" ry="19" fill="#E3DECD" stroke="{CH}" stroke-width="4.5"/><ellipse cx="246" cy="0" rx="4" ry="9" fill="none" stroke="{CH}" stroke-width="2.5"/>')
add(f'<rect x="70" y="-21" width="24" height="42" fill="{RED}" stroke="{DDRED}" stroke-width="2.5"/>')
add(f'<path d="M82,10 l-18,40 l16,-8 l8,16 z M82,10 l20,38 l-16,-8 l-6,14 z" fill="{RED}" stroke="{DDRED}" stroke-width="2.5" stroke-linejoin="round"/>')
add(f'<circle cx="0" cy="0" r="24" fill="{SKIN}" stroke="{CH}" stroke-width="5"/>')
add(f'<path d="M-9,-20 q3,14 -1,38 M6,-22 q3,16 0,42" stroke="{SKIN2}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
add('</g>')
add(f'<path d="M380,-660 Q470,-600 470,-490" fill="none" stroke="{GOLD2}" stroke-width="7" stroke-linecap="round" stroke-dasharray="26 14" opacity=".9"/>')
add(f'<path d="M340,-690 Q470,-640 500,-520" fill="none" stroke="{GOLD}" stroke-width="4" stroke-linecap="round" opacity=".45"/>')

# ----- deflected challenges -----
def sparks(cx, cy, n=8, r0=26, r1=54, col=GOLD2, a0=0):
    s = f'<g stroke="{col}" stroke-width="6" stroke-linecap="round">'
    for k in range(n):
        a = math.radians(a0 + k * 360 / n)
        s += f'<line x1="{cx + r0 * math.cos(a):.0f}" y1="{cy + r0 * math.sin(a):.0f}" x2="{cx + r1 * math.cos(a):.0f}" y2="{cy + r1 * math.sin(a):.0f}"/>'
    return s + '</g>'

add(sparks(-352, -470, 7, 24, 52, GOLD2, 100))
add(f'<g transform="translate(-455,-568) rotate(-18)"><rect x="-46" y="-40" width="92" height="76" rx="14" fill="#fff" stroke="{CH}" stroke-width="4.5"/><polygon points="18,34 34,58 -2,34" fill="#fff" stroke="{CH}" stroke-width="4.5" stroke-linejoin="round"/><rect x="-14" y="30" width="24" height="9" fill="#fff"/>{txt(0, 18, "?", 62, RED, 900, "middle")}</g>')
add(sparks(452, -690, 7, 22, 46, RED, 10))
add(f'<g transform="translate(500,-720) rotate(16)"><circle r="34" fill="{GOLD2}" stroke="{GOLD3}" stroke-width="4.5"/><circle r="24" fill="none" stroke="{GOLD3}" stroke-width="2.5"/>{txt(0, 13, "$", 38, GOLD3, 900, "middle")}</g>')
add('</g>')

# =====================================================================
add(f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="n"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".09"/></feComponentTransfer></filter>')
add(f'<rect width="{W}" height="{H}" filter="url(#grain)" style="mix-blend-mode:multiply"/>')
P.extend(LOGO_P)
add('</svg>')

svg = "\n".join(P)
open(os.path.join(SP, "higher_ed_challenges.svg"), "w").write(svg)
print("svg bytes:", len(svg))
