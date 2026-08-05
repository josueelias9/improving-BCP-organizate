

## DB design

This is the design of the application and the database

- Document: the representation of a place that stores money

TODO:
- Transaction should have a connection to User? Remember that this app is intented to be used be just me. This relation doesnt make sense. And, in case we want to relate a transaction to a user, we can clearly do it thought a document. KEEP IT SIMPLE!
- add a new table "Account"
- a Document can have many transactions. A Document can have a single account
- The definition of Account here is "the representation of a place that has money". That is it.
- Following this, Document should be modified (remove balance). Adding hashing have more relevance with this approach

```mermaid
erDiagram
    USER {
        _ name
        _ is_active
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
        string id "this is generated with the hash of the content of the document"
        json data "all meaningfull data that can be extracted"
        bool processed
        _ time_range "not sure about this. It can be inferred from the first and last transaction date"
        _ plain_text
        float balance "net amount"
    }

    %% Relaciones
    USER ||--o{ DOCUMENT : "has"
    DOCUMENT ||--o{ TRANSACTION : "has"
    USER ||--o{ TRANSACTION : "realize"
    TRANSACTION }o--|| CATEGORY : "pertenece a"
    CATEGORY ||--o| CATEGORY : "may have"
    DOCUMENT_TYPE ||--o{ DOCUMENT : "has many"
```

