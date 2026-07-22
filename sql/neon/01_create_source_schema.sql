CREATE SCHEMA IF NOT EXISTS ticketing_src;
CREATE TABLE IF NOT EXISTS ticketing_src.organizer (
  organizer_id BIGSERIAL PRIMARY KEY,
  organizer_name VARCHAR(200) NOT NULL,
  country VARCHAR(100),
  region VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.reseller (
  reseller_id VARCHAR(20) PRIMARY KEY,
  reseller_name VARCHAR(200) NOT NULL,
  country VARCHAR(100),
  region VARCHAR(100),
  city VARCHAR(100),
  is_external BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.customer (
  customer_id BIGSERIAL PRIMARY KEY,
  customer_name VARCHAR(200) NOT NULL,
  customer_email VARCHAR(250) UNIQUE,
  country VARCHAR(100),
  region VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.venue (
  venue_id BIGSERIAL PRIMARY KEY,
  venue_name VARCHAR(200) NOT NULL,
  city VARCHAR(100),
  country VARCHAR(100),
  region VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.event (
  event_id BIGSERIAL PRIMARY KEY,
  organizer_id BIGINT REFERENCES ticketing_src.organizer(organizer_id),
  venue_id BIGINT REFERENCES ticketing_src.venue(venue_id),
  event_name VARCHAR(250),
  event_type VARCHAR(100),
  start_datetime TIMESTAMP,
  end_datetime TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.ticket_type (
  ticket_type_id BIGSERIAL PRIMARY KEY,
  event_id BIGINT REFERENCES ticketing_src.event(event_id),
  ticket_name VARCHAR(150),
  base_price NUMERIC(12,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ticketing_src.ticket_sale (
  sale_id BIGSERIAL PRIMARY KEY,
  sale_datetime TIMESTAMP NOT NULL,
  organizer_id BIGINT REFERENCES ticketing_src.organizer(organizer_id),
  reseller_id VARCHAR(20) REFERENCES ticketing_src.reseller(reseller_id),
  customer_id BIGINT REFERENCES ticketing_src.customer(customer_id),
  event_id BIGINT REFERENCES ticketing_src.event(event_id),
  ticket_type_id BIGINT REFERENCES ticketing_src.ticket_type(ticket_type_id),
  sold_by VARCHAR(20) CHECK (sold_by IN ('ORGANIZER','RESELLER')),
  sales_channel VARCHAR(50) CHECK (sales_channel IN ('ONSITE','WEB','MOBILE_APP','CALL_CENTRE','PARTNER_PORTAL')),
  quantity INTEGER CHECK (quantity > 0),
  unit_price NUMERIC(12,2),
  gross_amount NUMERIC(12,2),
  commission_rate NUMERIC(5,2),
  commission_amount NUMERIC(12,2),
  net_amount NUMERIC(12,2),
  currency VARCHAR(3) DEFAULT 'USD',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ticket_sale_updated_at ON ticketing_src.ticket_sale(updated_at);
