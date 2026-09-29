"""Backup workbook: data behind the three slides, live formulas, evidence, calibration and checks.
usage: python3 build_backup.py <out.xlsx>   (run from nu-peer-slides/pipeline; reads inputs/)"""
import sys, json
import numpy as np, pandas as pd, openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1]
RED = "C8102E"
def font(**k): return Font(name="Lato", size=k.pop("size", 10), **k)
HB = Border(bottom=Side(style="thin", color="000000"))

def title(ws, text, sub=None):
    ws["A1"] = text; ws["A1"].font = font(bold=True, size=14, color=RED)
    if sub: ws["A2"] = sub; ws["A2"].font = font(size=9, color="6B6B70")

def header(ws, row, labels, widths=None):
    for i, l in enumerate(labels, 1):
        c = ws.cell(row, i, l); c.font = font(bold=True); c.border = HB
        c.alignment = Alignment(wrap_text=True, vertical="bottom")
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w

def put(ws, r, c, v, fmt=None, bold=False, color="000000", wrap=False):
    cell = ws.cell(r, c, v); cell.font = font(bold=bold, color=color)
    if fmt: cell.number_format = fmt
    if wrap: cell.alignment = Alignment(wrap_text=True, vertical="top")
    return cell

wb = Workbook()

# ============================================================== README
ws = wb.active; ws.title = "README"
title(ws, "Peer slides: backup data, evidence and checks", "Every derived number is a live formula. Sources and verbatim evidence are on the Evidence sheet.")
lines = [
    ("Slide 1", "S1_Scorecard: College Scorecard institution-level file, release of June 10, 2026, same filters as the original slide (1,527 institutions)."),
    ("Slide 2", "S2_Survey: Inside Higher Ed business-officer survey 2015-2026, re-read from the report PDFs; the original slide's values and the differences are shown."),
    ("Slide 3", "S3_FY25: FY25 audited statements (plus Form 990 / MD&A where the audited statements combine salaries and benefits). S3_Sensitivity, S3_FY23_Recalc and S3_Enrollment test the assumptions."),
    ("Evidence", "Verbatim source rows and document links for each FY25 figure."),
    ("Checks", "Every test run and every disconnect found, with status."),
    ("Data_needed", "What is still open (Harvard FY25 report; Northeastern headcount confirmation; Penn / Stanford salaries and wages)."),
]
for i, (a, b) in enumerate(lines, 4):
    put(ws, i, 1, a, bold=True); put(ws, i, 2, b, wrap=True)
ws.column_dimensions["A"].width = 14; ws.column_dimensions["B"].width = 130

# ============================================================== S1
df = pd.read_csv("inputs/slide1_scorecard_jun2026.csv")
df["ctl"] = df.control.map({1: "Public", 2: "Private"})
df = df.sort_values("y", ascending=False).reset_index(drop=True)
ws = wb.create_sheet("S1_Scorecard")
title(ws, "Slide 1: net price vs median earnings 10 years after entry (College Scorecard, June 10, 2026 release)",
      "Earnings: pooled AY2009-10 / 2010-11 entry cohorts measured CY2020-21, 2022 dollars. Net price: AY2023-24. Rank = 1 + number of institutions with higher earnings.")
header(ws, 4, ["UNITID", "Institution", "City", "State", "Control", "Avg annual net price (NPT4)", "Median earnings, 10th yr after entry", "Rank by earnings", "Highlight", "Private net price", "Private earnings"],
       [10, 46, 20, 7, 9, 16, 20, 10, 18, 14, 14])
r0 = 5; n = len(df); r1 = r0 + n - 1
hl = {"Northeastern University": "Northeastern", "Vanderbilt University": "Vanderbilt", "Boston University": "Boston University", "Massachusetts Institute of Technology": "MIT"}
for i, row in df.iterrows():
    r = r0 + i
    vals = [int(row.UNITID), row["name"], row.city, row.st, row.ctl, int(row.x), int(row.y), f"=COUNTIF($G${r0}:$G${r1},\">\"&G{r})+1", hl.get(row["name"], ""),
            f'=IF(E{r}="Private",F{r},"")', f'=IF(E{r}="Private",G{r},"")']
    for j, v in enumerate(vals, 1):
        c = put(ws, r, j, v, bold=bool(hl.get(row["name"])), color=(RED if row["name"] == "Northeastern University" else "000000"))
    for j in (6, 7, 10, 11): ws.cell(r, j).number_format = '"$"#,##0'
