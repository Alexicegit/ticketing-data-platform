-- ============================================================
-- DATABASE & SCHEMAS
-- ============================================================

CREATE DATABASE IF NOT EXISTS B2B_EVENT_TICKETING;

USE DATABASE B2B_EVENT_TICKETING;

CREATE SCHEMA IF NOT EXISTS RAW;
USE SCHEMA RAW;

-- ============================================================
-- RAW TABLES - POSTGRES SOURCE SYSTEM
-- ============================================================

CREATE OR REPLACE TABLE RAW.ORGANIZERS (

    ORGANIZER_ID        VARCHAR(20)      NOT NULL,
    ORGANIZER_NAME      VARCHAR(200)     NOT NULL,
    COUNTRY             VARCHAR(100),
    REGION              VARCHAR(100),

    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)      DEFAULT 'POSTGRES'

);

CREATE OR REPLACE TABLE RAW.RESELLERS (

    RESELLER_ID         VARCHAR(20)      NOT NULL,
    RESELLER_NAME       VARCHAR(200)     NOT NULL,
    COUNTRY             VARCHAR(100),
    REGION              VARCHAR(100),

    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)      DEFAULT 'POSTGRES'

);

CREATE OR REPLACE TABLE RAW.COMMISSION_AGREEMENTS (

    AGREEMENT_ID        NUMBER(38,0)     NOT NULL,
    ORGANIZER_ID        VARCHAR(20)      NOT NULL,
    RESELLER_ID         VARCHAR(20)      NOT NULL,

    COMMISSION_RATE     NUMBER(5,2)      NOT NULL,

    EFFECTIVE_FROM      DATE             NOT NULL,
    EFFECTIVE_TO        DATE             NOT NULL,

    UPDATED_AT          TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)      DEFAULT 'POSTGRES'

);

CREATE OR REPLACE TABLE RAW.EVENTS (

    EVENT_ID            VARCHAR(20)      NOT NULL,
    ORGANIZER_ID        VARCHAR(20)      NOT NULL,

    EVENT_NAME          VARCHAR(300)     NOT NULL,
    EVENT_TYPE          VARCHAR(100),
    VENUE               VARCHAR(300),
    REGION              VARCHAR(100),

    EVENT_DATE          DATE             NOT NULL,

    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)      DEFAULT 'POSTGRES'

);

CREATE OR REPLACE TABLE RAW.CUSTOMERS (

    CUSTOMER_ID         VARCHAR(20)      NOT NULL,

    FIRST_NAME          VARCHAR(100),
    LAST_NAME           VARCHAR(100),
    EMAIL               VARCHAR(255),
    COUNTRY             VARCHAR(100),

    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)      DEFAULT 'POSTGRES'

);

CREATE OR REPLACE TABLE RAW.TICKET_SALES (

    ------------------------------------------------------------------
    -- Transaction Key
    ------------------------------------------------------------------
    TICKET_ID           VARCHAR(20)      NOT NULL,

    ------------------------------------------------------------------
    -- Business Keys
    ------------------------------------------------------------------
    EVENT_ID            VARCHAR(20)      NOT NULL,
    ORGANIZER_ID        VARCHAR(20)      NOT NULL,
    RESELLER_ID         VARCHAR(20),

    ------------------------------------------------------------------
    -- Seller Information
    ------------------------------------------------------------------
    SELLER_TYPE         VARCHAR(20)      NOT NULL,
    SELLER_ID           VARCHAR(20)      NOT NULL,
    SELLER_NAME         VARCHAR(200)     NOT NULL,

    ------------------------------------------------------------------
    -- Customer Information
    ------------------------------------------------------------------
    CUSTOMER_ID         VARCHAR(20)      NOT NULL,

    ------------------------------------------------------------------
    -- Sales Information
    ------------------------------------------------------------------
    SALES_CHANNEL       VARCHAR(30)      NOT NULL,
    QUANTITY            NUMBER(10,0)     NOT NULL,
    UNIT_PRICE          NUMBER(10,2)     NOT NULL,
    TOTAL_AMOUNT        NUMBER(12,2)     NOT NULL,
    PURCHASE_DATE       DATE             NOT NULL,

    ------------------------------------------------------------------
    -- ETL Metadata
    ------------------------------------------------------------------
    BATCH_ID            VARCHAR(100)     NOT NULL,
    UPDATED_AT          TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    LOAD_TS             TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM       VARCHAR(50)

);

