/*==============================================================================
SCHEMA: B2B_TICKETING

PURPOSE
-------
Source system for B2B Event Ticketing Analytics project.

BUSINESS ENTITIES
-----------------
1. CUSTOMERS
   - Who bought the ticket

2. ORGANIZERS
   - Event organizers

3. RESELLERS
   - Third-party ticket sellers
   - Supports reseller location reporting

4. COMMISSION_AGREEMENTS
   - Commission rates between organizers and resellers

5. EVENTS
   - Event master data

6. TICKET_SALES
   - Transaction fact table
   - Supports:
     * Who sold the ticket (Organizer / Reseller)
     * Sales Channel Analysis
     * Customer Analysis
     * Revenue Analysis
     * Commission Analysis
     * Weekly Sales Trends
==============================================================================*/


/*==============================================================================
CUSTOMERS
------------------------------------------------------------------------------
Stores customer information used for:
- Who bought the ticket
- Customer purchase analysis
- Top customers
==============================================================================*/

CREATE TABLE b2b_ticketing.customers (
    customer_id       VARCHAR(20) NOT NULL,
    first_name        VARCHAR(100),
    last_name         VARCHAR(100),
    email             VARCHAR(200),
    country           VARCHAR(50),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT customers_customer_id_not_null
        CHECK (customer_id IS NOT NULL),

    CONSTRAINT customers_pkey
        PRIMARY KEY (customer_id)
);

CREATE TRIGGER customers_updated_at
BEFORE UPDATE
ON b2b_ticketing.customers
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();


/*==============================================================================
ORGANIZERS
------------------------------------------------------------------------------
Stores event organizers.

Examples:
- ABC Events
- Global Sports Management
- Music Nation
==============================================================================*/

CREATE TABLE b2b_ticketing.organizers (
    organizer_id      VARCHAR(10) NOT NULL,
    organizer_name    VARCHAR(100),
    country           VARCHAR(50),
    region            VARCHAR(50),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT organizers_organizer_id_not_null
        CHECK (organizer_id IS NOT NULL),

    CONSTRAINT organizers_pkey
        PRIMARY KEY (organizer_id)
);

CREATE TRIGGER organizers_updated_at
BEFORE UPDATE
ON b2b_ticketing.organizers
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();


/*==============================================================================
RESELLERS
------------------------------------------------------------------------------
Stores reseller information.

Reporting Usage:
- Top Resellers
- Reseller Location Analysis
- Commission Analysis
==============================================================================*/

CREATE TABLE b2b_ticketing.resellers (
    reseller_id       VARCHAR(10) NOT NULL,
    reseller_name     VARCHAR(100),
    country           VARCHAR(50),
    region            VARCHAR(50),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT resellers_reseller_id_not_null
        CHECK (reseller_id IS NOT NULL),

    CONSTRAINT resellers_pkey
        PRIMARY KEY (reseller_id)
);

CREATE TRIGGER resellers_updated_at
BEFORE UPDATE
ON b2b_ticketing.resellers
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();


/*==============================================================================
COMMISSION AGREEMENTS
------------------------------------------------------------------------------
Defines commission rates between organizers and resellers.

Examples:
- Organizer A → Reseller X = 10%
- Organizer B → Reseller Y = 15%

Reporting Usage:
- Average Commission Rate
- Commission Analysis
- Commission vs Revenue
==============================================================================*/

CREATE TABLE b2b_ticketing.commission_agreements (
    agreement_id      SERIAL PRIMARY KEY,
    organizer_id      VARCHAR(10),
    reseller_id       VARCHAR(10),
    commission_rate   NUMERIC(5,2),
    effective_from    DATE,
    effective_to      DATE,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT commission_agreements_organizer_id_fkey
        FOREIGN KEY (organizer_id)
        REFERENCES b2b_ticketing.organizers (organizer_id),

    CONSTRAINT commission_agreements_reseller_id_fkey
        FOREIGN KEY (reseller_id)
        REFERENCES b2b_ticketing.resellers (reseller_id)
);

CREATE TRIGGER commission_agreements_updated_at
BEFORE UPDATE
ON b2b_ticketing.commission_agreements
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();


/*==============================================================================
EVENTS
------------------------------------------------------------------------------
Stores event master data.

Reporting Usage:
- Event Type Analysis
- Popular Events by Region
- Event Performance
==============================================================================*/

