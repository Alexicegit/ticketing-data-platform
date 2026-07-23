-- =====================================================
-- SOURCE DATA VALIDATION
-- Project: Ticketing Data Platform
-- Schema : b2b_ticketing
-- =====================================================

-- =====================================================
-- 1. ROW COUNTS
-- =====================================================

SELECT 'organizers' AS table_name, COUNT(*) AS row_count
FROM b2b_ticketing.organizers

UNION ALL

SELECT 'resellers', COUNT(*)
FROM b2b_ticketing.resellers

UNION ALL

SELECT 'commission_agreements', COUNT(*)
FROM b2b_ticketing.commission_agreements

UNION ALL

SELECT 'events', COUNT(*)
FROM b2b_ticketing.events

UNION ALL

SELECT 'customers', COUNT(*)
FROM b2b_ticketing.customers

UNION ALL

SELECT 'ticket_sales', COUNT(*)
FROM b2b_ticketing.ticket_sales;

-- =====================================================
-- 2. DUPLICATE PRIMARY KEY CHECKS
-- Expected: 0 rows returned
-- =====================================================

SELECT organizer_id, COUNT(*)
FROM b2b_ticketing.organizers
GROUP BY organizer_id
HAVING COUNT(*) > 1;

SELECT reseller_id, COUNT(*)
FROM b2b_ticketing.resellers
GROUP BY reseller_id
HAVING COUNT(*) > 1;

SELECT event_id, COUNT(*)
FROM b2b_ticketing.events
GROUP BY event_id
HAVING COUNT(*) > 1;

SELECT customer_id, COUNT(*)
FROM b2b_ticketing.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

SELECT ticket_id, COUNT(*)
FROM b2b_ticketing.ticket_sales
GROUP BY ticket_id
HAVING COUNT(*) > 1;

-- =====================================================
-- 3. EVENT -> ORGANIZER RELATIONSHIP
-- Expected: 0
-- =====================================================

SELECT COUNT(*) AS invalid_events
FROM b2b_ticketing.events e
LEFT JOIN b2b_ticketing.organizers o
ON e.organizer_id = o.organizer_id
WHERE o.organizer_id IS NULL;

-- =====================================================
-- 4. COMMISSION AGREEMENT VALIDATION
-- Expected: 0
-- =====================================================

SELECT COUNT(*) AS invalid_commission_organizers
FROM b2b_ticketing.commission_agreements ca
LEFT JOIN b2b_ticketing.organizers o
ON ca.organizer_id = o.organizer_id
WHERE o.organizer_id IS NULL;

SELECT COUNT(*) AS invalid_commission_resellers
FROM b2b_ticketing.commission_agreements ca
LEFT JOIN b2b_ticketing.resellers r
ON ca.reseller_id = r.reseller_id
WHERE r.reseller_id IS NULL;

-- =====================================================
-- 5. TICKET SALES RELATIONSHIPS
-- Expected: 0
-- =====================================================

SELECT COUNT(*) AS invalid_event_reference
FROM b2b_ticketing.ticket_sales ts
LEFT JOIN b2b_ticketing.events e
ON ts.event_id = e.event_id
WHERE e.event_id IS NULL;

SELECT COUNT(*) AS invalid_customer_reference
FROM b2b_ticketing.ticket_sales ts
LEFT JOIN b2b_ticketing.customers c
ON ts.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS invalid_reseller_reference
FROM b2b_ticketing.ticket_sales ts
LEFT JOIN b2b_ticketing.resellers r
ON ts.reseller_id = r.reseller_id
WHERE r.reseller_id IS NULL;

-- =====================================================
-- 6. BUSINESS RULE VALIDATION
------------------------------

-- A reseller can only sell tickets for organizers
-- where a commission agreement exists.
---------------------------------------

-- Expected: 0
-- =====================================================

SELECT COUNT(*) AS sales_without_commission_agreement
FROM b2b_ticketing.ticket_sales ts
JOIN b2b_ticketing.events e
ON ts.event_id = e.event_id
LEFT JOIN b2b_ticketing.commission_agreements ca
ON ca.organizer_id = e.organizer_id
AND ca.reseller_id = ts.reseller_id
WHERE ca.agreement_id IS NULL;

-- =====================================================
-- 7. COMMISSION RATE CHECK
-- Expected: 0
-- =====================================================

SELECT COUNT(*) AS invalid_commission_rates
FROM b2b_ticketing.commission_agreements
WHERE commission_rate < 0
OR commission_rate > 100;

-- =====================================================
-- 8. SALES AMOUNT VALIDATION
-- Expected:
-- 0 if clean data
-- >0 if intentional bad records exist
-- =====================================================

SELECT COUNT(*) AS invalid_amounts
FROM b2b_ticketing.ticket_sales
WHERE ROUND(quantity * unit_price, 2) <> total_amount;

-- =====================================================
-- 9. NEGATIVE QUANTITY CHECK
-- =====================================================

SELECT COUNT(*) AS invalid_quantity
FROM b2b_ticketing.ticket_sales
WHERE quantity <= 0;

-- =====================================================
-- 10. NEGATIVE PRICE CHECK
-- =====================================================

SELECT COUNT(*) AS invalid_price
FROM b2b_ticketing.ticket_sales
WHERE unit_price <= 0;

-- =====================================================
-- 11. NULL CRITICAL FIELDS
-- =====================================================

SELECT COUNT(*) AS null_event_ids
FROM b2b_ticketing.ticket_sales
WHERE event_id IS NULL;

SELECT COUNT(*) AS null_customer_ids
FROM b2b_ticketing.ticket_sales
WHERE customer_id IS NULL;

SELECT COUNT(*) AS null_reseller_ids
FROM b2b_ticketing.ticket_sales
WHERE reseller_id IS NULL;

-- =====================================================
-- 12. DATE RANGE VALIDATION
-- =====================================================

SELECT
MIN(event_date) AS min_event_date,
MAX(event_date) AS max_event_date
FROM b2b_ticketing.events;

SELECT
MIN(purchase_date) AS min_purchase_date,
MAX(purchase_date) AS max_purchase_date
FROM b2b_ticketing.ticket_sales;

-- =====================================================
-- 13. REVENUE BY YEAR
-- Business sanity check
-- =====================================================

SELECT
EXTRACT(YEAR FROM purchase_date) AS sales_year,
COUNT(*) AS transactions,
SUM(quantity) AS tickets_sold,
ROUND(SUM(total_amount), 2) AS revenue
FROM b2b_ticketing.ticket_sales
GROUP BY 1
ORDER BY 1;

-- =====================================================
-- 14. TOP 10 EVENTS BY REVENUE
-- =====================================================

SELECT
e.event_name,
ROUND(SUM(ts.total_amount), 2) AS revenue
FROM b2b_ticketing.ticket_sales ts
JOIN b2b_ticketing.events e
ON ts.event_id = e.event_id
GROUP BY e.event_name
ORDER BY revenue DESC
LIMIT 10;

-- =====================================================
-- 15. TOP 10 RESELLERS BY REVENUE
-- =====================================================

SELECT
r.reseller_name,
ROUND(SUM(ts.total_amount), 2) AS revenue
FROM b2b_ticketing.ticket_sales ts
JOIN b2b_ticketing.resellers r
ON ts.reseller_id = r.reseller_id
GROUP BY r.reseller_name
ORDER BY revenue DESC
LIMIT 10;

-- =====================================================
-- END OF VALIDATION SCRIPT
-- =====================================================
