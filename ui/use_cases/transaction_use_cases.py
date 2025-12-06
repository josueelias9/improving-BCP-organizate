"""
Use Cases - Application business logic
"""
from typing import List, Optional
import pandas as pd
from domain.entities import Transaction
from domain.repositories import TransactionRepository, CategoryRepository


class GetTransactionsUseCase:
    """Get all transactions with processing"""
    
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo
    
    def execute(self) -> pd.DataFrame:
        """Execute use case"""
        transactions = self.transaction_repo.get_all()
        
        if not transactions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = [vars(t) for t in transactions]
        df = pd.DataFrame(data)
        
        # Parse dates
        if 'fecha_proceso' in df.columns:
            df['fecha_proceso'] = pd.to_datetime(df['fecha_proceso'], format='%d/%m/%Y', errors='coerce')
        if 'fecha_consumo' in df.columns:
            df['fecha_consumo'] = pd.to_datetime(df['fecha_consumo'], format='%d/%m/%Y', errors='coerce')
        
        # Add month for filtering
        if 'fecha_proceso' in df.columns:
            df['month'] = df['fecha_proceso'].dt.to_period('M')
        
        # Sort by order
        if 'order' in df.columns:
            df = df.sort_values('order', ascending=True)
        
        return df


class UpdateTransactionUseCase:
    """Update a single transaction"""
    
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo
    
    def execute(self, transaction_id: str, history: Optional[str], category_name: Optional[str]) -> dict:
        """Execute use case"""
        return self.transaction_repo.update(transaction_id, history, category_name)


class BatchUpdateTransactionsUseCase:
    """Update multiple transactions"""
    
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo
    
    def execute(self, updates: List[dict]) -> dict:
        """Execute use case"""
        return self.transaction_repo.batch_update(updates)


class GetCategoriesUseCase:
    """Get all categories"""
    
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo
    
    def execute(self) -> List[dict]:
        """Execute use case"""
        categories = self.category_repo.get_all()
        return [{'name': c.name, 'description': c.description, 'id': c.id} for c in categories]
