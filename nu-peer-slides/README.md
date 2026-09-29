# Peer slides: Northeastern rebrand (DRAFT)

Three slides from the uploaded `analyze_update.pptx`, rebuilt on the official Northeastern template (Lato, red `#C8102E`, black rules, source left / "Northeastern University" right).

| File | What it is |
|---|---|
| `NU_peer_slides_rebrand_DRAFT.pptx` | The deck. Native charts (right-click > Edit Data). Speaker notes list what changed and the checks run. |
| `NU_peer_slides_backup.xlsx` | Data behind each slide with live formulas, the checks log, and the data still needed. |
| `previews/` | LibreOffice renders of the three slides (fonts and marker draw order differ slightly from PowerPoint). |
| `pipeline/` | Scripts that rebuild both files. `inputs/` holds the data extracted from the original deck. |

## Status
Rebrand is done on the **existing** data (Oct 2023 Scorecard, 2014-2024 survey values, FY23 financials). The data refresh is **not** done: the working session's network policy blocked collegescorecard.ed.gov, nces.ed.gov, insidehighered.com and the university finance sites. See the `Data_needed` sheet in the backup workbook.

## Rebuild
```
cd pipeline
python3 prep_base.py <NU-Official-Template-White.potx> base.pptx .   # template from the northeastern-brand skill
python3 build_deck.py ../NU_peer_slides_rebrand_DRAFT.pptx
python3 build_backup.py ../NU_peer_slides_backup.xlsx
python3 qa_labels.py <rendered.pdf>     # label overlap / bounds check on a LibreOffice PDF render
python3 brand_audit.py <deck.pptx>      # palette, typeface, shape audit
```
Set `DRAFT = False` in `build_deck.py` to drop the red draft tags once data is refreshed.
