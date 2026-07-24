/*==============================================================
  COMMISSION_AGREEMENTS
==============================================================*/

MERGE INTO RAW.COMMISSION_AGREEMENTS tgt
USING RAW.STG_COMMISSION_AGREEMENTS src
ON tgt.ORGANIZER_ID = src.ORGANIZER_ID
AND tgt.RESELLER_ID = src.RESELLER_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  CUSTOMERS
==============================================================*/

MERGE INTO RAW.CUSTOMERS tgt
USING RAW.STG_CUSTOMERS src
ON tgt.CUSTOMER_ID = src.CUSTOMER_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  EVENTS
==============================================================*/

MERGE INTO RAW.EVENTS tgt
USING RAW.STG_EVENTS src
ON tgt.EVENT_ID = src.EVENT_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  ORGANIZERS
==============================================================*/

MERGE INTO RAW.ORGANIZERS tgt
USING RAW.STG_ORGANIZERS src
ON tgt.ORGANIZER_ID = src.ORGANIZER_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  RESELLERS
==============================================================*/

MERGE INTO RAW.RESELLERS tgt
USING RAW.STG_RESELLERS src
ON tgt.RESELLER_ID = src.RESELLER_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  RESELLER_DAILY_SALES
==============================================================*/

MERGE INTO RAW.RESELLER_DAILY_SALES tgt
USING RAW.STG_RESELLER_DAILY_SALES src
ON tgt.RESELLER_ID = src.RESELLER_ID
AND tgt.SALE_DATE = src.SALE_DATE

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;


/*==============================================================
  TICKET_SALES
==============================================================*/

MERGE INTO RAW.TICKET_SALES tgt
USING RAW.STG_TICKET_SALES src
ON tgt.TICKET_ID = src.TICKET_ID

WHEN MATCHED
AND src.UPDATED_AT > tgt.UPDATED_AT
THEN UPDATE ALL BY NAME

WHEN NOT MATCHED
THEN INSERT ALL BY NAME;