CREATE TABLE b2b_ticketing.events (
    event_id          VARCHAR(10) NOT NULL,
    organizer_id      VARCHAR(10),
    event_name        VARCHAR(200),
    event_type        VARCHAR(50),
    venue             VARCHAR(100),
    region            VARCHAR(50),
    event_date        DATE,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT events_event_id_not_null
        CHECK (event_id IS NOT NULL),

    CONSTRAINT events_pkey
        PRIMARY KEY (event_id),

    CONSTRAINT events_organizer_id_fkey
        FOREIGN KEY (organizer_id)
        REFERENCES b2b_ticketing.organizers (organizer_id)
);

-- Performance indexes for reporting
CREATE INDEX idx_events_event_type
ON b2b_ticketing.events (event_type);

CREATE INDEX idx_events_region
ON b2b_ticketing.events (region);

CREATE TRIGGER events_updated_at
BEFORE UPDATE
ON b2b_ticketing.events
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();


/*==============================================================================
TICKET SALES (FACT TABLE)
------------------------------------------------------------------------------
Core transactional table.

BUSINESS QUESTIONS ANSWERED
---------------------------
✓ Who sold the ticket?
✓ Organizer vs Reseller sales
✓ Who bought the ticket?
✓ Total amount and quantity
✓ Sales channel performance
✓ Weekly sales trends
✓ Top customers
✓ Top resellers
✓ Revenue analysis

COLUMN EXPLANATION
------------------
seller_type    : ORGANIZER / RESELLER
seller_id      : Generic seller identifier
seller_name    : Organizer or Reseller Name
sales_channel  : WEB, MOBILE_APP, ON_SITE, etc.
quantity       : Number of tickets purchased
unit_price     : Price per ticket
total_amount   : Total transaction amount
==============================================================================*/

CREATE TABLE b2b_ticketing.ticket_sales (

    -- Transaction Keys
    ticket_id         VARCHAR(20) NOT NULL,

    -- Business Keys
    event_id          VARCHAR(20) NOT NULL,
    organizer_id      VARCHAR(20) NOT NULL,
    reseller_id       VARCHAR(20),

    -- Seller Information
    seller_type       VARCHAR(20) NOT NULL,
    seller_id         VARCHAR(20) NOT NULL,
    seller_name       VARCHAR(200) NOT NULL,

    -- Buyer Information
    customer_id       VARCHAR(20) NOT NULL,

    -- Channel Information
    sales_channel     VARCHAR(30) NOT NULL,

    -- Transaction Metrics
    quantity          INTEGER NOT NULL,
    unit_price        NUMERIC(10,2) NOT NULL,
    total_amount      NUMERIC(12,2) NOT NULL,

    -- Transaction Date
    purchase_date     DATE NOT NULL,

    -- Audit Columns
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ticket_sales_pkey
        PRIMARY KEY (ticket_id),

    CONSTRAINT fk_ticket_customer
        FOREIGN KEY (customer_id)
        REFERENCES b2b_ticketing.customers (customer_id),

    CONSTRAINT fk_ticket_event
        FOREIGN KEY (event_id)
        REFERENCES b2b_ticketing.events (event_id),

    CONSTRAINT fk_ticket_organizer
        FOREIGN KEY (organizer_id)
        REFERENCES b2b_ticketing.organizers (organizer_id),

    CONSTRAINT fk_ticket_reseller
        FOREIGN KEY (reseller_id)
        REFERENCES b2b_ticketing.resellers (reseller_id)
);



/*==============================================================================
FACT TABLE INDEXES
------------------------------------------------------------------------------
Recommended indexes for reporting performance
==============================================================================*/

CREATE INDEX idx_ticket_sales_purchase_date
ON b2b_ticketing.ticket_sales (purchase_date);

CREATE INDEX idx_ticket_sales_event_id
ON b2b_ticketing.ticket_sales (event_id);

CREATE INDEX idx_ticket_sales_customer_id
ON b2b_ticketing.ticket_sales (customer_id);

CREATE INDEX idx_ticket_sales_reseller_id
ON b2b_ticketing.ticket_sales (reseller_id);

CREATE INDEX idx_ticket_sales_sales_channel
ON b2b_ticketing.ticket_sales (sales_channel);

CREATE INDEX idx_ticket_sales_seller_type
ON b2b_ticketing.ticket_sales (seller_type);

CREATE INDEX idx_ticket_sales_purchase_date_channel
ON b2b_ticketing.ticket_sales (
    purchase_date,
    sales_channel
);


/*==============================================================================
UPDATE TRIGGER
==============================================================================*/

CREATE TRIGGER ticket_sales_updated_at
BEFORE UPDATE
ON b2b_ticketing.ticket_sales
FOR EACH ROW
EXECUTE FUNCTION b2b_ticketing.update_modified_timestamp();