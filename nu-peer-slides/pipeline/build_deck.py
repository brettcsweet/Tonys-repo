"""Assemble the 3-slide Northeastern-branded deck (interim build on the data in the original file)."""
import json, sys
import numpy as np
import pandas as pd
import openpyxl
from nu_helpers import *
from slide1 import build_slide1
from slide2 import build_slide2
from slide3 import build_slide3

OUT = sys.argv[1] if len(sys.argv) > 1 else "deck.pptx"
DRAFT = True

# ---------------------------------------------------------------- slide 1 data (College Scorecard, June 10, 2026 release)
df = pd.read_csv("inputs/slide1_scorecard_jun2026.csv")
lm = json.load(open("inputs/s1_label_map_jun2026.json"))
def crank(frame, name):
    """competition rank: 1 + number of institutions with strictly higher earnings (ties share a rank)"""
    y = frame[frame.name == name].iloc[0].y
    return int((frame.y > y).sum()) + 1
foc = "Northeastern University"
fr = df[df.name == foc].iloc[0]
n_all = len(df); n_pub = int((df.control == 1).sum()); n_pri = int((df.control == 2).sum())
pri = df[df.control == 2]
foc_rank = crank(df, foc); pri_rank = crank(pri, foc)
vu_rank = crank(df, "Vanderbilt University"); bu_rank = crank(df, "Boston University"); mit_rank = crank(df, "Massachusetts Institute of Technology")
fit = np.polyfit(pri.x, pri.y, 1); r_pri = float(np.corrcoef(pri.x, pri.y)[0, 1])
n_neg = int((df.x < 0).sum())
n_tied = int((df.y == fr.y).sum())

s1_notes = [
    "(1) Median earnings of federally aided (Title IV) students who entered in 2009\u201310 or 2010\u201311, are working and not enrolled, measured in 2020 and 2021 (10th year after entry); 2022 dollars.",
    "(2) Average net price, academic year 2023\u201324, for undergraduate Title IV-receiving students: full cost of attendance (tuition and fees, books and supplies, living expenses) minus federal, state and institutional aid.",
    "(3) Landmark College is located in Putney, Vermont and is dedicated to students with learning disabilities (ADHD, dyslexia and autism).",
    f"Note: Of 6,273 institutions in the Scorecard file, the analysis includes {n_all:,} ({n_pub} public, {n_pri} private) with CONTROL = public or private not-for-profit; CCBASIC = 15\u201323; CCUGPROF = 5\u201315; net price and 10-year earnings reported."
    + (f" {n_neg} institution with a negative reported net price is counted but falls left of the axis." if n_neg == 1 else ""),
]
s1_source = ("Source: U.S. Department of Education, College Scorecard institution-level data (collegescorecard.ed.gov/data), release of June 10, 2026; Northeastern analysis.")
s1_speaker = f"""WHAT CHANGED FROM THE ORIGINAL
- Data refreshed to the College Scorecard release of June 10, 2026 (Most-Recent-Cohorts-Institution file), same filters as the original slide. Net price is now academic year 2023-24 (IPEDS 2024-25 collection). 10-year earnings are the newest Scorecard publishes: entering cohorts 2009-10 and 2010-11 pooled, measured in calendar 2020 and 2021, in 2022 dollars. Scorecard has not released a later 10-year earnings cohort, so earnings do not run through 2024.
- Rebuilt as a native chart (right-click > Edit Data; institution names are in column C of the embedded sheet). Vanderbilt logo removed; Vanderbilt is a navy label like the other private institutions. Markers: private institutions are bright royal blue (#1F4FE0, requested; not an NU brand color) and public institutions stay grey, one marker size smaller with a hairline (0.25 pt) black border, so the two groups separate where they overlap; private labels stay navy. Northeastern is the red marker and label; Boston University is labeled as a local comparison.
- Axis, title and footnote say 'after entry': the Scorecard field MD_EARN_WNE_P10 is measured 10 years after enrollment, not graduation.
- Removed Vanderbilt-internal speaker notes.

RESULTS AND CHECKS ({n_all:,} institutions: {n_pub} public, {n_pri} private)
- Northeastern ranks {foc_rank} of {n_all:,} ({pri_rank} of {n_pri} private; rank = 1 + institutions with strictly higher earnings, so ties share a rank{", and Northeastern University Oakland reports the identical earnings" if n_tied > 1 else ""}) at ${fr.y:,.0f} median earnings and ${fr.x:,.0f} net price (previous release: 38th of 1,557 at $88,842 and $34,255). Vanderbilt ranks {vu_rank} (previously 53rd); Boston University {bu_rank}; MIT {mit_rank}.
- Trendline is an OLS fit on private institutions: slope {fit[0]:.3f}, intercept ${fit[1]:,.0f}, r = {r_pri:.2f} (R-squared {r_pri**2:.2f}). Weak fit: 'better deal / worse deal' is directional.
- Earnings are in 2022 dollars for every school, so ranks are comparable within this release. The previous release used an older earnings cohort, so the change in rank is not a like-for-like trend.
- Cal Maritime is now Cal Poly Maritime Academy; University of the Sciences (merged into Saint Joseph's University in 2022) drops out.
"""
# ---------------------------------------------------------------- slide 2 data (Inside Higher Ed CBO survey, verified against the reports)
ihe = json.load(open("inputs/slide2_ihe_verified.json"))["years"]
years = list(range(2015, 2027))            # 2014 removed per request; 2025-2026 carry the trustees-only item
s2 = {"F": {}, "T": {}, "S": {}, "T2": {}}
for y in years:
    v = ihe[str(y)]
    if v["item"] == "trustees_only":
        s2["T2"][y] = v["trustees"]
    else:
        s2["F"][y] = v["faculty"]; s2["T"][y] = v["trustees"]; s2["S"][y] = v["senior_administrators"]
