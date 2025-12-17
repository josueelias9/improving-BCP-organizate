# Diagrama ERD - Sistema de Transacciones BCP

## Relación User - Transaction

```mermaid
erDiagram
    USER {
        _ name
        _ is_active
        _ customer_type
    }

    TRANSACTION {
        _ description
        _ amount
        _ transaction_type
        _ date
        _ currency
        _ unique_identifier 
        _ history
        _ order
    }

    CATEGORY {
        _ name
        _ description
        _ subcategory
    }

    DOCUMENT_TYPE {
        _ name
    }



    DOCUMENT {
        json data
        _ unique_identifier
        bool processed
        _ time_range
        _ plain_text
    }


    %% Relaciones
    USER ||--o{ DOCUMENT : "has"
    DOCUMENT ||--o{ TRANSACTION : "has"
    USER ||--o{ TRANSACTION : "realiza"
    TRANSACTION }o--|| CATEGORY : "pertenece a"
    CATEGORY ||--o| CATEGORY : "may have"
    DOCUMENT_TYPE ||--o{ DOCUMENT : "has many"
```