sc = 13
put(ws, 4, sc, "Summary (formulas)", bold=True).border = HB; ws.cell(4, sc + 1).border = HB
S = [("Institutions in file after filters", f"=COUNTA(B{r0}:B{r1})", "0"), ("  Public", f'=COUNTIF(E{r0}:E{r1},"Public")', "0"), ("  Private", f'=COUNTIF(E{r0}:E{r1},"Private")', "0"),
     ("Northeastern rank", f'=INDEX(H{r0}:H{r1},MATCH("Northeastern University",B{r0}:B{r1},0))', "0"),
     ("Vanderbilt rank", f'=INDEX(H{r0}:H{r1},MATCH("Vanderbilt University",B{r0}:B{r1},0))', "0"),
     ("Boston University rank", f'=INDEX(H{r0}:H{r1},MATCH("Boston University",B{r0}:B{r1},0))', "0"),
     ("MIT rank", f'=INDEX(H{r0}:H{r1},MATCH("Massachusetts Institute of Technology",B{r0}:B{r1},0))', "0"),
     ("Private trendline slope", f"=SLOPE(K{r0}:K{r1},J{r0}:J{r1})", "0.000"), ("Private trendline intercept", f"=INTERCEPT(K{r0}:K{r1},J{r0}:J{r1})", '"$"#,##0'),
     ("Private trendline r", f"=CORREL(J{r0}:J{r1},K{r0}:K{r1})", "0.000"), ("Private trendline R-squared", f"=RSQ(K{r0}:K{r1},J{r0}:J{r1})", "0.000"),
     ("Northeastern earnings", f'=INDEX(G{r0}:G{r1},MATCH("Northeastern University",B{r0}:B{r1},0))', '"$"#,##0'),
     ("Northeastern net price", f'=INDEX(F{r0}:F{r1},MATCH("Northeastern University",B{r0}:B{r1},0))', '"$"#,##0'),
     ("Northeastern vs private trendline ($)", "=N16-(N13+N12*N17)", '"$"#,##0')]
for i, (lab, f, fm) in enumerate(S, 5):
    put(ws, i, sc, lab); put(ws, i, sc + 1, f, fm, bold=True)
put(ws, 21, sc, "Prior release (Oct 10, 2023; 1,557 institutions), for reference", bold=True).border = HB; ws.cell(21, sc + 1).border = HB
for i, (lab, v) in enumerate([("Northeastern rank / earnings / net price", "38th; $88,842; $34,255"), ("Vanderbilt rank", "53rd ($84,415)"), ("Boston University rank", "75th ($80,582)"),
                              ("MIT rank / net price", "2nd; $5,084 net price"), ("Private trendline", "slope 1.035, intercept $29,753, r 0.49")], 22):
    put(ws, i, sc, lab); put(ws, i, sc + 1, v)
ws.column_dimensions[L(sc)].width = 44; ws.column_dimensions[L(sc + 1)].width = 28
ws.freeze_panes = "A5"

# ============================================================== S2
ihe = json.load(open("inputs/slide2_ihe_verified.json"))["years"]
ws = wb.create_sheet("S2_Survey")
title(ws, "Slide 2: 'Faculty / Trustees / Sr. administrators are aware of and understand the financial challenges confronting my institution'",
      "% of business officers answering 4 or 5 on a five-point scale, all institutions. Verified against each report; original slide values shown for comparison.")
header(ws, 4, ["Survey year", "Faculty", "Trustees", "Sr. Administrators", "Trustees minus Faculty (pts)", "Sr. Admin minus Faculty (pts)", "Original slide: Faculty", "Original slide: Trustees", "Original slide: Sr. Admin",
               "Differs from original?", "Item type", "n respondents", "Source (report page / table)"], [11, 9, 9, 12, 14, 14, 12, 12, 12, 12, 22, 13, 110])
row = 5
for y in range(2015, 2027):
    v = ihe[str(y)]
    put(ws, row, 1, y)
    for j, k in ((2, "faculty"), (3, "trustees"), (4, "senior_administrators")):
        if v[k] is not None: put(ws, row, j, v[k] / 100, "0%")
    if v["faculty"] is not None:
        put(ws, row, 5, f"=(C{row}-B{row})*100", "0"); put(ws, row, 6, f"=(D{row}-B{row})*100", "0")
    o = v["original_slide"]
    for j, k in ((7, "faculty"), (8, "trustees"), (9, "senior_administrators")):
        if o[k] is not None: put(ws, row, j, o[k] / 100, "0%")
    if o["faculty"] is not None:
        put(ws, row, 10, f'=IF(AND(B{row}=G{row},C{row}=H{row},D{row}=I{row}),"same","DIFFERS")', bold=True)
    put(ws, row, 11, {"aware_of_and_understand": "aware of and understand", "faculty_item_differs": "faculty item worded differently", "trustees_only": "trustees-only item"}[v["item"]])
    put(ws, row, 12, int(str(v["n"]).split()[0].replace(",", "")) if str(v["n"]).split()[0].replace(",", "").isdigit() else str(v["n"]))
    put(ws, row, 13, f"{v['page']}  |  {v['source_url']}")
    row += 1
put(ws, row + 1, 1, "2014 was removed from the slide as requested (report wording then: 'realistic about'; Faculty 22%, Trustees 67%, Sr. Admin 75%).", color="6B6B70")
put(ws, row + 2, 1, "2025-2026: only a trustees-only statement was asked ('Trustees understand the financial challenges confronting my institution'); it is not the same series.", color="6B6B70")
put(ws, row + 4, 1, "Rows differing from the original slide", bold=True)
put(ws, row + 4, 5, f'=COUNTIF(J5:J{row-1},"DIFFERS")', "0", bold=True)