n_fix = sum(1 for y in years if any(ihe[str(y)]["original_slide"][k] not in (None, ihe[str(y)][k]) for k in ("faculty", "trustees", "senior_administrators")))
s2_speaker = """WHAT CHANGED FROM THE ORIGINAL
- 2014 row removed as requested. 2025 and 2026 added where the survey asked something comparable; rebuilt as a native chart (values are in the embedded sheet).
- The item wording is 'aware of and understand the financial challenges confronting my institution', not 'realistic and aware': 'realistic' was only the 2013-2014 wording. The 2015-2024 reports all use 'aware of and understand'.
- 2025 and 2026: the three-group item was NOT asked. The reports ask a trustees-only statement ('Trustees understand the financial challenges confronting my institution'): 74% in 2025 (n=169, +/-7%) and 79% in 2026 (n=213, +/-6%). They are plotted as separate open markers with no connector because the wording and the groups differ. There is no 2025 or 2026 value for faculty or senior administrators.
- Every value was re-read from the report PDFs (all-institution results). Four rows on the original slide did not match: 2015 faculty 33 -> 32; 2020 31/87/93 -> 34/84/90 (the original used a private-nonprofit sub-column); 2022 28/91/91 -> 53/90/91 (the 2022 report's p.28 chart has misaligned rows; the detail tables give 53/90/91); 2024 44/91/95 -> 39/79/88 (the original used the private-nonprofit column).
- 2016 and 2017 faculty (27, 32) answer a different item: 'Faculty members understand the financial challenges my institution faces when they participate in college-wide budget discussions.' Marked with an asterisk.
- 2021 was fielded by Hanover Research (n=133) rather than Gallup; sample sizes run 133 to 416, so year-to-year moves of a few points are within the margin of error where one is stated (about 6-7%).

WHAT THE SERIES SHOWS
- Trustees minus faculty: between 34 and 50 points in every year 2015-2024 (47 in 2015, 40 in 2024). Sr. Administrators minus faculty: between 36 and 59 points (56 in 2015, 49 in 2024). Faculty peaked at 53% in 2022 and has fallen since (45, 39); trustees fell from 90% (2022) to 79% (2024); the trustees-only item read 74% (2025) and 79% (2026).
- The disconnect persists, but the corrected 2022-2024 rows show trustees and administrators well below the 91-95% the original slide showed for 2022-2024.
- Ratings are business officers' perceptions of each group, not self-reports; Sr. Administrators includes their own peers.
"""

# ---------------------------------------------------------------- slide 3 data (FY25 audited financial statements; see prep_slide3_data.py)
s3d = json.load(open("inputs/fy25_slide3.json"))
DISP = {"Northeastern": "Northeastern", "Boston University": "Boston University"}
rows3 = []
for r in s3d["rows"]:
    if r["short"] in s3d["missing"]: continue
    rows3.append(dict(name=DISP.get(r["short"], r["short"]), sw=r["sw"], opex=r["core_opex"], students=r["students"],
                      basis="est" if r["sw_basis"] == "est" else "audited", src=r["sw_basis"]))
