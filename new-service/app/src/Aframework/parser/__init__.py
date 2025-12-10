"""
Parser module - Framework/Adapter Layer
Contains parsers that adapt external formats to domain entities
"""

from .bcp_statement_parser import BCPStatementParser

__all__ = ["BCPStatementParser"]
