"""
Domain Entities - Core business objects
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Transaction:
    """Transaction entity"""
    id: str
    order: int
    description: str
    cargos: float
    abonos: float
    fecha_proceso: str
    currency: Optional[str] = None
    fecha_consumo: Optional[str] = None
    internal_transaction: Optional[bool] = None
    category_name: Optional[str] = None
    history: Optional[str] = None
    document_id: Optional[str] = None
    category_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    unique_identifier: Optional[str] = None
    amount: float = 0.0
    
    def __post_init__(self):
        """Calculate amount after initialization"""
        self.amount = self.abonos - self.cargos


@dataclass
class Category:
    """Category entity"""
    name: str
    description: Optional[str] = None
    id: Optional[str] = None
    parent_id: Optional[str] = None
