# Peer slides: Northeastern rebrand and FY25 refresh

Three slides rebuilt on the official Northeastern template (Lato, red `#C8102E`, black rules, source left / "Northeastern University" and page number right), with refreshed data.

| File | What it is |
|---|---|
| `NU_peer_slides_rebrand_DRAFT.pptx` | The deck. Native charts (right-click > Edit Data). Speaker notes list what changed, the checks run and the caveats. |
| `NU_peer_slides_backup.xlsx` | Data behind each slide with live formulas, verbatim source evidence, the FY23 recalculation, sensitivity tests, checks log and open items. |
| `previews/` | LibreOffice renders of the three slides (font metrics differ slightly from PowerPoint). |
| `pipeline/` | Scripts that rebuild both files. `inputs/` holds the extracted data with sources. |

## Status
- **Slide 1:** College Scorecard release of June 10, 2026 (net price AY2023-24; 10-year earnings are the newest cohort Scorecard publishes, 2009-11 entrants measured 2020-21).
- **Slide 2:** Inside Higher Ed survey 2015-2026 re-read from the reports; four original rows corrected; 2025-26 carry a trustees-only item.
- **Slide 3:** FY25 audited statements for 14 schools including Northeastern, BU, MIT and Harvard (Harvard's FY25 Financial Report was supplied by Northeastern because finance.harvard.edu blocks automated access). Penn and Stanford salaries and wages are flagged estimates.
See the `Checks` and `Data_needed` sheets in the workbook.

## Rebuild
```
cd pipeline
python3 prep_base.py <NU-Official-Template-White.potx> base.pptx .      # template from the northeastern-brand skill
python3 prep_slide1_data.py <Most-Recent-Cohorts-Institution.csv> inputs/slide1_scorecard_jun2026.csv
python3 prep_slide3_data.py                                            # reads inputs/fin and inputs/enroll
python3 build_deck.py ../NU_peer_slides_rebrand_DRAFT.pptx
python3 build_backup.py ../NU_peer_slides_backup.xlsx
python3 qa_labels.py <rendered.pdf>      # label overlap / bounds check on a LibreOffice PDF render
python3 brand_audit.py <deck.pptx>       # palette, typeface, shape audit
```
Adding or updating a school: put its extraction in `inputs/fin/<name>.json` (same schema) and rerun `prep_slide3_data.py`, `build_deck.py`, `build_backup.py`.
