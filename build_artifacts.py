import csv
import sqlite3
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent
DB = ROOT / "urban_service.db"

# Part A: apply the exact SQL workflow to the deterministic database.
conn = sqlite3.connect(DB)
with open(ROOT / "01_dedup_and_joins.sql", encoding="utf-8") as f:
    conn.executescript(f.read())
with open(ROOT / "02_insert_delete.sql", encoding="utf-8") as f:
    script = f.read()
    # The SQL file contains the final export SELECT; executescript is fine, then the
    # export is repeated below from the now-reconciled database.
    conn.executescript(script)
cur = conn.cursor()

summary_sql = """SELECT city, category, COUNT(*) AS bookings_count,
SUM(amount_inr) AS revenue_inr, SUM(sla_breach_flag) AS sla_breaches
FROM bookings
GROUP BY city, category
ORDER BY city, category"""
rows = cur.execute(summary_sql).fetchall()
conn.close()

with open(ROOT / "city_category_summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["city", "category", "bookings_count", "revenue_inr", "sla_breaches"])
    writer.writerows(rows)

# Part B: workbook built from the fixed CSV, never from the raw bookings export.
wb = Workbook()
ws = wb.active
ws.title = "City-Category Data"

with open(ROOT / "city_category_summary.csv", newline="", encoding="utf-8") as f:
    data = list(csv.reader(f))
for r_idx, row in enumerate(data, start=1):
    for c_idx, value in enumerate(row, start=1):
        cell = ws.cell(r_idx, c_idx, value=value)
        if r_idx == 1:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9EAF7")

# Add VLOOKUP formulas with absolute references.
ws["F1"] = "min_price_inr"
ws["G1"] = "max_price_inr"
for c in ("F1", "G1"):
    ws[c].font = Font(bold=True)
    ws[c].fill = PatternFill("solid", fgColor="D9EAF7")

for r in range(2, ws.max_row + 1):
    ws[f"F{r}"] = f'=VLOOKUP(B{r},\'Category Reference\'!$A$2:$C$7,2,FALSE)'
    ws[f"G{r}"] = f'=VLOOKUP(B{r},\'Category Reference\'!$A$2:$C$7,3,FALSE)'

for col in range(1, 8):
    ws.column_dimensions[get_column_letter(col)].width = 23

ref = wb.create_sheet("Category Reference")
ref.append(["category", "min_price_inr", "max_price_inr"])
bands = [
    ("AC Repair & Service", 499, 2499),
    ("Salon for Women", 699, 3499),
    ("Salon for Men", 349, 1499),
    ("Deep Home Cleaning", 999, 4999),
    ("Plumbing", 199, 1499),
    ("Electrical Repair", 199, 1999),
]
for row in bands:
    ref.append(row)
for c in ref[1]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="D9EAF7")
ref.column_dimensions["A"].width = 26
ref.column_dimensions["B"].width = 16
ref.column_dimensions["C"].width = 16

# Formula-driven pivot cross-check: equivalent to Rows=city, Columns=category,
# Values=SUM(revenue_inr), and built entirely from the fixed City-Category Data sheet.
pivot = wb.create_sheet("Pivot Table")
cities = ["Bengaluru", "Mumbai", "Delhi NCR", "Pune", "Hyderabad", "Chennai"]
categories = [b[0] for b in bands]
pivot.append(["city"] + categories)
for c in pivot[1]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="D9EAF7")
for r, city in enumerate(cities, start=2):
    pivot.cell(r, 1, city)
    for c, category in enumerate(categories, start=2):
        col_letter = get_column_letter(c)
        pivot.cell(
            r, c,
            f'=SUMIFS(\'City-Category Data\'!$D:$D,\'City-Category Data\'!$A:$A,$A{r},\'City-Category Data\'!$B:$B,{col_letter}$1)'
        )
pivot.column_dimensions["A"].width = 18
for c in range(2, len(categories) + 2):
    pivot.column_dimensions[get_column_letter(c)].width = 22

kpi = wb.create_sheet("KPI Summary")
kpi.append([
    "city", "total_revenue_inr", "total_sla_breaches",
    "city_category_combinations", "Part A SQL total", "Matches Part A SQL total?"
])
for c in kpi[1]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="D9EAF7")

part_a = {
    "Pune": 228727,
    "Bengaluru": 179835,
    "Chennai": 175572,
    "Hyderabad": 171638,
    "Mumbai": 151430,
    "Delhi NCR": 140771,
}
for r, city in enumerate(["Pune", "Bengaluru", "Chennai", "Hyderabad", "Mumbai", "Delhi NCR"], start=2):
    kpi.cell(r, 1, city)
    kpi.cell(r, 2, f'=SUMIFS(\'City-Category Data\'!$D:$D,\'City-Category Data\'!$A:$A,A{r})')
    kpi.cell(r, 3, f'=SUMIFS(\'City-Category Data\'!$E:$E,\'City-Category Data\'!$A:$A,A{r})')
    kpi.cell(r, 4, f'=COUNTIFS(\'City-Category Data\'!$A:$A,A{r})')
    kpi.cell(r, 5, part_a[city])
    kpi.cell(r, 6, f'=IF(B{r}=E{r},"Yes","No")')

highest_fill = PatternFill("solid", fgColor="C6EFCE")
lowest_fill = PatternFill("solid", fgColor="FFC7CE")
kpi.conditional_formatting.add("B2:B7", CellIsRule(operator="equal", formula=["MAX($B$2:$B$7)"], fill=highest_fill))
kpi.conditional_formatting.add("B2:B7", CellIsRule(operator="equal", formula=["MIN($B$2:$B$7)"], fill=lowest_fill))
for c in range(1, 7):
    kpi.column_dimensions[get_column_letter(c)].width = 28

for sheet in wb.worksheets:
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="center")
    sheet.freeze_panes = "A2"

out = ROOT / "urban_service_ops_kpi_workbook.xlsx"
wb.save(out)
print(f"Built {out.name} from the fixed city_category_summary.csv.")
