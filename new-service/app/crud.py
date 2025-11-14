"""
CRUD operations - Main entry point
Re-exports all CRUD functions from infrastructure layer
"""

from app.src.Ainfrastructure.database.crud.user import (
    create_user,
    get_user,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
    user_exists
)

from app.src.Ainfrastructure.database.crud.document import (
    create_document,
    get_document,
    get_documents_by_user,
    get_document_by_filename,
    get_documents_by_type,
    get_all_documents,
    update_document,
    delete_document
)

from app.src.Ainfrastructure.database.crud.transaction import (
    create_transaction,
    create_transactions_bulk,
    get_transaction,
    get_transactions_by_user,
    get_transactions_by_document,
    get_transactions_by_category,
    update_transaction,
    delete_transaction,
    get_transaction_by_name
)

from app.src.Ainfrastructure.database.crud.category import (
    create_category,
    get_category,
    get_category_by_name,
    get_all_categories,
    get_categories_by_parent,
    get_root_categories,
    update_category,
    delete_category,
    category_exists
)

__all__ = [
    # User
    "create_user",
    "get_user",
    "get_user_by_email",
    "get_all_users",
    "update_user",
    "delete_user",
    "user_exists",
    # Document
    "create_document",
    "get_document",
    "get_documents_by_user",
    "get_document_by_filename",
    "get_documents_by_type",
    "get_all_documents",
    "update_document",
    "delete_document",
    # Transaction
    "create_transaction",
    "create_transactions_bulk",
    "get_transaction",
    "get_transactions_by_user",
    "get_transactions_by_document",
    "get_transactions_by_category",
    "update_transaction",
    "delete_transaction",
    "get_transaction_by_name",
    # Category
    "create_category",
    "get_category",
    "get_category_by_name",
    "get_all_categories",
    "get_categories_by_parent",
    "get_root_categories",
    "update_category",
    "delete_category",
    "category_exists",
]
