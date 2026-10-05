-- (a) List every duplicated partner_id in the raw import.
SELECT partner_id, COUNT(*) AS duplicate_count
FROM partners_import
GROUP BY partner_id
HAVING COUNT(*) > 1
ORDER BY partner_id;

-- (b) Build the clean partner table by collapsing exact duplicate rows.
DROP TABLE IF EXISTS partners;
CREATE TABLE partners AS
SELECT partner_id, city, primary_category, rating, active, days_since_onboarding
FROM partners_import
GROUP BY partner_id, city, primary_category, rating, active, days_since_onboarding;

-- Confirm all bookings resolve to a real clean partner.
SELECT COUNT(*) AS booking_rows, COUNT(p.partner_id) AS matched_partner_rows
FROM bookings b
INNER JOIN partners p ON b.partner_id = p.partner_id;

-- Find categories that have never received a booking.
SELECT c.category
FROM categories c
LEFT JOIN bookings b ON c.category = b.category
WHERE b.booking_id IS NULL;

-- Find partners that have never received a booking.
SELECT p.partner_id, p.city, p.primary_category
FROM partners p
LEFT JOIN bookings b ON p.partner_id = b.partner_id
WHERE b.booking_id IS NULL
ORDER BY p.partner_id;

-- Compare COUNT(*) with COUNT(b.booking_id) on the category LEFT JOIN.
SELECT c.category,
       COUNT(*) AS joined_row_count,
       COUNT(b.booking_id) AS matched_booking_count
FROM categories c
LEFT JOIN bookings b ON c.category = b.category
GROUP BY c.category
ORDER BY c.category;
-- For Pest Control, COUNT(*) = 1 because the unmatched category still contributes one joined row;
-- COUNT(b.booking_id) = 0 because that synthetic row has a NULL booking_id.

-- Find clean partners whose primary category starts with Salon.
SELECT partner_id, city, primary_category, rating
FROM partners
WHERE primary_category LIKE 'Salon%'
ORDER BY partner_id;
