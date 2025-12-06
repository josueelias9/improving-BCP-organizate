"""
API Implementation of Transaction Repository
"""
import requests
from typing import List, Optional
import logging
from domain.entities import Transaction
from domain.repositories import TransactionRepository

logger = logging.getLogger(__name__)


class ApiTransactionRepository(TransactionRepository):
    """Transaction repository using API"""
    
    def __init__(self, base_url: str = "http://new-service:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_all(self, skip: int = 0, limit: int = 1000) -> List[Transaction]:
        """Get all transactions from API"""
        try:
            url = f"{self.base_url}/api/transactions/"
            params = {"skip": skip, "limit": limit}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            transactions = [Transaction(**item) for item in data]
            
            logger.info(f"Retrieved {len(transactions)} transactions")
            return transactions
            
        except requests.RequestException as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise
    
    def update(self, transaction_id: str, history: Optional[str], category_name: Optional[str]) -> dict:
        """Update a transaction"""
        try:
            url = f"{self.base_url}/api/transactions/{transaction_id}"
            
            payload = {}
            if history is not None:
                payload["history"] = history
            if category_name is not None:
                payload["category_name"] = category_name
            
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Updated transaction {transaction_id}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error updating transaction: {str(e)}")
            raise
    
    def batch_update(self, updates: List[dict]) -> dict:
        """Update multiple transactions"""
        try:
            url = f"{self.base_url}/api/transactions/batch"
            payload = {"updates": updates}
            
            response = self.session.patch(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Batch updated {result.get('updated', 0)} transactions")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error in batch update: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            url = f"{self.base_url}/api"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
