from pathlib import Path
import random
import pandas as pd
from faker import Faker
fake = Faker(); random.seed(42); Faker.seed(42)
out = Path('sample_data'); (out/'reseller_exports').mkdir(parents=True, exist_ok=True)
rows = []
for i in range(1, 101):
    rows.append({
      'sale_id': i, 'sale_datetime': '2020-02-01 10:00:00', 'organizer_id': 1, 'reseller_id': 'R001', 'customer_id': i,
      'event_id': 1001, 'ticket_type_id': 5001, 'sold_by': 'RESELLER', 'sales_channel': random.choice(['WEB','MOBILE_APP','ONSITE']),
      'quantity': random.randint(1,5), 'unit_price': 150.00, 'gross_amount': 150.00, 'commission_rate': 10.00,
      'commission_amount': 15.00, 'net_amount': 135.00, 'currency': 'USD', 'updated_at': '2020-02-01 11:00:00'
    })
pd.DataFrame(rows).to_csv(out/'ticket_sale.csv', index=False)
pd.DataFrame([{
  'sale_date':'2020-02-01','reseller_id':'R001','reseller_name':'Northwind Tickets','reseller_region':'Europe','event_id':1001,
  'event_name':'Cloud Data Summit','event_type':'Conference','ticket_type_id':5001,'ticket_name':'VIP','sales_channel':'WEB',
  'quantity':2,'unit_price':150.00,'gross_amount':300.00,'commission_rate':10.00,'customer_email':'customer1@example.com','currency':'USD'
}]).to_csv(out/'reseller_exports'/'DailySales_02012020_R001.csv', index=False)
print('Sample data generated')
