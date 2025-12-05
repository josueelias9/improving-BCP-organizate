"""
Entity DTOs - Domain Entities as Data Transfer Objects
Used for transferring entity data between layers
"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Transaction entity representing a bank transaction"""
    fecha_proceso: Optional[str] = None
    fecha_valor: Optional[str] = None
    description: Optional[str] = None
    cargos: float = 0.0
    abonos: float = 0.0
    internal_transaction: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if transaction has meaningful data"""
        return (
            (self.description and self.description.strip()) or
            self.cargos != 0.0 or
            self.abonos != 0.0
        )


@dataclass
class ExtractionResult:
    """Result of PDF extraction operation"""
    filename: str
    transactions: list[Transaction]
    total_transactions: int
    success: bool
    error_message: Optional[str] = None
    extracted_text: Optional[str] = None
    account_code: Optional[str] = None
    currency: Optional[str] = None  # 'PEN' or 'USD'
    saldo_anterior: Optional[float] = None
    initial_day: Optional[str] = None
    final_day: Optional[str] = None
