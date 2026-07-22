# ERD
```mermaid
erDiagram
ORGANIZER ||--o{ EVENT : owns
VENUE ||--o{ EVENT : hosts
EVENT ||--o{ TICKET_TYPE : has
RESELLER ||--o{ TICKET_SALE : sells
CUSTOMER ||--o{ TICKET_SALE : buys
EVENT ||--o{ TICKET_SALE : sold_for
```
