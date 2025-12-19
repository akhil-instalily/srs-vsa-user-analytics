"""
Canonical filter model for all analytics endpoints.

All analytics functions and endpoints must accept this filter schema.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class AnalyticsFilters(BaseModel):
    """
    Canonical filter model for all analytics queries.

    Filters are applied at the SQL level, never post-filtered in Python.
    """

    # Required filters
    start_date: datetime = Field(
        ...,
        description="Start date for analytics time range (inclusive)"
    )

    end_date: datetime = Field(
        ...,
        description="End date for analytics time range (inclusive)"
    )

    product_context: Literal["pool", "landscape"] = Field(
        ...,
        description="Product context: 'pool' queries interaction_log, 'landscape' queries landscape_interaction_log"
    )

    # Optional filters
    environment: Optional[str] = Field(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    )

    user_id: Optional[str] = Field(
        None,
        description="Filter by specific user ID"
    )

    user_type: Literal["all", "internal", "external"] = Field(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )

    def get_table_name(self) -> str:
        """
        Get the correct table name based on product context.

        Returns:
            'interaction_log' for pool, 'landscape_interaction_log' for landscape
        """
        if self.product_context == "pool":
            return "interaction_log"
        elif self.product_context == "landscape":
            return "landscape_interaction_log"
        else:
            raise ValueError(f"Invalid product_context: {self.product_context}")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "product_context": "pool",
                "environment": "production",
                "user_id": "user123"
            }
        }
