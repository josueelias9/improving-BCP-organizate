"""
API Implementation of Category Repository
"""
import requests
from typing import List
import logging
from domain.entities import Category
from domain.repositories import CategoryRepository

logger = logging.getLogger(__name__)


class ApiCategoryRepository(CategoryRepository):
    """Category repository using API"""
    
    def __init__(self, base_url: str = "http://new-service:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_all(self) -> List[Category]:
        """Get all categories from API"""
        try:
            url = f"{self.base_url}/api/categories/"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            categories = [Category(**item) for item in data]
            
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
            
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise
