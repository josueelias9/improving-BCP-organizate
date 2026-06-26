default_categories = [
    {
        "name": "Food & Dining",
        "description": "Expenses related to food and beverages",
        "children": [
            {"name": "Restaurants", "description": "Dining at restaurants"},
            {"name": "Groceries", "description": "Food shopping"},
            {"name": "Delivery", "description": "Home delivery orders"},
        ],
    },
    {
        "name": "Transportation",
        "description": "Mobility and transportation expenses",
        "children": [
            {"name": "Fuel", "description": "Gasoline and fuel"},
            {"name": "Taxi/Uber", "description": "Transportation services"},
            {"name": "Public Transport", "description": "Bus, metro, train"},
        ],
    },
    {
        "name": "Entertainment",
        "description": "Leisure and entertainment expenses",
        "children": [
            {"name": "Movies", "description": "Movie tickets"},
            {"name": "Streaming", "description": "Netflix, Spotify, etc."},
            {"name": "Games", "description": "Video games and entertainment"},
        ],
    },
    {
        "name": "Health",
        "description": "Medical and health expenses",
        "children": [
            {"name": "Pharmacy", "description": "Medications"},
            {"name": "Medical Visits", "description": "Medical consultations"},
            {"name": "Insurance", "description": "Health insurance"},
        ],
    },
    {
        "name": "Utilities",
        "description": "Basic services payments",
        "children": [
            {"name": "Electricity", "description": "Electric bill"},
            {"name": "Water", "description": "Water bill"},
            {"name": "Internet", "description": "Internet service"},
            {"name": "Phone", "description": "Phone services"},
        ],
    },
    {"name": "Other", "description": "Uncategorized expenses", "children": []},
]


default_document_types = [
    {"name": "bcp_debit"},
    {"name": "bcp_credit"},
    {"name": "pichincha"},
]


default_users = [
    {
        "email": "admin@bcpextractor.com",
        "name": "Administrator",
        "is_active": True,
    },
    {
        "email": "test@bcpextractor.com",
        "name": "Test User",
        "is_active": True,
    },
]


default_documents = [
    {
        "processed": True,
        "unique_identifier": "bcp_debit_2023-01-01_2023-01-31",
        "document_type": "bcp_debit",
        "user": "admin@bcpextractor.com",
    }
]

default_transactions = [
    {
        "description": "Grocery Store",
        "amount": 50.0,
        "category": "Groceries",
        "order": 1,
        "transaction_type": "expense",
        "document": "bcp_debit_2023-01-01_2023-01-31",
    },
    {
        "description": "Restaurant",
        "amount": 30.0,
        "category": "Restaurants",
        "order": 2,
        "transaction_type": "expense",
        "document": "bcp_debit_2023-01-01_2023-01-31",
    },
    {
        "description": "Gas Station",
        "amount": 40.0,
        "category": "Fuel",
        "order": 3,
        "transaction_type": "expense",
        "document": "bcp_debit_2023-01-01_2023-01-31",
    },
    {
        "description": "Movie Theater",
        "amount": 15.5,
        "category": "Movies",
        "order": 4,
        "transaction_type": "expense",
        "document": "bcp_debit_2023-01-01_2023-01-31",
    },
]
