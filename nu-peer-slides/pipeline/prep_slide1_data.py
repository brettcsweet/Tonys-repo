"""Slide 1 input: College Scorecard institution-level file (Most-Recent-Cohorts-Institution.csv, June 10, 2026 release).
Applies the filters from the original slide: CONTROL = public / private not-for-profit; CCBASIC 15-23; CCUGPROF 5-15;
net price (NPT4_PUB for public, NPT4_PRIV for private) present; MD_EARN_WNE_P10 present.
usage: python3 prep_slide1_data.py <Most-Recent-Cohorts-Institution.csv> inputs/slide1_scorecard_jun2026.csv"""
import sys
import numpy as np, pandas as pd

src, out = sys.argv[1], sys.argv[2]
cols = ["UNITID", "INSTNM", "CITY", "STABBR", "CONTROL", "CCBASIC", "CCUGPROF", "NPT4_PUB", "NPT4_PRIV", "MD_EARN_WNE_P10"]
raw = pd.read_csv(src, usecols=cols, low_memory=False, na_values=["NULL", "PrivacySuppressed"])
n_file = len(raw)
d = raw[raw.CONTROL.isin([1, 2])]
d = d[d.CCBASIC.between(15, 23)]
d = d[d.CCUGPROF.between(5, 15)]
d = d.assign(x=np.where(d.CONTROL == 1, d.NPT4_PUB, d.NPT4_PRIV))
d = d[d.x.notna() & d.MD_EARN_WNE_P10.notna()].copy()
d = d.rename(columns={"INSTNM": "name", "CITY": "city", "STABBR": "st", "CONTROL": "control", "MD_EARN_WNE_P10": "y"})
dup = d.name.duplicated(keep=False)
d["name"] = np.where(dup, d.name + " (" + d.city + ", " + d.st + ")", d.name)   # unique keys for labels and the chart sheet
d = d[["UNITID", "name", "city", "st", "control", "x", "y"]].sort_values(["y", "x"]).reset_index(drop=True)
d.to_csv(out, index=False)
print(f"file rows {n_file:,}; kept {len(d):,} (public {(d.control==1).sum()}, private {(d.control==2).sum()}); negative net price rows: {(d.x<0).sum()}")