# ============================================================== S3_FY25
fy = json.load(open("inputs/fy25_slide3.json"))
rows = {r["short"]: r for r in fy["rows"]}
ORDER = ["Rice", "Vanderbilt", "Northwestern", "Princeton", "Harvard", "Yale", "Chicago", "Duke", "Emory", "Penn", "Stanford", "Northeastern", "Boston University", "MIT"]
ws = wb.create_sheet("S3_FY25")
title(ws, "Slide 3: FY25 salaries & wages per student (audited financial statements; see Evidence)",
      "Core operating expenses = total operating expenses - depreciation - amortization - interest. S&W basis: audited line, Form 990 / MD&A chart, or ESTIMATE (Penn, Stanford). Students = fall 2024 total enrollment.")
header(ws, 4, ["Institution", "Fiscal year end", "Salaries & wages ($)", "S&W basis", "Salaries + benefits, combined ($)", "Form 990 S&W ($)", "Form 990 lines 5-10 ($)", "Total operating expenses ($)",
               "Depreciation ($)", "Amortization ($)", "Interest ($)", "Core operating expenses ($)", "Students (fall 2024)", "S&W per student", "Core opex per student (x)", "S&W share of core opex (y)",
               "Check: x*y - S&W/student", "Health system consolidated", "Notes"], [18, 16, 17, 20, 18, 16, 16, 18, 15, 13, 14, 18, 12, 13, 14, 12, 12, 26, 90])
n990 = fy["n990"]
first = 5
notes = {"Yale": "Yale reports depreciation, amortization and interest as ONE operating line ($504.9M); shown in the depreciation column.",
         "Rice": "Depreciation and amortization are one line; interest and bond costs separate.",
         "Emory": "Depreciation and amortization are one line ($379.2M).",
         "Duke": "Depreciation and amortization are one line ($471.7M). Health system acquired the physician practice July 1, 2023 (FY23 not comparable; FY25 fine).",
         "Penn": "Statements show 'compensation and benefits' combined only. S&W ESTIMATED = combined x Form 990 S&W share (990 covers a narrower scope than the consolidated statements). D&A one line.",
         "Stanford": "Statements show salaries and benefits combined only. S&W ESTIMATED = combined x Form 990 S&W share. Interest is net and embedded in other operating expenses. Includes SLAC and the hospitals.",
         "Northeastern": "Audited statements show 'Salary and benefits' combined ($1,341.0M). S&W from Form 990 lines 5+6+7 (990 lines 5-10 are 96.8% of the audited combined line). Interest ($49.9M) is below the debt-note figure ($60.0M).",
         "Northwestern": "Audited statements show salaries, wages and benefits combined. Form 990 lines 5-10 tie to that line to the dollar, so 990 S&W is on the audited basis.",
         "Vanderbilt": "Audited statements show salaries, wages and benefits combined ($976.4M). S&W from the MD&A expense chart ($M precision). VUMC is not consolidated.",
         "Boston University": "Separate S&W line in the audited statements. Boston Medical Center is not consolidated. Right-of-use amortization (~$15M) not removed.",
         "MIT": "Includes Lincoln Laboratory (S&W not disclosed separately). 'Total expenses before depreciation and interest' = core. Net periodic benefit income of $170M is outside operating expenses.",
         "Chicago": "Includes UChicago Medicine; Argonne and Fermilab are not consolidated.",
         "Princeton": "Includes the Plasma Physics Laboratory ($246.9M expense). Students from the Report of the Treasurer (CDS host not reachable).",
         "Harvard": "PENDING: Harvard's finance site denies automated access; FY25 Financial Report PDF needed."}
r = first
pos = {}
for short in ORDER:
    pos[short] = r
    d = rows[short]
    put(ws, r, 1, short, bold=(short == "Northeastern"), color=(RED if short == "Northeastern" else "000000"))
    if short == "Harvard":
        put(ws, r, 2, "June 30, 2025"); put(ws, r, 4, "pending", color=RED, bold=True); put(ws, r, 13, 21189, "#,##0"); put(ws, r, 19, notes[short], wrap=True); r += 1; continue
    put(ws, r, 2, d["fy_end"])
    dep = d["depreciation"]
    if short == "Yale": dep = 504923000
    if short in ("Penn", "Stanford"):
        f990 = n990[short]
        put(ws, r, 5, d["combined_comp"], "#,##0"); put(ws, r, 6, f990["sw"], "#,##0"); put(ws, r, 7, f990["lines_5_10"], "#,##0")
        put(ws, r, 3, f"=E{r}*F{r}/G{r}", "#,##0"); put(ws, r, 4, "ESTIMATE (990 share x audited combined)", color=RED)
    elif short in ("Northeastern", "Northwestern"):
        f990 = n990[short]
        put(ws, r, 5, d["combined_comp"], "#,##0"); put(ws, r, 6, f990["sw"], "#,##0"); put(ws, r, 7, f990["lines_5_10"], "#,##0")
        put(ws, r, 3, f"=F{r}", "#,##0"); put(ws, r, 4, "Form 990 (ties to audited)" if short == "Northwestern" else "Form 990 (96.8% of audited combined)")
    elif short == "Vanderbilt":
        put(ws, r, 5, d["combined_comp"], "#,##0"); put(ws, r, 3, d["sw"], "#,##0"); put(ws, r, 4, "MD&A expense chart")
    else:
        put(ws, r, 3, d["sw"], "#,##0"); put(ws, r, 4, "audited line")
        if d.get("combined_comp"): put(ws, r, 5, d["combined_comp"], "#,##0")
        elif d.get("benefits") and d.get("sw"): put(ws, r, 5, f"=C{r}+{d['benefits']}", "#,##0")
    put(ws, r, 8, d["total_opex"], "#,##0"); put(ws, r, 9, dep, "#,##0")
    if d.get("amortization"): put(ws, r, 10, d["amortization"], "#,##0")
    if short != "Yale": put(ws, r, 11, d["interest"], "#,##0")
    put(ws, r, 12, f"=H{r}-I{r}-J{r}-K{r}", "#,##0"); put(ws, r, 13, d["students"], "#,##0")
    put(ws, r, 14, f"=C{r}/M{r}", '"$"#,##0'); put(ws, r, 15, f"=L{r}/M{r}", '"$"#,##0'); put(ws, r, 16, f"=C{r}/L{r}", "0.0%"); put(ws, r, 17, f"=O{r}*P{r}-N{r}", "0.00")
    put(ws, r, 18, d["health_system"] or "no"); put(ws, r, 19, notes.get(short, ""), wrap=True)
    r += 1
