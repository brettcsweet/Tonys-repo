#!/usr/bin/env python3
"""Build the two-page peer endowment report from data/endowments.json.

Page 1: table of the top 50 private universities (US News 2027) with FY26
return and FY25 / FY26 endowment market value.
Page 2: board graphic, FY26 returns sorted highest to lowest.

Schools that have not reported yet carry placeholder numbers. Placeholders are
computed here (never stored as if real) and are flagged on both pages.

Usage: python3 scripts/build_report.py
"""
import html
import json
import statistics
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "endowments.json"
OUT = ROOT / "report" / "endowment-returns.html"

HOME = "Northeastern University"
SPEND = 0.045  # assumed net payout used only to roll a placeholder FY26 value


def esc(s):
    return html.escape(str(s), quote=True)


def load():
    d = json.loads(DATA.read_text())
    schools = d["schools"]
    reported = [s["fy26_return"] for s in schools if s.get("fy26_return") is not None]
    median = statistics.median(reported) if reported else None
    ph = d["placeholder"]["return"]
    for s in schools:
        s["ret_est"] = s.get("fy26_return") is None
        s["ret"] = ph if s["ret_est"] else s["fy26_return"]
        s["v25_est"] = s.get("fy25_value") is None
        s["v25"] = s.get("fy25_value")
        s["v26_est"] = s.get("fy26_value") is None
        if s["v26_est"] and s["v25"] is not None:
            s["v26"] = s["v25"] * (1 + s["ret"] / 100 - SPEND)
        else:
            s["v26"] = s.get("fy26_value")
    return d, schools, median, len(reported)


def fmt_b(v, est):
    if v is None:
        return '<span class="na">n/a</span>'
    txt = f"${v:,.1f}B" if v >= 1 else f"${v * 1000:,.0f}M"
    return f'<span class="est">{txt}</span>' if est else txt


def fmt_ret(s):
    txt = f"{s['ret']:.1f}%"
    return f'<span class="est">{txt}</span>' if s["ret_est"] else txt


def table_rows(rows):
    out = []
    for s in rows:
        cls = ' class="home"' if s["school"] == HOME else ""
        out.append(
            f"<tr{cls}><td class=\"num rk\">{esc(s['usnews_rank'])}</td>"
            f"<td class=\"name\">{esc(s['short'])}</td>"
            f"<td class=\"num\">{fmt_ret(s)}</td>"
            f"<td class=\"num\">{fmt_b(s['v25'], s['v25_est'])}</td>"
            f"<td class=\"num\">{fmt_b(s['v26'], s['v26_est'])}</td></tr>"
        )
    return "\n".join(out)


def table_block(rows):
    return f"""<table>
<thead><tr><th class="num">US News</th><th>University</th><th class="num">FY26 return</th>
<th class="num">FY25 MV</th><th class="num">FY26 MV</th></tr></thead>
<tbody>
{table_rows(rows)}
</tbody></table>"""


