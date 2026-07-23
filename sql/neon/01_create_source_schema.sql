/******************************************************************************
 Project        : B2B Event Ticketing Platform
 Database       : PostgreSQL / Neon PostgreSQL
 Schema         : b2b_ticketing
 Description    : Source OLTP schema for ticketing sales platform
******************************************************************************/

-- ============================================================================
-- 1. CREATE SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS b2b_ticketing;

-- ============================================================================
-- 2. CLEANUP EXISTING OBJECTS
--    Drop child tables first, then parent tables
-- ============================================================================

DROP TABLE IF EXISTS b2b_ticketing.ticket_sales CASCADE;
DROP TABLE IF EXISTS b2b_ticketing.commission_agreements CASCADE;
DROP TABLE IF EXISTS b2b_ticketing.events CASCADE;
DROP TABLE IF EXISTS b2b_ticketing.customers CASCADE;
DROP TABLE IF EXISTS b2b_ticketing.resellers CASCADE;
DROP TABLE IF EXISTS b2b_ticketing.organizers CASCADE;

-- ============================================================================
-- 3. MASTER TABLES
-- ============================================================================

------------------------------------------------------------------------------
-- ORGANIZERS
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.organizers
(
    organizer_id     VARCHAR(10) PRIMARY KEY,
    organizer_name   VARCHAR(100) NOT NULL,
    country          VARCHAR(50),
    region           VARCHAR(50)
);

COMMENT ON TABLE b2b_ticketing.organizers
IS 'Event organizers responsible for managing events';

------------------------------------------------------------------------------
-- RESELLERS
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.resellers
(
    reseller_id      VARCHAR(10) PRIMARY KEY,
    reseller_name    VARCHAR(100) NOT NULL,
    country          VARCHAR(50),
    region           VARCHAR(50)
);

COMMENT ON TABLE b2b_ticketing.resellers
IS 'Ticket resellers selling tickets on behalf of organizers';

------------------------------------------------------------------------------
-- CUSTOMERS
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.customers
(
    customer_id      VARCHAR(20) PRIMARY KEY,
    first_name       VARCHAR(100),
    last_name        VARCHAR(100),
    email            VARCHAR(200),
    country          VARCHAR(50)
);

COMMENT ON TABLE b2b_ticketing.customers
IS 'End customers purchasing event tickets';

-- ============================================================================
-- 4. TRANSACTIONAL / REFERENCE TABLES
-- ============================================================================

------------------------------------------------------------------------------
-- COMMISSION AGREEMENTS
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.commission_agreements
(
    agreement_id      SERIAL PRIMARY KEY,

    organizer_id      VARCHAR(10) NOT NULL,
    reseller_id       VARCHAR(10) NOT NULL,

    commission_rate   NUMERIC(5,2),

    effective_from    DATE,
    effective_to      DATE,

    CONSTRAINT fk_commission_organizer
        FOREIGN KEY (organizer_id)
        REFERENCES b2b_ticketing.organizers (organizer_id),

    CONSTRAINT fk_commission_reseller
        FOREIGN KEY (reseller_id)
        REFERENCES b2b_ticketing.resellers (reseller_id)
);

COMMENT ON TABLE b2b_ticketing.commission_agreements
IS 'Commission percentages agreed between organizers and resellers';

------------------------------------------------------------------------------
-- EVENTS
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.events
(
    event_id          VARCHAR(10) PRIMARY KEY,

    organizer_id      VARCHAR(10) NOT NULL,

    event_name        VARCHAR(200) NOT NULL,
    event_type        VARCHAR(50),

    venue             VARCHAR(100),
    region            VARCHAR(50),

    event_date        DATE NOT NULL,

    CONSTRAINT fk_events_organizer
        FOREIGN KEY (organizer_id)
        REFERENCES b2b_ticketing.organizers (organizer_id)
);

COMMENT ON TABLE b2b_ticketing.events
IS 'List of events managed by organizers';

------------------------------------------------------------------------------
-- TICKET SALES
------------------------------------------------------------------------------

CREATE TABLE b2b_ticketing.ticket_sales
(
    ticket_id         VARCHAR(20) PRIMARY KEY,

    event_id          VARCHAR(10) NOT NULL,
    customer_id       VARCHAR(20) NOT NULL,
    reseller_id       VARCHAR(10) NOT NULL,

    sales_channel     VARCHAR(50),

    quantity          INTEGER NOT NULL,

    unit_price        NUMERIC(10,2) NOT NULL,

    total_amount      NUMERIC(12,2) NOT NULL,

    purchase_date     DATE NOT NULL,

    CONSTRAINT fk_sales_event
        FOREIGN KEY (event_id)
        REFERENCES b2b_ticketing.events (event_id),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id)
        REFERENCES b2b_ticketing.customers (customer_id),

    CONSTRAINT fk_sales_reseller
        FOREIGN KEY (reseller_id)
        REFERENCES b2b_ticketing.resellers (reseller_id)
);

COMMENT ON TABLE b2b_ticketing.ticket_sales
IS 'Ticket sales transactions';

-- ============================================================================
-- 5. PERFORMANCE INDEXES
-- ============================================================================

------------------------------------------------------------------------------
-- TICKET SALES INDEXES
------------------------------------------------------------------------------

CREATE INDEX idx_ticket_sales_purchase_date
    ON b2b_ticketing.ticket_sales (purchase_date);

CREATE INDEX idx_ticket_sales_event_id
    ON b2b_ticketing.ticket_sales (event_id);

CREATE INDEX idx_ticket_sales_reseller_id
    ON b2b_ticketing.ticket_sales (reseller_id);

CREATE INDEX idx_ticket_sales_customer_id
    ON b2b_ticketing.ticket_sales (customer_id);

------------------------------------------------------------------------------
-- EVENTS INDEXES
------------------------------------------------------------------------------

CREATE INDEX idx_events_event_type
    ON b2b_ticketing.events (event_type);

CREATE INDEX idx_events_region
    ON b2b_ticketing.events (region);

CREATE INDEX idx_events_event_date
    ON b2b_ticketing.events (event_date);

-- ============================================================================
-- 6. VALIDATION QUERIES
-- ============================================================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'b2b_ticketing'
ORDER BY table_name;