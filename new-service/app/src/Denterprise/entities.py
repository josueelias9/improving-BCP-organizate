from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    """Transaction entity representing a bank transaction"""
    fecha_proceso: Optional[str] = None
    fecha_valor: Optional[str] = None
    descripcion: Optional[str] = None
    cargos: float = 0.0
    abonos: float = 0.0
    transaccion_interna: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if transaction has meaningful data"""
        return (
            (self.descripcion and self.descripcion.strip()) or
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

    @property
    def has_transactions(self) -> bool:
        return len(self.transactions) > 0