def chart_svg(schools, median, ph):
    rows = sorted(schools, key=lambda s: (-s["ret"], s["ret_est"], s["short"]))
    W, H = 1200, 520
    left, right, top, bottom = 48, 16, 24, 118
    pw, ph = W - left - right, H - top - bottom
    hi = max(s["ret"] for s in rows)
    lo = min(0.0, min(s["ret"] for s in rows))
    step = 5
    vmax = step * (int(hi // step) + 1)
    vmin = -step * (int(-lo // step) + (1 if lo < 0 else 0))
    y = lambda v: top + ph * (vmax - v) / (vmax - vmin)
    n = len(rows)
    slot = pw / n
    bw = slot - 4
    parts = []
    t = vmin
    while t <= vmax + 1e-9:
        parts.append(f'<line x1="{left}" x2="{W - right}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/>')
        parts.append(f'<text x="{left - 8}" y="{y(t) + 4:.1f}" class="tick" text-anchor="end">{t:.0f}%</text>')
        t += step
    for i, s in enumerate(rows):
        x = left + i * slot + 2
        y0, y1 = y(0), y(s["ret"])
        ytop, h = min(y0, y1), max(abs(y1 - y0), 1)
        if s["school"] == HOME:
            cls = "bar home-bar" if not s["ret_est"] else "bar home-est"
        else:
            cls = "bar est-bar" if s["ret_est"] else "bar"
        tip = f"{s['school']}: {s['ret']:.1f}%" + (" (placeholder)" if s["ret_est"] else "")
        parts.append(
            f'<rect x="{x:.1f}" y="{ytop:.1f}" width="{bw:.1f}" height="{h:.1f}" class="{cls}">'
            f"<title>{esc(tip)}</title></rect>"
        )
        if not s["ret_est"]:
            inside = h > 18
            ly = (ytop + 12 if inside else ytop - 5) if s["ret"] >= 0 else ytop + h + 12
            vcls = "val val-in" if inside else "val"
            parts.append(
                f'<text x="{x + bw / 2:.1f}" y="{ly:.1f}" class="{vcls}" text-anchor="middle">{s["ret"]:.1f}</text>'
            )
        lx, lyy = x + bw / 2, y(min(0, vmin if s["ret"] < 0 else 0)) + 10
        lyy = y(vmin) + 10 if vmin < 0 else y(0) + 10
        name_cls = "lbl home-lbl" if s["school"] == HOME else ("lbl est-lbl" if s["ret_est"] else "lbl")
        parts.append(
            f'<text transform="translate({lx + 3:.1f},{lyy:.1f}) rotate(-60)" class="{name_cls}" text-anchor="end">{esc(s["short"])}</text>'
        )
    parts.append(f'<line x1="{left}" x2="{W - right}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="axis"/>')
    if median is None:
        return svg_wrap(W, H, parts)
    ym = y(median)
    parts.append(f'<line x1="{left}" x2="{W - right}" y1="{ym:.1f}" y2="{ym:.1f}" class="median"/>')
    parts.append(
        f'<text x="{W - right - 4}" y="{ym - 6:.1f}" class="median-lbl" text-anchor="end">Median of reported: {median:.1f}%</text>'
    )
    return svg_wrap(W, H, parts)


def svg_wrap(W, H, parts):
    return (
        f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="FY26 endowment returns, highest to lowest">'
        + "".join(parts)
        + "</svg>"
    )


def build():
    d, schools, median, n_rep = load()
    ph = d["placeholder"]["return"]
    ph_label = esc(d["placeholder"]["label"])
    schools.sort(key=lambda s: s["private_rank"])
    n = len(schools)
    rep = [s for s in schools if not s["ret_est"]]
    best = max(rep, key=lambda s: s["fy26_return"]) if rep else None
    worst = min(rep, key=lambda s: s["fy26_return"]) if rep else None
    home = next((s for s in schools if s["school"] == HOME), None)
    v25_real = [s for s in schools if not s["v25_est"]]
    half = (n + 1) // 2
    as_of = d.get("as_of", date.today().isoformat())
    as_of_txt = date.fromisoformat(as_of).strftime("%B %-d, %Y")

    home_line = ""
    if home:
        if home["ret_est"]:
            home_line = "<li>Northeastern FY26 return not yet published; shown at the placeholder rate.</li>"
        else:
            pos = sorted(rep, key=lambda s: -s["fy26_return"]).index(home) + 1
            home_line = f"<li>Northeastern returned <b>{home['fy26_return']:.1f}%</b>, No. {pos} of {n_rep} reported.</li>"
    bullets = [
        f"<li><b>{n_rep} of {n}</b> schools have reported FY26 returns; the rest show a placeholder of {ph:.1f}% ({ph_label}).</li>"
    ]
    if best and worst:
        bullets.append(
            f"<li>Reported range: <b>{best['fy26_return']:.1f}%</b> ({esc(best['short'])}) to <b>{worst['fy26_return']:.1f}%</b> ({esc(worst['short'])}).</li>"
        )
    bullets.append(home_line)

    page = f"""<title>Peer Endowment Returns FY26</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap">
<style>
:root {{
  --red: #C8102E; --ink: #000; --ink2: #3a3a3a; --muted: #6b6b6b; --rule: #000;
  --hair: #d9d9d9; --paper: #fff; --gold: #A4804A; --est: #8f8f8f; --canvas: #efefef;
  color-scheme: light;
}}
body {{ background: var(--canvas); color: var(--ink); font-family: Lato, "Helvetica Neue", Arial, sans-serif;
  padding-inline: 16px; padding-block: 24px; }}
.slide {{ background: var(--paper); max-width: 1280px; margin: 0 auto 24px; padding: 36px 44px 20px;
  display: flex; flex-direction: column; gap: 14px; border-top: 6px solid var(--red); }}
.kicker {{ font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--red); margin: 0; }}
h1 {{ font-size: 28px; font-weight: 900; margin: 0; text-wrap: balance; line-height: 1.15; }}
.sub {{ font-size: 14px; color: var(--ink2); margin: 0; }}
.tables {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }}
.tables > div {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; font-variant-numeric: tabular-nums; background: var(--paper); }}
th {{ text-align: left; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: .05em;
  border-bottom: 2px solid var(--rule); padding: 4px 6px; white-space: nowrap; vertical-align: bottom; }}
td {{ padding: 3px 6px; border-bottom: 1px solid var(--hair); white-space: nowrap; }}
tbody tr:last-child td {{ border-bottom: 1px solid var(--rule); }}
.num {{ text-align: right; }}
td.rk {{ color: var(--muted); }}
tr.home td {{ font-weight: 900; color: var(--red); }}
.est {{ color: var(--muted); font-style: italic; }}
.est::after {{ content: "*"; }}
.na {{ color: var(--muted); }}
ul.pts {{ margin: 0; padding-left: 18px; font-size: 15px; line-height: 1.5; display: grid; gap: 2px; }}
.chart {{ overflow-x: auto; }}
.chart svg {{ width: 100%; min-width: 760px; height: auto; display: block; }}
.grid {{ stroke: var(--hair); stroke-width: 1; }}
.axis {{ stroke: var(--ink); stroke-width: 1.5; }}
.tick {{ font-size: 12px; fill: var(--muted); }}
.bar {{ fill: #262626; }}
.bar:hover {{ fill: #555; }}
.home-bar {{ fill: var(--red); }}
.est-bar {{ fill: #f4f4f4; stroke: var(--est); stroke-width: 1; stroke-dasharray: 3 2; }}
.home-est {{ fill: var(--paper); stroke: var(--red); stroke-width: 1.5; stroke-dasharray: 3 2; }}
.val {{ font-size: 9.5px; fill: var(--ink2); font-weight: 700; }}
.val-in {{ fill: #fff; }}
.lbl {{ font-size: 10.5px; fill: var(--ink2); }}
.est-lbl {{ fill: var(--muted); font-style: italic; }}
.home-lbl {{ fill: var(--red); font-weight: 900; }}
.median {{ stroke: var(--gold); stroke-width: 1.5; stroke-dasharray: 6 4; }}
.median-lbl {{ font-size: 12px; fill: var(--gold); font-weight: 700; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 18px; font-size: 12px; color: var(--ink2); align-items: center; }}
.sw {{ display: inline-block; width: 12px; height: 12px; vertical-align: -2px; margin-right: 6px; }}
.note {{ font-size: 11px; color: var(--muted); margin: 0; line-height: 1.45; }}
footer {{ display: flex; justify-content: space-between; gap: 16px; border-top: 1px solid var(--rule);
  padding-top: 8px; font-size: 11px; color: var(--ink2); flex-wrap: wrap; }}
footer b {{ color: var(--ink); white-space: nowrap; margin-left: auto; }}
@media (max-width: 900px) {{ .tables {{ grid-template-columns: 1fr; }} .slide {{ padding: 24px 18px 14px; }} h1 {{ font-size: 22px; }} }}
</style>

<section class="slide" id="table">
  <p class="kicker">Peer endowment performance &middot; Fiscal year 2026</p>
  <h1>FY26 endowment returns and market value, top 50 private universities</h1>
  <p class="sub">Peer set: top 50 private national universities, U.S. News &amp; World Report 2027. Market value in $ billions at fiscal year end (June 30 unless noted). Status as of {as_of_txt}: {n_rep} of {n} returns reported; FY25 value found for {len(v25_real)} of {n}.</p>
  <div class="tables">
    <div>{table_block(schools[:half])}</div>
    <div>{table_block(schools[half:])}</div>
  </div>
  <p class="note">* Grey italic = placeholder until the school publishes. Placeholder return = {ph:.1f}%, the {ph_label}; placeholder FY26 value = FY25 value &times; (1 + placeholder return &minus; {SPEND * 100:.1f}% assumed payout). Returns are net of fees as reported by each school; some schools report a pooled fund (e.g., Stanford Merged Pool). Northeastern FY26 value is from the internal fund file (1,799 funds). Details and source links: data/endowments.json.</p>
  <footer><span>Source: university reports and press releases; Bloomberg; Chief Investment Officer; Pensions &amp; Investments; student newspapers; U.S. News 2027.</span><b>{HOME}</b></footer>
</section>

<section class="slide" id="chart">
  <p class="kicker">Peer endowment performance &middot; Fiscal year 2026</p>
  <h1>FY26 endowment returns, highest to lowest</h1>
  <ul class="pts">{"".join(bullets)}</ul>
  <div class="legend">
    <span><i class="sw" style="background:#262626"></i>Reported</span>
    <span><i class="sw" style="background:var(--red)"></i>Northeastern</span>
    <span><i class="sw" style="background:#fff;border:1px dashed var(--est)"></i>Placeholder (not yet reported)</span>
    <span><i class="sw" style="height:0;border-top:2px dashed var(--gold)"></i>Median of reported</span>
  </div>
  <div class="chart">{chart_svg(schools, median, ph)}</div>
  <footer><span>Source: university reports and press releases; Bloomberg; Chief Investment Officer; Pensions &amp; Investments. As of {as_of_txt}.</span><b>{HOME}</b></footer>
</section>
"""
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}: {n} schools, {n_rep} reported, median {median}")


if __name__ == "__main__":
    build()
