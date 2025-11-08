from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Transaction:
    """Transaction entity representing a bank transaction"""
    fecha_proceso: Optional[str] = None
    fecha_consumo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_operacion: Optional[str] = None
    soles: float = 0.0
    dolares: float = 0.0

    def is_valid(self) -> bool:
        """Check if transaction has meaningful data"""
        return (
            (self.descripcion and self.descripcion.strip()) or
            self.soles != 0.0 or
            self.dolares != 0.0
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

    @property
    def has_transactions(self) -> bool:
        return len(self.transactions) > 0