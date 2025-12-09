from datetime import date
from typing import Optional, Dict, Any
from enum import Enum


# Enums
class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==============================================


class DocumentTypeEntity():
    def __init__(self,name):
        self.name = name

class UserEntity():
    def __init__(self,
                 

email,
name,
is_active,
customer_type,
                 
                 ):
        self.email = email
        self.name = name
        self.is_active = is_active
        self.customer_type = customer_type

class TransactionEntity():
    def __init__(self,
order,
description,
history,
amount,
transaction_type,
transaction_date,
unique_identifier,):

        self.order = order
        self.description = description
        self.history = history
        self.amount = amount
        self.transaction_type = transaction_type
        self.transaction_date = transaction_date
        self.unique_identifier = unique_identifier


class CategoryEntity():
    def __init__(self,name,
                 description):
        self.name = name
        self.description = description


class DocumentEntity():
    def __init__(self,
                 
                 
data,
currency,
unique_identifier,
processed):
                 
                 
                 
        
        self.data = data
        self.currency = currency
        self.unique_identifier = unique_identifier
        self.processed = processed