last = r - 1
put(ws, r + 1, 1, "Median (13 schools with data)", bold=True)
for col in (14, 15, 16):
    put(ws, r + 1, col, f"=MEDIAN({L(col)}{first}:{L(col)}{last})", ws.cell(first, col).number_format, bold=True)
put(ws, r + 2, 1, "Northeastern rank, S&W per student (1 = lowest)", bold=True)
put(ws, r + 2, 14, f"=RANK(N{pos['Northeastern']},N{first}:N{last},1)", "0", bold=True)
put(ws, r + 3, 1, "Northeastern S&W per student as % of peer median", bold=True)
put(ws, r + 3, 14, f"=N{pos['Northeastern']}/N{r+1}", "0%", bold=True)
ws.freeze_panes = "B5"

# ============================================================== S3_Sensitivity
ws2 = wb.create_sheet("S3_Sensitivity")
title(ws2, "Slide 3: sensitivity of the conclusions to the three judgement calls",
      "A: student count basis for Northeastern.  B: all schools, CDS fall 2024 vs IPEDS-style headcount.  C: estimated S&W for Penn and Stanford under alternative wage shares.")
nr = pos["Northeastern"]
put(ws2, 4, 1, "A. Northeastern S&W per student by student-count basis", bold=True)
header(ws2, 5, ["Basis", "Students", "S&W per student", "Core opex per student", "Note"], [46, 14, 16, 18, 90])
for i, (b, s, note) in enumerate([("Common Data Set 2024-25 (used on slide)", 39774, "B1 'total all students'"),
                                  ("IPEDS-style headcount (College Navigator fall 2024)", 32553, "As reported by the enrollment agent from College Navigator; IPEDS file for fall 2024 is not yet posted"),
                                  ("Northeastern Facts and Figures fall 2024", 48812, "Excludes non-degree students; adds co-op students as an extra column")], 6):
    put(ws2, i, 1, b); put(ws2, i, 2, s, "#,##0"); put(ws2, i, 3, f"=S3_FY25!C{nr}/B{i}", '"$"#,##0'); put(ws2, i, 4, f"=S3_FY25!L{nr}/B{i}", '"$"#,##0'); put(ws2, i, 5, note)
put(ws2, 10, 1, "B. S&W per student: CDS fall 2024 vs IPEDS fall 2023 headcount", bold=True)
header(ws2, 11, ["Institution", "CDS fall 2024", "IPEDS fall 2023", "S&W per student (CDS)", "S&W per student (IPEDS F23)", "Rank low-to-high (CDS)", "Rank low-to-high (IPEDS)", "IPEDS F23 vs CDS F24 (%)"])
ipeds = json.load(open("inputs/ipeds_fall_total.json"))["2023"]
ipk = {"Boston University": "Boston University", "MIT": "MIT"}
rr = 12
for short in [s for s in ORDER if s != "Harvard"]:
    put(ws2, rr, 1, short); put(ws2, rr, 2, f"=S3_FY25!M{pos[short]}", "#,##0"); put(ws2, rr, 3, ipeds[ipk.get(short, short)], "#,##0")
    put(ws2, rr, 4, f"=S3_FY25!C{pos[short]}/B{rr}", '"$"#,##0'); put(ws2, rr, 5, f"=S3_FY25!C{pos[short]}/C{rr}", '"$"#,##0')
    put(ws2, rr, 6, f"=RANK(D{rr},D$12:D$24,1)", "0"); put(ws2, rr, 7, f"=RANK(E{rr},E$12:E$24,1)", "0"); put(ws2, rr, 8, f"=(C{rr}/B{rr}-1)*100", "0.0")
    rr += 1
