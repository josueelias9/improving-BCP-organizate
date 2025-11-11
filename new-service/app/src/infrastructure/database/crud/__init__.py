"""
Database CRUD operations - Main entry point
"""

from .user import (
    create_user,
    get_user,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
    user_exists
)

from .document import (
    create_document,
    get_document,
    get_documents_by_user,
    get_document_by_filename,
    get_documents_by_type,
    get_all_documents,
    update_document,
    delete_document
)

from .transaction import (
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

from .category import (
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
    # User CRUD
    "create_user",
    "get_user", 
    "get_user_by_email",
    "get_all_users",
    "update_user",
    "delete_user",
    "user_exists",
    
    # Document CRUD
    "create_document",
    "get_document",
    "get_documents_by_user",
    "get_document_by_filename", 
    "get_documents_by_type",
    "get_all_documents",
    "update_document",
    "delete_document",
    
    # Transaction CRUD
    "create_transaction",
    "create_transactions_bulk",
    "get_transaction",
    "get_transactions_by_user",
    "get_transactions_by_document",
    "get_transactions_by_category", 
    "update_transaction",
    "delete_transaction",
    "get_transaction_by_name",
    
    # Category CRUD
    "create_category",
    "get_category",
    "get_category_by_name",
    "get_all_categories",
    "get_categories_by_parent",
    "get_root_categories",
    "update_category",
    "delete_category",
    "category_exists"
]