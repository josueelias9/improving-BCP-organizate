"""
Entity DTOs - Domain Entities as Data Transfer Objects
Used for transferring entity data between layers
"""
from datetime import date
from typing import Optional
from dataclasses import dataclass


@dataclass
class DTOTransaction:
    """Transaction entity representing a bank transaction"""
    fecha_proceso: Optional[date] = None
    fecha_valor: Optional[date] = None
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
    
    def to_transaction_type_and_amount(self) -> tuple[str, float]:
        """Convert cargos/abonos to type and amount"""
        if self.cargos == 0.0:
            return ("income", self.abonos)
        else:
            return ("expense", self.cargos)


@dataclass
class DTOExtractionResult:
    """Result of PDF extraction operation"""
    filename: str
    transactions: list[DTOTransaction]
    total_transactions: int
    success: bool
    error_message: Optional[str] = None
    extracted_text: Optional[str] = None
    account_code: Optional[str] = None
    currency: Optional[str] = None  # 'PEN' or 'USD'
    saldo_anterior: Optional[float] = None
    initial_day: Optional[date] = None
    final_day: Optional[date] = None