put(ws2, rr + 2, 1, "C. Penn and Stanford estimated S&W under alternative S&W shares of salaries + benefits", bold=True)
header(ws2, rr + 3, ["Institution", "Salaries + benefits ($)", "S&W share used (Form 990)", "S&W per student, share used", "Peer-median share (hospital schools)", "S&W per student, peer share", "Original slide assumption (72.8%)", "S&W per student, 72.8%"])
for k, short in enumerate(("Penn", "Stanford")):
    q = rr + 4 + k; p = pos[short]
    put(ws2, q, 1, short); put(ws2, q, 2, f"=S3_FY25!E{p}", "#,##0"); put(ws2, q, 3, f"=S3_FY25!F{p}/S3_FY25!G{p}", "0.0%")
    put(ws2, q, 4, f"=B{q}*C{q}/S3_FY25!M{p}", '"$"#,##0')
    put(ws2, q, 5, f"=MEDIAN(S3_FY25!C{pos['Chicago']}/S3_FY25!E{pos['Chicago']},S3_FY25!C{pos['Duke']}/S3_FY25!E{pos['Duke']},S3_FY25!C{pos['Emory']}/S3_FY25!E{pos['Emory']})", "0.0%")
    put(ws2, q, 6, f"=B{q}*E{q}/S3_FY25!M{p}", '"$"#,##0'); put(ws2, q, 7, 0.728, "0.0%"); put(ws2, q, 8, f"=B{q}*G{q}/S3_FY25!M{p}", '"$"#,##0')
put(ws2, rr + 7, 1, "Peer-median share = median of Chicago, Duke and Emory (the hospital-consolidated schools whose audited statements report S&W and benefits separately).", color="6B6B70")

# ============================================================== S3_FY23_Recalc
ws3 = wb.create_sheet("S3_FY23_Recalc")
title(ws3, "Slide 3: what the original FY23 slide actually used vs the stated definition",
      "Original values from the chart's embedded workbook. Recomputed FY23 from each school's audited statements using the SPEC definition. IPEDS columns: FY23 finance file F2223_F2 fields F2E131 (total expenses) and F2E132 (salaries and wages).")
header(ws3, 4, ["Institution", "Original: S&W", "Original: 'core opex'", "Audited FY23: S&W", "Audited FY23: total operating expenses", "Audited FY23: depreciation + amortization + interest", "Audited FY23: core (total - D&A - interest)",
                "Original 'core' vs audited TOTAL (%)", "Original 'core' vs audited CORE (%)", "Original S&W vs audited S&W (%)", "Audited FY23: salaries + benefits combined", "Original S&W / combined", "IPEDS FY23 F2E131 (total exp)", "IPEDS FY23 F2E132 (S&W)"],
       [16, 16, 16, 16, 18, 20, 18, 14, 14, 14, 18, 12, 18, 16])
wbo = openpyxl.load_workbook("inputs/orig_slide3_workbook.xlsx", data_only=True).active
norm = {"U Chicago": "Chicago", "U Penn": "Penn"}
orig = {}
for rr_ in range(94, 105):
    nm = norm.get(wbo.cell(rr_, 13).value, wbo.cell(rr_, 13).value); orig[nm] = (wbo.cell(rr_, 14).value, wbo.cell(rr_, 15).value)
ipeds_fin = {"Rice": (959377000, 421781000), "Vanderbilt": (1615854013, 699234852), "Northwestern": (3038060000, 1334540000), "Princeton": (2263259000, 886833000),
             "Harvard": (5911797000, 2421074000), "Yale": (4873675887, 2202260626), "Chicago": (5084463771, 1604106945), "Duke": (8431382000, 3609077000),
             "Emory": (8514754000, 4252849000), "Penn": (13857148000, 6045218000), "Stanford": (7659884000, 3467999000)}
FMAP = {"Rice": "Rice_University", "Vanderbilt": "Vanderbilt_University", "Northwestern": "Northwestern_University", "Princeton": "Princeton_University", "Harvard": "Harvard_University",
        "Yale": "Yale_University", "Chicago": "University_of_Chicago", "Duke": "Duke_University", "Emory": "Emory_University", "Penn": "University_of_Pennsylvania", "Stanford": "Stanford_University"}
rr_ = 5
for short in ["Rice", "Vanderbilt", "Northwestern", "Princeton", "Harvard", "Yale", "Chicago", "Duke", "Emory", "Penn", "Stanford"]:
    y = json.load(open(f"inputs/fin/{FMAP[short]}.json"))["years"].get("FY23") or {}
    put(ws3, rr_, 1, short); put(ws3, rr_, 2, orig[short][0], "#,##0"); put(ws3, rr_, 3, orig[short][1], "#,##0")
    if y.get("total_operating_expenses"):
        put(ws3, rr_, 4, y.get("salaries_and_wages"), "#,##0"); put(ws3, rr_, 5, y["total_operating_expenses"], "#,##0")
        put(ws3, rr_, 6, y["total_operating_expenses"] - y["core_opex"], "#,##0"); put(ws3, rr_, 7, f"=E{rr_}-F{rr_}", "#,##0")
        put(ws3, rr_, 8, f"=(C{rr_}/E{rr_}-1)*100", "0.0"); put(ws3, rr_, 9, f"=(C{rr_}/G{rr_}-1)*100", "0.0")
        if y.get("salaries_and_wages"): put(ws3, rr_, 10, f"=(B{rr_}/D{rr_}-1)*100", "0.0")
        if y.get("sw_combined_with_benefits"):
            put(ws3, rr_, 11, y["sw_combined_with_benefits"], "#,##0"); put(ws3, rr_, 12, f"=B{rr_}/K{rr_}", "0.0000")
    else:
        put(ws3, rr_, 4, "Harvard FY23 report not reached", color=RED)
    put(ws3, rr_, 13, ipeds_fin[short][0], "#,##0"); put(ws3, rr_, 14, ipeds_fin[short][1], "#,##0")
    rr_ += 1
