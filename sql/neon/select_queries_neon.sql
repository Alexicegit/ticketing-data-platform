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
-----------------------------------------------------------------------------
Select * from b2b_ticketing.commission_agreements;
Select * from b2b_ticketing.customers;
Select * from b2b_ticketing.events;
Select * from b2b_ticketing.organizers;
Select * from b2b_ticketing.resellers;
Select * from b2b_ticketing.ticket_sales;

---------------------------------------------------------------------------
-- truncate tables --
/*truncate table b2b_ticketing.commission_agreements cascade;
truncate table b2b_ticketing.customers cascade;
truncate table b2b_ticketing.events cascade;
truncate table b2b_ticketing.organizers cascade;
truncate table b2b_ticketing.resellers cascade;
truncate table b2b_ticketing.ticket_sales cascade;
*/
--------------------------------------------------------
