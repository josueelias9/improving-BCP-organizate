"""
API Client for BCP Transaction Manager
Handles all communication with the FastAPI backend
"""
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BCPApiClient:
    """Client for communicating with BCP PDF Extractor API"""
    
    def __init__(self, base_url: str = "http://new-service:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the API (default: http://new-service:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_all_transactions(self, skip: int = 0, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all transactions from API
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            requests.HTTPError: If API request fails
        """
        try:
            url = f"{self.base_url}/api/transactions/"
            params = {"skip": skip, "limit": limit}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            transactions = response.json()
            logger.info(f"Retrieved {len(transactions)} transactions from API")
            return transactions
            
        except requests.RequestException as e:
            logger.error(f"Error fetching transactions: {str(e)}")
            raise
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories from API
        
        Returns:
            List of category dictionaries
            
        Raises:
            requests.HTTPError: If API request fails
        """
        try:
            url = f"{self.base_url}/api/categories/"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            categories = response.json()
            logger.info(f"Retrieved {len(categories)} categories from API")
            return categories
            
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise
    
    def update_transaction(
        self, 
        transaction_id: str, 
        history: Optional[str] = None,
        category_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a single transaction
        
        Args:
            transaction_id: UUID of the transaction
            history: New history text (optional)
            category_name: New category name (optional)
            
        Returns:
            Update result dictionary
            
        Raises:
            requests.HTTPError: If API request fails
        """
        try:
            url = f"{self.base_url}/api/transactions/{transaction_id}"
            
            # Build update payload
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
            logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
            raise
    
    def batch_update_transactions(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update multiple transactions at once
        
        Args:
            updates: List of update dictionaries with transaction_id, history, category_name
            
        Returns:
            Batch update result dictionary
            
        Raises:
            requests.HTTPError: If API request fails
        """
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
        """
        Check if API is reachable
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/api"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