put(ws3, rr_ + 1, 1, "Reading it: column H is ~0% for every school with data: the original 'core operating expenses' equal audited total operating expenses (depreciation and interest were never removed). "
                    "Column L is exactly 0.7280 for Penn, Stanford and Northwestern: their original S&W was 72.8% of combined salaries and benefits, an undisclosed assumption.", wrap=False, color="6B6B70")

# ============================================================== S3_Enrollment
ws4 = wb.create_sheet("S3_Enrollment")
title(ws4, "Slide 3: student counts (Common Data Set B1 'total all students') vs IPEDS vs the original slide",
      "IPEDS fall 2024 is not yet posted, so IPEDS fall 2022 and 2023 are shown for calibration.")
header(ws4, 4, ["Institution", "CDS fall 2024 (used)", "CDS fall 2023", "CDS fall 2022", "IPEDS fall 2023", "IPEDS fall 2022", "Original slide count (FY23)", "IPEDS F23 vs CDS F23 (%)", "Original vs IPEDS F22 (%)", "Source of fall 2024 count"], [18, 14, 13, 13, 13, 13, 16, 14, 14, 100])
ip = json.load(open("inputs/ipeds_fall_total.json"))
orig_st = {"Rice": 8285, "Vanderbilt": 13710, "Northwestern": 23000, "Princeton": 8778, "Harvard": 21400, "Yale": 14751, "Chicago": 18058, "Duke": 18009, "Emory": 16000, "Penn": 23374, "Stanford": 17529}
EMAP = dict(FMAP); EMAP.update({"Northeastern": "Northeastern_University", "Boston University": "Boston_University", "MIT": "Massachusetts_Institute_of_Technology"})
rr_ = 5
for short in ORDER:
    e = json.load(open(f"inputs/enroll/{EMAP[short]}.json"))
    g = lambda k: (e.get(k) or {}).get("total_all_students")
    key = ipk.get(short, short)
    put(ws4, rr_, 1, short)
    f24 = g("fall_2024")
    if f24 is None and short == "Princeton": f24 = 9050
    put(ws4, rr_, 2, f24, "#,##0"); put(ws4, rr_, 3, g("fall_2023"), "#,##0"); put(ws4, rr_, 4, g("fall_2022"), "#,##0")
    put(ws4, rr_, 5, ip["2023"][key], "#,##0"); put(ws4, rr_, 6, ip["2022"][key], "#,##0")
    if short in orig_st: put(ws4, rr_, 7, orig_st[short], "#,##0"); put(ws4, rr_, 9, f"=(G{rr_}/F{rr_}-1)*100", "0.0")
    if g("fall_2023"): put(ws4, rr_, 8, f"=(E{rr_}/C{rr_}-1)*100", "0.0")
    src = (e.get("fall_2024") or {}).get("source_url") or "Princeton Report of the Treasurer FY25: 5,726 undergraduates + 3,324 graduate students (term not named; CDS host not reachable)"
    put(ws4, rr_, 10, src)
    rr_ += 1
put(ws4, rr_ + 1, 1, "Reading it: Harvard (CDS excludes Extension School), Penn (CDS counts degree-seeking traditional programs only), Chicago (CDS ~12-14% below IPEDS) and Northeastern (CDS ~24% ABOVE IPEDS) do not match IPEDS; "
                    "the original slide mixed fall 2021 (Rice), fall 2022 (Vanderbilt), degree-seeking counts (Harvard, Penn) and round estimates (Emory 16,000, Northwestern 23,000).", color="6B6B70")

# ============================================================== Evidence
ws5 = wb.create_sheet("Evidence")
title(ws5, "Verbatim source rows and documents for each FY25 figure", "Amounts in the evidence text are as printed (usually $ thousands). Page numbers are PDF pages unless noted.")
header(ws5, 4, ["Institution", "Item", "FY25 value ($)", "Evidence (verbatim row, statement, page)", "Document"], [18, 24, 18, 120, 90])
rr_ = 5
for short in ORDER:
    d = json.load(open(f"inputs/fin/{EMAP[short]}.json"))
    y = d["years"]["FY25"]; ev = y.get("evidence") or {}
    doc = "; ".join(f"{x.get('label','')}: {x.get('url','')[:160]}" for x in d.get("documents", [])[:2])
    for item, key in (("Salaries and wages", "salaries_and_wages"), ("Total operating expenses", "total_operating_expenses"), ("Depreciation", "depreciation"), ("Interest", "interest_expense")):
        v = y.get(key)
        put(ws5, rr_, 1, short); put(ws5, rr_, 2, item); put(ws5, rr_, 3, v, "#,##0"); put(ws5, rr_, 4, ev.get(key, ""), wrap=True); put(ws5, rr_, 5, doc, wrap=True)
        rr_ += 1
