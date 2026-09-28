# FY26 endowment returns tracker

Tracks officially reported FY26 endowment returns (1-year, 5-year annualized, 10-year annualized)
for the U.S. News & World Report 2027 Best National Universities top 50, public and private
(51 institutions including ties at No. 49). A weekly cloud routine (Friday mornings) updates the
data, rebuilds the deck and workbook, commits them here, and emails Brett a summary.

| Path | What it is |
|---|---|
| `data/top50.json` | The dataset. Source of truth. |
| `scripts/build.py` | Builds both deliverables from the JSON. |
| `assets/backup_render/slide-1.jpg`, `slide-2.jpg` | Static FY25 Skorina backup slides (slides 4-5). Do not edit. |
| `output/FY26_Endowment_Returns_Top50.pptx` | 5 slides: 1-yr, 5-yr, 10-yr charts, two backup slides. |
| `output/FY26_Endowment_Data_Top50.xlsx` | Data sheet and methodology sheet. |

Build: `pip install -r endowment/requirements.txt` then `python3 endowment/scripts/build.py`.

## Data schema (`institutions[]`)

| Field | Meaning |
|---|---|
| `usNewsRank`, `name`, `short`, `control` | 2027 rank (ties share a number), full name, chart label, public/private |
| `fyEnd` | Fiscal year end, `MM-DD`. Most `06-30`; Stanford, Emory, Northwestern, NYU, UT Austin `08-31`; Caltech `09-30`; Villanova, Boston College `05-31` |
| `fy26Return` | FY26 1-year return %, as stated by the institution or credible press quoting it |
| `fy26Return5yr`, `fy26Return10yr` | FY26 5- and 10-year annualized returns %, only as separately reported |
| `spacexPts` | Points of the 1-year return a source explicitly attributes to a SpaceX stake; else null |
| `fy25M`, `fy26M` | Endowment market value at FY end, $ millions |
| `returnBasis` | `reported` or `management estimate` |
| `notes` | Sources and caveats for the row |
| `lastChecked` | ISO date the row was last researched |

## Sourcing rules

- Never calculate or derive a return from dollar values, or one metric from another. Record only a
  figure the institution or a credible source explicitly states for that specific metric.
- 5- and 10-year figures usually come later than 1-year ones. It is normal for them to stay null.
- Set `spacexPts` only when a source attributes a specific share of the gain to SpaceX (e.g. "about half").
- Update `fy25M`/`fy26M` only from a primary source (audited statements, Form 990, official
  investment/foundation report) or a clearly labeled press figure; say which in `notes`.
- Do not overwrite a non-null value unless a primary source corrects it; note the correction.
- Search order: the institution's investment office, treasurer, trustees and news office; then
  Bloomberg, Pensions & Investments, WSJ, NYT, Chronicle of Higher Education, Inside Higher Ed,
  Higher Ed Dive, Institutional Investor, ai-cio.com, Charles Skorina; then campus newspapers.

## Weekly routine (Friday mornings)

1. For each institution with a null metric, search for a newly released FY26 figure (respecting `fyEnd`).
2. Update `data/top50.json`: new values, `notes` with source, `lastChecked` = today for every row
   checked, top-level `asOf` = today.
3. `python3 endowment/scripts/build.py`
4. Render check: convert the deck to PDF with LibreOffice and look at slides 1-3. Northeastern's bar is
   red, every bar has a school label and a value, nothing overlaps or leaves the slide.
5. Commit data and outputs, push to the working branch.
6. Email brettcsweet@gmail.com, subject `FY26 Endowment Tracker — Weekly Update YYYY-MM-DD`:
   new disclosures (school, metric, value, source), other changes, how many of 51 remain unreported
   per metric, GitHub links to both files, and the .xlsx attached. If nothing changed, send one line
   saying so with the remaining counts.
7. When every institution has a 1-year return, say so and suggest turning off the schedule or
   moving to a monthly cadence for the 5- and 10-year figures.

Note on attachments: the Gmail send tool has an undocumented attachment size ceiling somewhere
between ~9,900 and ~10,200 raw bytes (~13,200-13,600 base64 characters) — see the investigation
notes in the session history around 2026-09-28. `FY26_Endowment_Data_Top50.xlsx` (~12.7KB) is over
this ceiling, so it currently cannot be attached; link it instead and note the issue in the email
until the tool is fixed or the workbook is shrunk below the threshold.
