# Urban Company Service-Ops Diagnostic & AI-Augmented Reporting Toolkit

This public repository is the single connected deliverable for Parts A–D.

## Tableau Public dashboard

**Live Tableau Public dashboard:** TABLEAU_PUBLIC_URL_TO_PASTE_HERE

The dashboard specification is documented in `TABLEAU_BUILD_NOTES.md`. A live Tableau Public publication requires the owner's Tableau Public session; the repository does not invent a dashboard URL that has not been published.

## Part A — Data Setup, Python Sanity-Check & SQL Diagnostic

- `generate_data.py` — exact deterministic generator with `random.seed(2604)`.
- `urban_service.db` — SQLite database after the clean-partner and delete/insert workflow.
- `cities.csv`, `categories.csv`, `partners_import.csv`, `bookings.csv` — generated seed exports.
- `verify_output.txt` — initial row-count checks.
- `sanity_check.py` — pure-Python category check plus SQLite cross-check.
- `01_dedup_and_joins.sql` — duplicate detection, clean-partner creation, join diagnostics, count comparison, and `LIKE 'Salon%'`.
- `02_insert_delete.sql` — removal of the 3 seeded test rows, schema-correct insertion of the 3 specified replacement bookings, final KPI query, and the fixed export query.
- `city_category_summary.csv` — the fixed 27-row export consumed by Parts B and C.

Acceptance checks include 7 categories, 52 raw partner rows, 600 initial bookings, duplicate IDs P003/P017/P031, 49 clean partners, Pest Control as the zero-booking category, P049 as the idle partner, 600 final bookings, ₹10,47,973 final revenue, 79 SLA breaches, and a 13.2% overall SLA breach rate.

### Schema clarification

The brief prints an 11-value INSERT example even though the supplied generator creates a 9-column `bookings` table because `status` and `customer_rating` are deliberately not stored. The repository uses the schema-correct 9-column insert so the generator and acceptance totals remain consistent.

## Part B — Spreadsheet Cross-Check & KPI Workbook

`urban_service_ops_kpi_workbook.xlsx` contains:

- `City-Category Data` — the fixed CSV import plus working exact-match VLOOKUP formulas for min/max price bands.
- `Category Reference` — the six specified category price bands.
- `Pivot Table` — city × category revenue cross-tab from the fixed data.
- `KPI Summary` — SUMIFS/COUNTIFS metrics, Part A totals, reconciliation formulas, and best/worst revenue conditional formatting.

The six city revenue totals reconcile to Part A exactly: Pune ₹2,28,727; Bengaluru ₹1,79,835; Chennai ₹1,75,572; Hyderabad ₹1,71,638; Mumbai ₹1,51,430; Delhi NCR ₹1,40,771.

## Part C — Tableau Dashboard & Storytelling

- `DASHBOARD_STORY.md` contains exactly two narratives: City Ops Lead and Category Lead.
- `TABLEAU_BUILD_NOTES.md` specifies the KPI cards, SLA Breach Rate calculation, Month Focus parameter, category bar chart, geographic map, City → Category drill-down, and cross-chart filter.

## Part D — AI-Augmented Reporting

- `prompt_pack.md` contains all three prompts and the critic-and-refine exchange.
- `escalation_agent_spec.md` contains the four ordered rules, five guardrails, logging fields, and the required eight-booking hand trace.

## Generated-artifact build

`.github/workflows/build-artifacts.yml` regenerates the deterministic seed, applies the SQL workflow, exports the fixed CSV, builds the workbook, runs the Python sanity check, and commits the generated database/CSV/workbook outputs.