HEALTH = ("Chicago", "Duke", "Emory", "Penn", "Stanford")
LAB = ("MIT", "Princeton", "Stanford")
OTHER_SRC = ("Northeastern", "Northwestern", "Vanderbilt")
EST = ("Penn", "Stanford")
def marks(nm):
    m = []
    if nm in HEALTH: m.append("(1)")
    if nm in LAB: m.append("(2)")
    if nm in OTHER_SRC: m.append("(3)")
    if nm in EST: m.append("(4)")
    return " ".join(m)
foot_marks = {}
for r in rows3:
    mk = [x for x in ("(2)", "(3)", "(4)") if x in marks(r["name"])]
    if mk: foot_marks[r["name"]] = " " + " ".join(mk)
missing_names = [r["short"] for r in s3d["rows"] if r["short"] in s3d["missing"]]
for r in rows3:
    r["swps"] = r["sw"] / r["students"]; r["share"] = r["sw"] / r["opex"]; r["opex_ps"] = r["opex"] / r["students"]
neu3 = next(r for r in rows3 if r["name"] == "Northeastern")
peers3 = [r for r in rows3 if r["name"] != "Northeastern"]
share_lo, share_hi = min(r["share"] for r in rows3), max(r["share"] for r in rows3)
lowest = min(rows3, key=lambda r: r["swps"])
import statistics
peer_med_share = statistics.median(r["share"] for r in peers3)
s3_title = (f"Northeastern\u2019s S&W per student is ${neu3['swps']/1000:,.0f}K, "
            f"{'the lowest' if lowest['name'] == 'Northeastern' else 'among the lowest'} in the peer set, at a {neu3['share']:.0%} share of expenses vs a {peer_med_share:.0%} peer median")
s3_notes = ["(1) Blue markers: consolidates a health care system (academic medical center): Chicago, Duke, Emory, Penn, Stanford.  (2) Consolidates a federal laboratory: MIT (Lincoln Laboratory), Princeton (Plasma Physics Laboratory), Stanford (SLAC).",
            "(3) Audited statements report salaries and benefits combined: Northeastern S&W = audited line \u00f7 1.33 (33% fringe benefit rate); Northwestern S&W from its Form 990; Vanderbilt from the MD&A expense chart.  (4) Light blue: Penn and Stanford S&W estimated from combined salaries and benefits, assuming a 35% fringe benefit rate (S&W = combined \u00f7 1.35).",
            "Note: FY25 audited financial statements (fiscal years end June 30; Emory, Northwestern, Stanford August 31). Core operating expenses = total operating expenses less depreciation, amortization and interest. Students = fall 2024 total enrollment"
            " per Common Data Set 2024\u201325 (Princeton: Report of the Treasurer); Harvard\u2019s count includes Extension School degree students." + (f" {', '.join(missing_names)}: FY25 report not yet available." if missing_names else "")]
