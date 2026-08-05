default_categories = [
    # ================================== Food & Dining
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Food & Dining",
        "description": "Expenses related to food and beverages",
        "parent_id": None,
    },
    # ================================== Transportation
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Transportation",
        "description": "Mobility and transportation expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "Fuel",
        "description": "Gasoline and fuel",
        "parent_id": "00000000-0000-0000-0000-000000000002",
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "Taxi/Uber",
        "description": "Transportation services",
        "parent_id": "00000000-0000-0000-0000-000000000002",
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "Public Transport",
        "description": "Bus, metro, train",
        "parent_id": "00000000-0000-0000-0000-000000000002",
    },
    # ================================== Entertainment
    {
        "id": "00000000-0000-0000-0000-000000000006",
        "name": "Entertainment",
        "description": "Leisure and entertainment expenses",
        "parent_id": None,
    },
    # ================================== Health
    {
        "id": "00000000-0000-0000-0000-000000000007",
        "name": "Health",
        "description": "Medical and health expenses",
        "parent_id": None,
    },
    # ================================== Utilities
    {
        "id": "00000000-0000-0000-0000-000000000008",
        "name": "Utilities",
        "description": "Basic services payments",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000009",
        "name": "Electricity",
        "description": "Electric bill",
        "parent_id": "00000000-0000-0000-0000-000000000008",
    },
    {
        "id": "00000000-0000-0000-0000-000000000010",
        "name": "Water",
        "description": "Water bill",
        "parent_id": "00000000-0000-0000-0000-000000000008",
    },
    {
        "id": "00000000-0000-0000-0000-000000000011",
        "name": "Internet",
        "description": "Internet service",
        "parent_id": "00000000-0000-0000-0000-000000000008",
    },
    {
        "id": "00000000-0000-0000-0000-000000000012",
        "name": "Phone",
        "description": "Phone services",
        "parent_id": "00000000-0000-0000-0000-000000000008",
    },
    # ================================== Other
    {
        "id": "00000000-0000-0000-0000-000000000013",
        "name": "Other",
        "description": "Uncategorized expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000014",
        "name": "Dad",
        "description": "All transactions related to my dad",
        "parent_id": None,
    },
]


default_document_types = [
    {"id": "00000000-0000-0000-0000-000000000001", "name": "bcp_debit"},
    {"id": "00000000-0000-0000-0000-000000000002", "name": "bcp_credit"},
    {"id": "00000000-0000-0000-0000-000000000003", "name": "pichincha"},
    {"id": "00000000-0000-0000-0000-000000000004", "name": "yape"},
    {"id": "00000000-0000-0000-0000-000000000005", "name": "Interbank"},
    {"id": "00000000-0000-0000-0000-000000000006", "name": "Payoneer"},
    {"id": "00000000-0000-0000-0000-000000000007", "name": "local"},
]


default_users = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "admin@bcpextractor.com",
        "name": "Administrator",
        "is_active": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "email": "test@bcpextractor.com",
        "name": "Test User",
        "is_active": True,
    },
]


default_documents = [
    {
        "id": "0000000000000000000000000000000000000000000000000000000000000000",
        "processed": True,
        "document_type_id": "00000000-0000-0000-0000-000000000001",
        "user_id": "00000000-0000-0000-0000-000000000001",
        "data": {
            "information": "Data here is dynamic. It depends on the PDF content and the parser used."
        },
    }
]

default_transactions = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "description": "Grocery Store",
        "amount": 50.0,
        "category_id": "00000000-0000-0000-0000-000000000003",
        "order": 1,
        "transaction_type": "expense",
        "document_id": "0000000000000000000000000000000000000000000000000000000000000000",
        "currency": "SOL",
        "history": "This is something that happened first.",
        "unique_identifier": "example__unique__identifier__1",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "description": "Restaurant",
        "amount": 30.0,
        "category_id": "00000000-0000-0000-0000-000000000002",
        "order": 2,
        "transaction_type": "expense",
        "document_id": "0000000000000000000000000000000000000000000000000000000000000000",
        "currency": "SOL",
        "history": "This is something that happened second.",
        "unique_identifier": "example__unique__identifier__2",
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "description": "Gas Station",
        "amount": 40.0,
        "category_id": "00000000-0000-0000-0000-000000000006",
        "order": 3,
        "transaction_type": "expense",
        "document_id": "0000000000000000000000000000000000000000000000000000000000000000",
        "currency": "SOL",
        "history": "This is something that happened third.",
        "unique_identifier": "example__unique__identifier__3",
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "description": "Movie Theater",
        "amount": 15.5,
        "category_id": "00000000-0000-0000-0000-000000000006",
        "order": 4,
        "transaction_type": "expense",
        "document_id": "0000000000000000000000000000000000000000000000000000000000000000",
        "currency": "SOL",
        "history": "This is something that happened fourth.",
        "unique_identifier": "example__unique__identifier__4",
    },
]
