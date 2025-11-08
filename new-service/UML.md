# Diagrama ERD - Sistema de Transacciones BCP

## Relación User - Transaction

```mermaid
erDiagram
    USER {
        _ document_number
        _ document_type
        _ first_name
        _ last_name
        _ email
        _ phone
        _ birth_date
        _ address
        _ city
        _ country
        _ created_at
        _ updated_at
        _ is_active
        _ customer_type
    }

    TRANSACTION {
        _ transaction_type
        _ amount
        _ currency
        _ description
        _ reference_number
        _ category
        _ subcategory
        _ merchant_name
        _ merchant_category
        _ transaction_date
        _ status
        _ payment_method
        _ account_number
        _ destination_account
        _ fee
        _ location
        _ metadata
        _ created_at
        _ updated_at
    }

    ACCOUNT {
        _ user_id
        _ account_number
        _ account_type
        _ currency
        _ balance
        _ available_balance
        _ is_active
        _ created_at
        _ updated_at
    }

    CATEGORY {
        _ name
        _ description
        _ color_code
        _ icon
        _ is_active
        _ created_at
    }

    TRANSACTION_CATEGORY {
        _ transaction_id
        _ category_id
        _ assigned_at
    }

    %% Relaciones
    USER ||--o{ TRANSACTION : "realiza"
    USER ||--o{ ACCOUNT : "posee"
    TRANSACTION }o--|| CATEGORY : "pertenece a"
    TRANSACTION ||--o| ACCOUNT : "origen"
    CATEGORY ||--o{ TRANSACTION_CATEGORY : "clasifica"
    TRANSACTION ||--o{ TRANSACTION_CATEGORY : "se clasifica en"
```
