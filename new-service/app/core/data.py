default_categories = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Food & Dining",
        "description": "Expenses related to food and beverages",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Transportation",
        "description": "Mobility and transportation expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "Entertainment",
        "description": "Leisure and entertainment expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "Alcohol & Bars",
        "description": "Expenses related to alcoholic beverages and bars",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "Health",
        "description": "Medical and health expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000006",
        "name": "Utilities",
        "description": "Basic services payments",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000007",
        "name": "Other",
        "description": "Uncategorized expenses",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000008",
        "name": "Dad",
        "description": "All transactions related to my dad",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000009",
        "name": "Pets",
        "description": "All transactions related to my pets",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000010",
        "name": "Family",
        "description": "All transactions related to my family",
        "parent_id": None,
    },
    {
        "id": "00000000-0000-0000-0000-000000000011",
        "name": "Investments",
        "description": "All transactions related to my investments",
        "parent_id": None,
    },
]


default_document_types = [
    {"id": "00000000-0000-0000-0000-000000000001", "name": "bcp_debit"},
    {"id": "00000000-0000-0000-0000-000000000002", "name": "bcp_credit"},
    {"id": "00000000-0000-0000-0000-000000000003", "name": "pichincha"},
    {"id": "00000000-0000-0000-0000-000000000004", "name": "yape"},
    {"id": "00000000-0000-0000-0000-000000000005", "name": "Scotiabank"},
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
        "account_id": "example-account-001",
    }
]

default_accounts = [
    {"id": "example-account-001"},
]

default_transactions = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "description": "Grocery Store",
        "amount": 50.0,
        "category_id": "00000000-0000-0000-0000-000000000003",
        "order": 1,
        "transaction_type": "expense",
        "account_id": "example-account-001",
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
        "account_id": "example-account-001",
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
        "account_id": "example-account-001",
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
        "account_id": "example-account-001",
        "currency": "SOL",
        "history": "This is something that happened fourth.",
        "unique_identifier": "example__unique__identifier__4",
    },
]


default_targets = [
    {
        "name": "Toyota",
        "price": 20000.0,
        "currency": "USD",
    },
    {
        "name": "Toyota",
        "price": 200000.0,
        "currency": "USD",
    },
    {
        "name": "Toyota",
        "price": 2000.0,
        "currency": "USD",
    },
    {
        "name": "Green Card",
        "price": 1000000.0,
        "currency": "USD",
    },
]
