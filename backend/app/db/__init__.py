"""Database module for connection and query execution."""

from .client import db_client, get_db_client, DatabaseClient

__all__ = ["db_client", "get_db_client", "DatabaseClient"]
