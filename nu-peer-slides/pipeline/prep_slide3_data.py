"""Slide 3 input: FY25 salaries & wages, core operating expenses and students for the peer set, with provenance.
Reads the per-institution extraction JSONs in inputs/fin and inputs/enroll and writes inputs/fy25_slide3.json.
S&W basis: 'audited' (separate line in audited statements), 'reported-other' (Form 990 / MD&A expense chart, tied to audited
statements), 'est' (Penn, Stanford: audited combined salaries+benefits / (1 + assumed fringe benefit rate))."""
import json
FIN, EN = "inputs/fin/", "inputs/enroll/"
ORDER = [("Rice", "Rice_University"), ("Vanderbilt", "Vanderbilt_University"), ("Northwestern", "Northwestern_University"),
         ("Princeton", "Princeton_University"), ("Harvard", "Harvard_University"), ("Yale", "Yale_University"),
         ("Chicago", "University_of_Chicago"), ("Duke", "Duke_University"), ("Emory", "Emory_University"),
         ("Penn", "University_of_Pennsylvania"), ("Stanford", "Stanford_University"),
         ("Northeastern", "Northeastern_University"), ("Boston University", "Boston_University"), ("MIT", "Massachusetts_Institute_of_Technology")]
HEALTH = {"Chicago": "UChicago Medicine", "Duke": "Duke University Health System", "Emory": "Emory Healthcare",
          "Penn": "Penn Medicine (UPHS)", "Stanford": "Stanford Health Care and Lucile Packard Children's Hospital"}
n990 = json.load(open(FIN + "Northeastern_University_990.json"))
o990 = json.load(open(FIN + "990_northwestern_penn_stanford.json"))
def find(d, *path):
    for p in path: d = d[p]
    return d
# Form 990 figures (from the agents' summary tables, whole dollars)
F990 = {
    "Northeastern": dict(sw=1045135178, lines_5_10=1297581752, share=1045135178 / 1297581752),
    "Northwestern": dict(sw=1556522638, lines_5_10=1997950859, share=1556522638 / 1997950859),
    "Penn": dict(sw=4515553000, lines_5_10=5886033000, share=4515553000 / 5886033000),
    "Stanford": dict(sw=4781181437, lines_5_10=5963697901, share=4781181437 / 5963697901),
}
FRINGE = 0.35   # assumed fringe benefit rate (benefits / S&W) for schools whose audited statements combine salaries and benefits and no 990 ties (Penn, Stanford), per Northeastern's direction
CDS_OVERRIDE = {"Princeton": (9050, "Report of the Treasurer FY25 / financial statements: 5,726 undergraduates + 3,324 graduate students (term not named; CDS host not reachable)")}
rows, missing = [], []
for short, f in ORDER:
    fin = json.load(open(FIN + f + ".json"))
    y = fin["years"]["FY25"]
    en = json.load(open(EN + f + ".json"))
    st = (en.get("fall_2024") or {}).get("total_all_students")
    st_src = "Common Data Set 2024-25, B1 total all students (fall 2024)"
    if st is None and short in CDS_OVERRIDE: st, st_src = CDS_OVERRIDE[short]
    if en.get("fall_2024_used_on_slide"):   # Harvard: CDS total plus Extension School degree students (its expenses include the Division of Continuing Education)
        st, st_src = en["fall_2024_used_on_slide"]["total_all_students"], "Common Data Set 2024-25 B1 total all students (21,189) plus Harvard Extension School degree students, fall 2024 (3,630; Harvard OIRA Fact Book 2025-26)"
    core, tot = y.get("core_opex"), y.get("total_operating_expenses")
    sw, basis, sw_src = y.get("salaries_and_wages"), "audited", "audited statements (separate salaries and wages line)"
    comb = y.get("sw_combined_with_benefits")
    if short == "Vanderbilt":
        basis, sw_src = "reported-other", "Management's discussion and analysis expense chart (faculty + staff/student wages, $M precision); audited statements show salaries, wages and benefits combined"
    elif short in ("Northeastern", "Northwestern"):
        sw, basis = F990[short]["sw"], "reported-other"
        sw_src = "IRS Form 990 Part IX lines 5+6+7 (audited statements show salary and benefits combined)" + ("; 990 lines 5-10 tie to the audited combined line to the dollar" if short == "Northwestern" else "; 990 lines 5-10 are 96.8% of the audited combined line")
    elif short in ("Penn", "Stanford"):
        sw = round(comb / (1 + FRINGE)); basis = "est"
        sw_src = f"ESTIMATE: audited combined salaries and benefits ${comb:,.0f} / (1 + {FRINGE:.0%} assumed fringe benefit rate) = {1/(1+FRINGE):.2%} S&W share (Form 990 share for reference: {F990[short]['share']:.2%}; 990 covers a narrower scope than the consolidated statements)"
    rows.append(dict(short=short, name=fin.get("institution"), sw=sw, sw_basis=basis, sw_source=sw_src, combined_comp=comb, benefits=y.get("employee_benefits"),
                     total_opex=tot, depreciation=y.get("depreciation"), amortization=y.get("amortization"), interest=y.get("interest_expense"),
                     core_opex=core, students=st, students_source=st_src, health_system=HEALTH.get(short), fy_end=fin.get("fiscal_year_end_fy25")))
    if sw is None or core is None or st is None: missing.append(short)
json.dump(dict(rows=rows, missing=missing, n990=F990, fringe=FRINGE), open("inputs/fy25_slide3.json", "w"), indent=1)
print("missing:", missing)
for r in rows:
    if r["sw"] and r["core_opex"] and r["students"]:
        print(f"{r['short']:18s} S&W {r['sw']/1e6:8.1f}M {r['sw_basis']:14s} core {r['core_opex']/1e6:8.1f}M students {r['students']:6,d}  S&W/st ${r['sw']/r['students']/1e3:6.1f}K  opex/st ${r['core_opex']/r['students']/1e3:6.1f}K  S&W% {r['sw']/r['core_opex']:.1%}")
    else: print(f"{r['short']:18s} INCOMPLETE")