s3_source = "Source: University FY25 audited financial statements, IRS Form 990 filings, Common Data Sets; Northeastern analysis."
sens = {k: neu3["sw"] / v for k, v in (("CDS 2024-25 (used)", neu3["students"]), ("IPEDS-style 32,553", 32553), ("Facts and Figures 48,812", 48812))}
s3_speaker = f"""WHAT CHANGED FROM THE ORIGINAL
- Updated to FY25 audited financial statements and added Northeastern, Boston University and MIT. Universities' logos removed: every institution is a data point with a label. {', '.join(missing_names) + ' is not shown: its FY25 financial report could not be reached.' if missing_names else ''}
- 'Core operating expenses' now follow the axis definition: total operating expenses less depreciation, amortization and interest. The original FY23 figures did NOT: they equal each school's total operating expenses to the dollar (for Rice, Vanderbilt, Northwestern, Princeton, Harvard, Duke and Penn they are the IPEDS FY23 'total expenses' field). Restated on the stated definition, FY23 core expenses are 5-15% lower, so FY25 positions are not comparable with the earlier chart along the x axis. S&W per student (the iso-lines) does not depend on this definition.
- S&W: the original S&W for Penn, Stanford and Northwestern equals exactly 72.80% of each school's combined salaries-and-benefits line, an undisclosed assumption. Peers that report both lines run 74.8% to 81.4%. Northwestern is now actual (its Form 990 ties to the audited combined line to the dollar: S&W = 77.9%). Penn and Stanford are estimates, shown in light blue: per Northeastern's direction S&W = audited combined salaries and benefits / 1.35 (a 35% fringe benefit rate, i.e. a 74.1% S&W share). For reference the schools that report both lines have fringe rates of 23%-34% (74.8%-81.4% S&W share), so 35% is above every observed peer and these two estimates lean low; their own Form 990 shares (76.7%, 80.2%) would give S&W per student about 4% (Penn) and 8% (Stanford) higher.
- Markers: universities that consolidate a health system (footnote 1) are blue: royal blue for Chicago, Duke and Emory, lighter blue for Penn and Stanford (S&W estimated, footnote 4). Everyone else is black; Northeastern is red. Markers are one size larger than the first draft.
- Y axis now runs 30% to 60% (was 0% to 80%) with no horizontal gridlines: all 14 S&W shares fall between 43% and 54%, so the tighter range spreads the points and the chart is less busy. Dashed iso-lines are drawn to the plot edges and labelled in $K where they enter along the top edge.
- Student counts: the original mixed sources (Rice = fall 2021, Vanderbilt = fall 2022, Emory 16,000 and Northwestern 23,000 were round estimates; Harvard and Penn used degree-seeking counts while others used IPEDS). All FY25 counts are now fall 2024 total enrollment from each school's Common Data Set.

NORTHEASTERN
- S&W ${neu3['sw']/1e6:,.0f}M on core operating expenses ${neu3['opex']/1e6:,.0f}M = {neu3['share']:.1%}; {neu3['students']:,} students => ${neu3['swps']/1000:,.1f}K S&W per student and ${neu3['opex_ps']/1000:,.1f}K core expense per student (x axis $55.0K is unchanged: total operating expenses $2,388.2M less depreciation $151.3M and interest $49.9M = $2,187.1M).
- CHECK OF THE $1.3B: the audited statements show only 'Salary and benefits' of $1,341.0M, which is salaries AND benefits. At Northeastern's 33% fringe benefit rate S&W is $1,008M and benefits are $333M, so 39,774 students x $25.4K S&W per student = $1,008M, not $1.3B. $1,341.0M / 39,774 = $33.7K is salary-plus-benefits per student, not S&W per student, and is not comparable with the peers' S&W (the nine peers that report both lines exclude benefits). On the like-for-like salary-plus-benefits basis Northeastern is still lowest ($33.7K vs Boston University $43.1K).
- How S&W is derived: neither the audited statements nor any footnote split the line, so S&W = audited $1,341.0M / (1 + 33% fringe rate, per Northeastern) = $1,008.3M. For reference the Form 990 (university only, 96.8% of the audited line) shows S&W $1,045.1M and benefits $252.4M (24.2% of S&W); using the 990 as filed would give $26.3K and 47.8%, and scaling its S&W share to the audited line $27.2K and 49.4%.
- Student count: per Northeastern's direction the Common Data Set fall 2024 headcount (39,774) is used. It is about 22% above the IPEDS-style headcount (about 32.5K) and Facts and Figures shows 48,812; S&W per student would be $25.4K, $31.0K or $20.7K respectively. Northeastern is lowest in the peer set on all three.
- Northeastern and BU headcounts include large graduate, online and co-op populations; per-headcount measures understate S&W per FTE student.

OTHER CHECKS AND CAVEATS
- Rice FY25 S&W +10.7% and scholarship presentation change; Duke FY24 includes the physician-practice acquisition (FY23-FY24 not comparable; FY25 is fine); Emory FY25 includes three months of the Houston Healthcare acquisition; Northeastern FY25 includes two weeks of Marymount Manhattan College; Yale reports depreciation, amortization and interest as one combined line; Vanderbilt S&W is from a chart at $M precision.
- Chicago's CDS headcount (16,221) is 12% below IPEDS-style counts.
- Harvard (FY25 and FY23 Financial Reports, supplied by Northeastern; audited, unqualified opinions): S&W $2,759M and employee benefits $756M are separate lines (benefits = 27.4% of S&W), total operating expenses $6,794M less depreciation $459M and interest $263M = core $6,073M; S&W share 45.4%. The nine natural-classification lines sum to total operating expenses in FY25, FY24 and FY23. Students: 24,819 = Common Data Set fall 2024 total 21,189 (degree schools only) plus 3,630 Extension School degree students (621 undergraduate + 3,009 graduate, Harvard OIRA Fact Book 2025-26, as of Oct 15, 2024), added because Harvard's expenses include the Division of Continuing Education. $111K S&W per student and $245K core expense per student. Without the Extension count it would be $130K; the Fact Book's distinct-student total (24,519) gives $113K; IPEDS (30,386 in fall 2023, adds non-degree Extension course takers) gives $91K. FY23 tie-out: the original slide's Harvard S&W ($2,421,076K) equals the audited FY23 line to the dollar and its 'core' ($5,911,797K) equals audited FY23 total operating expenses; on the stated definition FY23 core is $5,278M. S&W grew 13.9% FY23 to FY25. No hospital is consolidated. Harvard sits just below Princeton ($128K) on S&W per student and 5 points lower on S&W share (45% vs 51%).
"""

