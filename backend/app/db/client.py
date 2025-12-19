"""
Database client for PostgreSQL connection and query execution.

Supports both:
- TCP connection (local development)
- Unix socket connection (Google Cloud Run with Cloud SQL)
"""

import os
import psycopg2
from psycopg2 import pool
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseClient:
    """PostgreSQL database client with connection pooling."""

    def __init__(self):
        self.connection_pool: Optional[pool.SimpleConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool with Cloud Run support."""

        # Check if running on Cloud Run with Cloud SQL
        cloud_sql_connection = os.getenv("CLOUD_SQL_CONNECTION_NAME")

        if cloud_sql_connection:
            # Cloud Run: Use Unix socket
            connection_params = {
                "host": f"/cloudsql/{cloud_sql_connection}",
                "dbname": os.getenv("POSTGRES_NAME"),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASS"),
            }
        else:
            # Local: Use TCP connection
            connection_params = {
                "host": os.getenv("POSTGRES_HOST"),
                "port": os.getenv("POSTGRES_PORT", "5432"),
                "dbname": os.getenv("POSTGRES_NAME"),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASS"),
            }

        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **connection_params
            )
            print("✓ Database connection pool initialized successfully")
        except Exception as e:
            print(f"✗ Failed to initialize database connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool."""
        if self.connection_pool:
            return self.connection_pool.getconn()
        raise Exception("Connection pool not initialized")

    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries.

        Args:
            query: SQL query string
            params: Query parameters (optional)
            fetch_one: If True, return only the first row

        Returns:
            List of dictionaries representing rows
        """
        conn = None
        cursor = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Execute query
            cursor.execute(query, params or ())

            # Fetch results
            if fetch_one:
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row))]
                return []
            else:
                rows = cursor.fetchall()
                if rows:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                return []

        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            raise

        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and verify both tables exist.

        Returns:
            Dict with connection status and table info
        """
        try:
            # Test basic query
            result = self.execute_query("SELECT version();", fetch_one=True)
            pg_version = result[0]["version"] if result else "Unknown"

            # Check interaction_log table
            pool_count = self.execute_query(
                "SELECT COUNT(*) as count FROM interaction_log;",
                fetch_one=True
            )

            # Check landscape_interaction_log table
            landscape_count = self.execute_query(
                "SELECT COUNT(*) as count FROM landscape_interaction_log;",
                fetch_one=True
            )

            return {
                "status": "connected",
                "postgres_version": pg_version,
                "tables": {
                    "interaction_log": {
                        "exists": True,
                        "row_count": pool_count[0]["count"] if pool_count else 0
                    },
                    "landscape_interaction_log": {
                        "exists": True,
                        "row_count": landscape_count[0]["count"] if landscape_count else 0
                    }
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def close(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ Database connection pool closed")


# Global database client instance
db_client = DatabaseClient()


def get_db_client() -> DatabaseClient:
    """Get the global database client instance."""
    return db_client
