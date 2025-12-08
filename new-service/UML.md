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
        _ history
        _ income
        _ outcome
        _ currency
        _ date
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
        _ currency
        json data
    }


    %% Relaciones
    USER ||--o{ DOCUMENT : "has"
    DOCUMENT ||--o{ TRANSACTION : "has"
    USER ||--o{ TRANSACTION : "realiza"
    TRANSACTION }o--|| CATEGORY : "pertenece a"
    CATEGORY ||--o| CATEGORY : "may have"
    DOCUMENT_TYPE ||--o{ DOCUMENT : "has many"
```