-- ============================================================
-- RAW TABLE - RESELLER CSV SOURCE
-- ============================================================

CREATE OR REPLACE TABLE RAW.RESELLER_DAILY_SALES (

    TRANSACTION_ID                  NUMBER(38,0)     NOT NULL,

    RESELLER_ID                     VARCHAR(20)      NOT NULL,

    EVENT_NAME                      VARCHAR(300),

    NUMBER_OF_PURCHASED_TICKETS     NUMBER(10,0),

    TOTAL_AMOUNT                    NUMBER(12,2),

    SALES_CHANNEL                   VARCHAR(30),

    CUSTOMER_FIRST_NAME             VARCHAR(100),
    CUSTOMER_LAST_NAME              VARCHAR(100),

    OFFICE_LOCATION                 VARCHAR(200),

    CREATED_DATE                    DATE,

    SOURCE_FILE_NAME                VARCHAR(255),

    LOAD_TS                         TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_SYSTEM                   VARCHAR(50)      DEFAULT 'CSV'

);

-- ============================================================
-- RAW LOAD AUDIT TABLE
-- ============================================================

CREATE OR REPLACE TABLE RAW.LOAD_AUDIT (

    LOAD_ID             NUMBER(38,0) AUTOINCREMENT,

    SOURCE_SYSTEM       VARCHAR(50),
    SOURCE_OBJECT       VARCHAR(200),

    LOAD_START_TIME     TIMESTAMP_NTZ,
    LOAD_END_TIME       TIMESTAMP_NTZ,

    RECORDS_READ        NUMBER(38,0),
    RECORDS_LOADED      NUMBER(38,0),
    RECORDS_REJECTED    NUMBER(38,0),

    STATUS              VARCHAR(50),

    CREATED_TS          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()

);

-- ============================================================
-- FILE HISTORY
-- ============================================================

CREATE OR REPLACE TABLE RAW.FILE_HISTORY (

    FILE_NAME           VARCHAR(255),

    SOURCE_SYSTEM       VARCHAR(50),

    FILE_DATE           DATE,

    LOAD_TIMESTAMP      TIMESTAMP_NTZ,

    RECORD_COUNT        NUMBER(38,0),

    STATUS              VARCHAR(50)

);

-- ============================================================
-- AUDIT SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS AUDIT;

-- ============================================================
-- FILE LOAD HISTORY
-- ============================================================

CREATE OR REPLACE TABLE AUDIT.FILE_LOAD_HISTORY (

    FILE_NAME           VARCHAR(255),
    FILE_SHA            VARCHAR(100),

    LOAD_DATE           TIMESTAMP_NTZ,

    RECORD_COUNT        NUMBER(38,0),

    STATUS              VARCHAR(50),

    ERROR_MESSAGE       VARCHAR(1000)

);

-- ============================================================
-- JOB AUDIT
-- ============================================================

CREATE OR REPLACE TABLE AUDIT.JOB_AUDIT (

    JOB_NAME            VARCHAR(200),

    START_TIME          TIMESTAMP_NTZ,
    END_TIME            TIMESTAMP_NTZ,

    STATUS              VARCHAR(50),

    RECORDS_LOADED      NUMBER(38,0),

    FILES_PROCESSED     NUMBER(38,0),

    ERROR_MESSAGE       VARCHAR(1000)

);

-- ============================================================
-- VERIFY OBJECTS
-- ============================================================

SHOW TABLES IN SCHEMA RAW;
SHOW TABLES IN SCHEMA AUDIT;