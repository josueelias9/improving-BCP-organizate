

## DB design

This is the design of the application and the database

- Document: the representation of a place that stores money

TODO:
- Transaction should have a connection to User? Remember that this app is intented to be used be just me. This relation doesnt make sense. And, in case we want to relate a transaction to a user, we can clearly do it thought a document. KEEP IT SIMPLE!
- add a new table "Account"
- a Document can have many transactions. A Document can have a single account
- The definition of Account here is "the representation of a place that has money". That is it.
- Following this, Document should be modified (remove balance). Adding hashing have more relevance with this approach


entity definitions:
- DOCUMENT: the representation of a file
- ACCOUNT: a place where money goes in and out
- HISTORY: a registry of the amount of time of an account in a specific time

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

    HISTORY {
        date time "when it was registered"
        float balance "net amount"
    }

    CATEGORY {
        _ name
        _ description
        _ subcategory
    }

    DOCUMENT_FORMAT {
        _ name
    }


    ACCOUNT {        
        _ id PK "extracted from document's plain text. If no one is present, use the doc format"
    }

    DOCUMENT {
        string id PK "this is generated with the hash of the content of the document"
        bool processed "true if transactions were extracted from this document"
        string plain_text
    }

    %% Relaciones
    USER ||--o{ DOCUMENT : "has"
    ACCOUNT ||--o{ TRANSACTION : "could have"
    TRANSACTION }o--|| CATEGORY : "pertenece a"
    CATEGORY ||--o| CATEGORY : "may have"
    DOCUMENT_FORMAT ||--o{ DOCUMENT : "has many"
    DOCUMENT }|--o| ACCOUNT : "could have"
    ACCOUNT ||--o{ HISTORY : "could have"
    
```