def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1:'st',2:'nd',3:'rd'}.get(n % 10,'th')}"

s1_sub = (f"Northeastern ranks {ordinal(foc_rank)} (of {n_all:,}) in median earnings 10 years after entry: "
          f"${fr.y/1000:,.0f}K at a ${fr.x/1000:,.0f}K average net price")

prs = open_base("base.pptx")
tag1 = None
tag2 = None
tag3 = ("DRAFT \u00b7 " + ", ".join(missing_names) + " FY25 pending") if (DRAFT and missing_names) else None

build_slide1(prs, df, lm, focus=foc, title="Wide variation in ‘return’ on college investment", subtitle=s1_sub,
             notes_paras=s1_notes, source=s1_source, draft_tag=tag1, notes_text=s1_speaker, xmax=60000, ymax=150000)
build_slide2(prs, s2, years, title="Is there a dangerous disconnect in perception at our institutions?",
             subtitle="From Inside Higher Ed\u2019s annual survey of college and university business officers",
             notes_paras=["* 2016 and 2017 faculty item asked whether faculty understand the challenges when they take part in budget discussions. Open markers, 2025\u20132026: a trustees-only statement (\u201cTrustees understand\u2026\u201d); faculty and senior administrators were not asked.",
                          "Note: All institutions. Wording 2015\u20132024: \u201caware of and understand\u201d (the 2014 survey asked about \u201crealistic\u201d). Ratings are business officers\u2019 perceptions of each group, not self-reports by faculty or trustees."],
             source="Source: Inside Higher Ed, Survey of College and University (Chief) Business Officers, 2015\u20132026 (n = 133 to 416 per year).",
             draft_tag=tag2, notes_text=s2_speaker, frame_bottom=6.42, extra_label="Trustees only (2025\u201326 item)",
             star_years={"F": (2016, 2017)})
build_slide3(prs, rows3, "FY25", title=s3_title,
             subtitle="Core operating expense per student and S&W share of that expense; dashed lines, labelled at top, mark constant S&W per student",
             notes_paras=s3_notes, source=s3_source, draft_tag=tag3, notes_text=s3_speaker, focus="Northeastern", health_system=HEALTH,
             frame_bottom=6.05, foot_marks=foot_marks,
             hints={"Boston University": dict(dirs=[(0, -1)], min_r=0.16, max_r=0.5),      # above its marker
                    "Rice": dict(at=(0.87, 0.0)),                                          # right of its marker
                    "Vanderbilt": dict(at=(0.0, 1.07)),                                    # straight below, clear of the Northeastern label
                    "Northwestern": dict(at=(1.31, 0.93)),                                 # lower right
                    "Harvard": dict(at=(0.87, 0.38))})                                     # lower right of its marker

prs.core_properties.title = "Peer comparison: return on investment, perceptions and salaries per student"
import datetime
cp = prs.core_properties
cp.author = "Northeastern University"; cp.last_modified_by = "Northeastern University"
cp.created = cp.modified = datetime.datetime(2026, 9, 29, 12, 0, 0); cp.revision = 1; cp.comments = ""
prs.save(OUT)
print("saved", OUT, "focus rank", foc_rank, "vu rank", vu_rank)
