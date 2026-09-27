# Daily endowment-returns update

Runs once a day until every school in `data/endowments.json` has a reported FY26 return.

Artifact (keep this URL): https://claude.ai/artifact/PMwVE9qqhexZZ2ABZ5sdro
Branch: `claude/zen-carson-xn1rkv`

## Steps

1. Check out the branch and pull the latest.
2. For every school with `"status": "pending"`, search for a published FY26 result
   (fiscal year ended June 30, 2026, or the school's own FY end in `fy_end`).
   Sources: the school's news office or investment office, annual financial report,
   student newspaper, Bloomberg, ai-cio.com, Pensions & Investments (pionline.com
   endowment returns tracker), Institutional Investor, WSJ, NYT, Charles Skorina.
   Many pages can't be fetched from the container; search-result text is acceptable
   when it quotes the school's figure.
3. Record only numbers with a source. For each newly found school set
   `fy26_return` (net %, one decimal), `fy26_value` ($B), `status: "reported"`,
   append the source URL to `sources`, and note anything unusual (pooled fund
   instead of total endowment, a different fiscal year end).
   Fill or correct `fy25_value` when a school's FY26 release restates it.
4. Update `as_of` to today's date.
5. `python3 scripts/build_report.py`
6. Commit (`Update FY26 endowment returns: <schools added>`) and push.
7. Republish `report/endowment-returns.html` to the artifact URL above.
8. Report to Brett: which schools were added today, with return and source, and
   how many of the 51 are still pending. If nothing new, say so in one line.

## Also on the list

- Confirm the peer set against usnews.com top-private (ranks 40-51 are single-source,
  and privates ranked ~60-90 may be missing). Four privates tie at No. 90, so 51 are listed.
- FY25 values flagged `weak` or `secondary` in `fy25_confidence`: replace with the
  school's audited figure when found.
- Placeholder return (`placeholder.return`, now 18.9% Wilshire TUCS median) applies to
  pending schools. Once 20+ schools have reported, switch it to the median of reported.

## Stop

When no school is pending, say so and ask Brett to stop the daily routine.
