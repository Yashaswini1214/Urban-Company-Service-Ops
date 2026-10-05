import sqlite3

sample_bookings = [
    {"booking_id": "B0005", "category": "AC Repair & Service", "amount_inr": 1316},
    {"booking_id": "B0019", "category": "AC Repair & Service", "amount_inr": 538},
    {"booking_id": "B0027", "category": "AC Repair & Service", "amount_inr": 1016},
    {"booking_id": "B0055", "category": "AC Repair & Service", "amount_inr": 1505},
    {"booking_id": "B0001", "category": "Plumbing", "amount_inr": 1369},
    {"booking_id": "B0003", "category": "Plumbing", "amount_inr": 772},
    {"booking_id": "B0004", "category": "Plumbing", "amount_inr": 1133},
    {"booking_id": "B0006", "category": "Plumbing", "amount_inr": 805},
    {"booking_id": "B0018", "category": "Salon for Men", "amount_inr": 1414},
    {"booking_id": "B0024", "category": "Salon for Men", "amount_inr": 1176},
    {"booking_id": "B0029", "category": "Salon for Men", "amount_inr": 858},
    {"booking_id": "B0032", "category": "Salon for Men", "amount_inr": 638},
]

category_stats = {}
for row in sample_bookings:
    category = row["category"]
    if category not in category_stats:
        category_stats[category] = {"count": 0, "total": 0}
    category_stats[category]["count"] += 1
    category_stats[category]["total"] += row["amount_inr"]

for category in sorted(category_stats):
    print(f"{category} — count {category_stats[category]['count']}, total ₹{category_stats[category]['total']:,}")

ids = [row["booking_id"] for row in sample_bookings]
placeholders = ",".join("?" for _ in ids)
conn = sqlite3.connect("urban_service.db")
cur = conn.cursor()
cur.execute(
    f"SELECT category, COUNT(*), SUM(amount_inr) FROM bookings WHERE booking_id IN ({placeholders}) GROUP BY category ORDER BY category",
    ids,
)
sql_results = cur.fetchall()
conn.close()

python_results = [(category, category_stats[category]["count"], category_stats[category]["total"])
                  for category in sorted(category_stats)]
assert sql_results == python_results

# SQL result matches pure-Python result exactly for all three categories.
print("SQL cross-check: MATCH")