put(ws5, rr_ + 1, 1, "Form 990 Part IX, Northeastern / Northwestern / Penn / Stanford: ProPublica Nonprofit Explorer 'Full Filing' renders of the IRS e-files; IRS object IDs are in inputs/fin/Northeastern_University_990.json and 990_northwestern_penn_stanford.json.", color="6B6B70")

# ============================================================== Checks
ws6 = wb.create_sheet("Checks")
title(ws6, "Checks run, disconnects found, and how each was handled")
header(ws6, 3, ["#", "Slide", "Check / observation", "Result", "Status"], [5, 7, 66, 120, 16])
C = [
    ("1", "Same filters reproduce the analysis set", "6,273 rows in the June 2026 file -> 1,527 institutions (584 public, 943 private) after CONTROL, CCBASIC 15-23, CCUGPROF 5-15, net price and 10-year earnings present. The original release had 1,557.", "Pass"),
    ("1", "Ranks (1 + institutions with higher earnings)", "Northeastern 33rd of 1,527 (29th of 943 private; ties with its 'Northeastern University Oakland' row at $92,538). Vanderbilt 38th, Boston University 77th, MIT 1st. Earlier release: 38th / 53rd / 75th / 2nd.", "Info"),
    ("1", "Does the earnings data run 'through 2024'?", "No. Net price is now AY2023-24 (IPEDS 2024-25 collection). 10-year earnings are the pooled AY2009-10 / 2010-11 entry cohorts measured CY2020-21 in 2022 dollars; the last 10-year refresh was June 13, 2024 and no later cohort exists. Scorecard was updated June 10, 2026 for IPEDS and FSA items.", "Info"),
    ("1", "Private trendline", "OLS on private institutions: slope 0.924, intercept $34,026, r 0.47, R-squared 0.22. Weak fit: 'better deal / worse deal' is directional.", "Pass / caveat"),
    ("1", "Title and axis said '10 years after graduation'", "The field is measured 10 years after entry (enrollment). Slide says 'after entry'.", "Fixed"),
    ("1", "Data quirks", "One institution reports a negative net price (Colegio Universitario de San Juan, -$778): counted in statistics, falls left of the axis. Three institutions exceed $56K net price (axis now to $60K). Cal Maritime is now Cal Poly Maritime Academy; University of the Sciences (merged into Saint Joseph's University in 2022) drops out. MIT net price is now $20,111 (the old file's $5,084 looked like an outlier).", "Handled"),
    ("2", "Item wording", "The 2015-2024 reports all ask 'aware of and understand the financial challenges confronting my institution'. 'Realistic about' was only the 2013-2014 wording. Slide statement corrected.", "Fixed"),
    ("2", "Original values that did not match the reports (all institutions)", "2015 faculty 33 -> 32; 2020 31/87/93 -> 34/84/90 (the original used a private-nonprofit sub-column); 2022 28/91/91 -> 53/90/91 (the 2022 chart on p.28 has misaligned rows; the detail tables give 53/90/91); 2024 44/91/95 -> 39/79/88 (the original used the private-nonprofit column). 2023 and the other rows match.", "Fixed"),
    ("2", "Faculty item in 2016 and 2017", "Different item: 'Faculty members understand the financial challenges my institution faces when they participate in college-wide budget discussions.' Values 27 and 32 are correct for that item; marked with an asterisk.", "Caveat"),
    ("2", "2025 and 2026", "The three-group item was not asked. Trustees-only statement: 74% (2025, n=169, +/-7%) and 79% (2026, n=213, +/-6%). Plotted as separate open markers. No faculty or senior-administrator values exist for these years.", "Info"),
    ("2", "Comparability of the series", "Fielded by Gallup in the earlier editions and by Hanover Research from 2021 (n=133 in 2021; 273-416 earlier; 169-238 for 2022-2026). No margin of error is stated for 2015-2022 (6-7% for 2023-2026). Year-to-year moves of a few points are within sampling error.", "Caveat"),
    ("2", "Who is asked", "Business officers rating other groups (Sr. Administrators includes their own peers); not faculty's own view.", "Fixed (labeled)"),
    ("3", "Definition of 'core operating expenses'", "The original values equal audited total operating expenses to the dollar for every school checked (Rice, Vanderbilt, Northwestern, Princeton, Yale, Chicago, Duke, Emory, Penn, Stanford), and equal the IPEDS FY23 'total expenses' field for Rice, Vanderbilt, Northwestern, Princeton, Harvard, Duke and Penn. Depreciation, amortization and interest were never removed although the axis says they were. FY25 now follows the axis; FY23 restated is 5-15% lower (S3_FY23_Recalc).", "Finding / fixed"),
    ("3", "Origin of the original S&W for Penn, Stanford, Northwestern", "Exactly 72.800% of each school's audited combined salaries and benefits: an undisclosed assumption. Schools that report both lines run 74.8%-81.4%, so 72.8% understates S&W by 3-10%. Northwestern is now actual (Form 990 ties to the audited line); Penn and Stanford are flagged estimates using their own Form 990 shares.", "Finding / fixed"),
    ("3", "S&W not separately reported in audited statements", "Northeastern, Northwestern, Penn, Stanford, Vanderbilt combine salaries and benefits. Northeastern and Northwestern use Form 990 S&W; Vanderbilt uses the MD&A expense chart; Penn and Stanford are estimated (grey markers). Sensitivity in S3_Sensitivity C: using the median share of the three hospital-consolidated schools with audited splits (about 81%) instead of each school's own 990 share moves Penn by about +6% and Stanford by about +1%.", "Handled / caveat"),
    ("3", "Student counts", "One instrument for all: Common Data Set 2024-25 B1 total all students (fall 2024). The original mixed fall 2021 (Rice), fall 2022 (Vanderbilt), degree-seeking counts (Harvard, Penn) and round estimates (Emory, Northwestern). CDS differs materially from IPEDS for Northeastern (+24%), Chicago (-14%), Penn (-17%) and Harvard (-30%).", "Handled / caveat"),
    ("3", "Northeastern student count is the key sensitivity", "CDS 39,774 -> S&W per student $26.3K; IPEDS-style 32,553 -> $32.1K; Facts and Figures 48,812 -> $21.4K. Northeastern is lowest in the peer set on all three (S3_Sensitivity A, B). Confirm the official count with University Decision Support.", "Open"),
    ("3", "Headcount vs FTE", "Northeastern and BU headcounts include large graduate, online and co-op populations (BU reports 29.6K FTE against 37.7K headcount), so S&W per headcount student understates S&W per FTE student for both.", "Caveat"),
    ("3", "Northeastern S&W scope", "Form 990 (university) lines 5-10 are 96.8% of the audited combined line; S&W may be understated by about 3% against the consolidated core expenses.", "Caveat"),
    ("3", "FY23 to FY24 comparability", "Duke's FY24 includes the July 1, 2023 physician-practice acquisition (S&W +29.5%); FY25 is unaffected. Rice's FY25 scholarship presentation changed (total and core not strictly comparable with FY24). Emory FY25 includes three months of Houston Healthcare. Northeastern FY25 includes two weeks of Marymount Manhattan College.", "Info"),
    ("3", "Entities inside the numbers", "Consolidated: hospitals at Chicago, Duke, Emory, Penn, Stanford; Lincoln Laboratory (MIT), Plasma Physics Laboratory (Princeton), SLAC (Stanford). Not consolidated: Northwestern Medicine, VUMC, Yale New Haven Hospital, Boston Medical Center, Argonne, Fermilab. Footnoted on the slide.", "Handled"),
    ("3", "Arithmetic", "For every school, core = total - depreciation - amortization - interest (formula), S&W per student = x * y (column Q = 0), and the natural-classification lines sum to total operating expenses in every year (as reported by the extraction). Key rows for Northeastern, BU and MIT re-checked against the PDFs.", "Pass"),
    ("3", "Harvard", "The FY25 Financial Report could not be reached (finance.harvard.edu denies automated access). Harvard is not on the FY25 chart; CDS fall 2024 enrollment (21,189) is recorded.", "Open"),
    ("3", "Original chart construction", "The original plotted only the eight iso-lines; logos were hand-placed pictures, so positions did not come from data, and Stanford's x-value exceeded the axis maximum. Rebuilt with real data points.", "Fixed"),
]
for i, (a, b, c, d_) in enumerate(C, 4):
    for j, v in enumerate([i - 3, a, b, c, d_], 1):
        cell = put(ws6, i, j, v, wrap=True)
    ws6.cell(i, 5).font = font(bold=True, color=(RED if d_.startswith(("Open", "Finding")) else "000000"))

