select
    agreement_id,
    organizer_id,
    reseller_id,
    commission_rate 
from {{ ref('stg_commissions') }}
where commission_rate  < 0
   or commission_rate  > 100
   or commission_rate  is null