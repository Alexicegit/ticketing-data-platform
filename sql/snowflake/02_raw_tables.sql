USE DATABASE TICKETING_DB;
USE SCHEMA RAW;
CREATE FILE FORMAT IF NOT EXISTS CSV_FF TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('NULL','null','') EMPTY_FIELD_AS_NULL = TRUE;
CREATE STAGE IF NOT EXISTS RAW_CSV_STAGE FILE_FORMAT = CSV_FF;
CREATE TABLE IF NOT EXISTS RAW_PLATFORM_SALES (
 sale_id NUMBER, sale_datetime TIMESTAMP_NTZ, organizer_id NUMBER, reseller_id VARCHAR, customer_id NUMBER, event_id NUMBER, ticket_type_id NUMBER,
 sold_by VARCHAR, sales_channel VARCHAR, quantity NUMBER, unit_price NUMBER(12,2), gross_amount NUMBER(12,2), commission_rate NUMBER(5,2),
 commission_amount NUMBER(12,2), net_amount NUMBER(12,2), currency VARCHAR, updated_at TIMESTAMP_NTZ, source_file VARCHAR, load_batch_id VARCHAR, loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS RAW_RESELLER_SALES (
 sale_date DATE, reseller_id VARCHAR, reseller_name VARCHAR, reseller_region VARCHAR, event_id NUMBER, event_name VARCHAR, event_type VARCHAR,
 ticket_type_id NUMBER, ticket_name VARCHAR, sales_channel VARCHAR, quantity NUMBER, unit_price NUMBER(12,2), gross_amount NUMBER(12,2), commission_rate NUMBER(5,2),
 customer_email VARCHAR, currency VARCHAR, source_file VARCHAR, file_sale_date DATE, load_batch_id VARCHAR, loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
);