# ============================================================== Data_needed
ws7 = wb.create_sheet("Data_needed")
title(ws7, "Still open")
header(ws7, 3, ["Slide", "Item", "Why", "Action"], [7, 70, 80, 70])
N = [("3", "Harvard FY25 Financial Report (and FY23 for calibration)", "finance.harvard.edu denies automated access; the PDFs are public.", "Download 'fy25 Harvard Financial Report' from finance.harvard.edu (Financial Reports) in a browser and upload; I will add Harvard to the chart."),
     ("3", "Northeastern official student count for FY25 analysis", "CDS 39,774 vs IPEDS-style 32,553 vs Facts and Figures 48,812 (S&W per student $26K / $32K / $21K).", "Confirm with University Decision Support which count leadership uses; I will relabel."),
     ("3", "Penn and Stanford salaries and wages", "Audited statements combine salaries and benefits; Form 990s cover a narrower scope than the consolidated statements.", "If Penn / Stanford finance offices can supply consolidated S&W, replace the grey estimates."),
     ("3", "Princeton Common Data Set 2024-25", "ir.princeton.edu is behind a bot challenge; the Treasurer's report count (9,050) is used.", "Optional: upload the CDS PDF."),
     ("3", "IPEDS fall 2024 enrollment and FY24 finance files", "Not yet posted on the IPEDS data center.", "Re-check when posted; IPEDS fall enrollment would give one government-standard definition.")]
for i, row_ in enumerate(N, 4):
    for j, v in enumerate(row_, 1): put(ws7, i, j, v, wrap=True)

wb.save(OUT)
print("saved", OUT)
