-- Remove the three seeded dummy/test bookings.
DELETE FROM bookings WHERE is_test = 1;

-- The brief's printed INSERT example contains 11 values, but bookings has 9 columns because
-- status and customer_rating are deliberately not stored by generate_data.py. The three rows
-- below preserve the intended booking_id/partner/city/category/date/amount/flags in the actual schema.
INSERT INTO bookings VALUES
  ('B9001','P009','Mumbai','Deep Home Cleaning','2026-03-31',3200,0,0,0),
  ('B9002','P041','Chennai','Plumbing','2026-03-31',640,0,0,0),
  ('B9003','P035','Hyderabad','Electrical Repair','2026-03-31',980,0,0,0);

-- Immediately after delete + insert: 600 rows and ₹10,47,973 total.
SELECT COUNT(*) AS bookings_count, SUM(amount_inr) AS total_revenue_inr FROM bookings;
-- Expected: 600 | 1047973

-- Fixed CSV export consumed by Parts B and C.
SELECT city,
       category,
       COUNT(*) AS bookings_count,
       SUM(amount_inr) AS revenue_inr,
       SUM(sla_breach_flag) AS sla_breaches
FROM bookings
GROUP BY city, category
ORDER BY city, category;
