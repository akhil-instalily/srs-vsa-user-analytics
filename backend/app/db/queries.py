"""
SQL query templates and builders for analytics.

All queries support product context routing:
- 'pool' → interaction_log
- 'landscape' → landscape_interaction_log

Filters are applied at the SQL level.
"""

from typing import Dict, Any, Optional, Tuple
from app.models.filters import AnalyticsFilters


def build_where_clause(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Build WHERE clause and parameters from AnalyticsFilters.

    Args:
        filters: Analytics filters

    Returns:
        Tuple of (where_clause_string, parameters_dict)
    """
    conditions = []
    params = {
        "start_date": filters.start_date,
        "end_date": filters.end_date,
    }

    # Date range filter (required)
    conditions.append("time_stamp >= %(start_date)s")
    conditions.append("time_stamp <= %(end_date)s")

    # Optional environment filter
    if filters.environment:
        conditions.append("environment = %(environment)s")
        params["environment"] = filters.environment

    # Optional user_id filter
    if filters.user_id:
        conditions.append("user_id = %(user_id)s")
        params["user_id"] = filters.user_id

    # Optional user_type filter (internal/external)
    if filters.user_type == "internal":
        conditions.append("user_id IN (SELECT user_id FROM internal_users)")
    elif filters.user_type == "external":
        conditions.append("user_id NOT IN (SELECT user_id FROM internal_users)")
    # If "all", no additional filter needed

    where_clause = " AND ".join(conditions)
    return where_clause, params


def get_base_query(
    filters: AnalyticsFilters,
    select_clause: str,
    additional_where: Optional[str] = None,
    group_by: Optional[str] = None,
    order_by: Optional[str] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Build a complete SQL query with product context routing.

    Args:
        filters: Analytics filters
        select_clause: SELECT clause (without 'SELECT' keyword)
        additional_where: Additional WHERE conditions
        group_by: GROUP BY clause (without 'GROUP BY' keyword)
        order_by: ORDER BY clause (without 'ORDER BY' keyword)

    Returns:
        Tuple of (query_string, parameters_dict)
    """
    table_name = filters.get_table_name()
    where_clause, params = build_where_clause(filters)

    # Add additional WHERE conditions
    if additional_where:
        where_clause = f"{where_clause} AND {additional_where}"

    # Build query
    query = f"SELECT {select_clause} FROM {table_name} WHERE {where_clause}"

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    return query, params


# ============================================
# Query templates for specific analytics
# ============================================

def session_metrics_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #1: Session Metrics (Time Range)
    - Total session count
    - Sessions with negative feedback
    - Sessions with positive feedback
    - Average session duration
    """
    select_clause = """
        COUNT(DISTINCT session_id) as total_sessions,
        COUNT(DISTINCT CASE WHEN user_feedback = '-1' THEN session_id END) as negative_feedback_sessions,
        COUNT(DISTINCT CASE WHEN user_feedback = '1' THEN session_id END) as positive_feedback_sessions,
        AVG(response_time) as avg_response_time
    """
    return get_base_query(filters, select_clause)


def volume_trends_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #3: Volume Trends (Time Range)
    - Sessions per day
    """
    select_clause = """
        DATE(time_stamp) as date,
        COUNT(DISTINCT session_id) as session_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="DATE(time_stamp)",
        order_by="date"
    )


def user_engagement_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #4: User Engagement (Time Range)
    - Unique users
    - Total conversations
    - Average conversations per user
    """
    select_clause = """
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT session_id) as total_conversations
    """
    return get_base_query(filters, select_clause)


def user_retention_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #5: User Retention (Time Range)
    - Returns user session counts for calculating retention
    """
    select_clause = """
        user_id,
        COUNT(DISTINCT session_id) as session_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="user_id"
    )


def query_categories_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #6: Query Categories (Time Range)
    - Session counts by query_category
    """
    select_clause = """
        query_category,
        COUNT(DISTINCT session_id) as session_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="query_category",
        order_by="session_count DESC"
    )


def returning_user_behavior_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #8: Returning User Behavior (Time Range)
    - User session counts and date ranges
    """
    select_clause = """
        user_id,
        COUNT(DISTINCT session_id) as session_count,
        MIN(DATE(time_stamp)) as first_chat_date,
        MAX(DATE(time_stamp)) as last_chat_date,
        MAX(DATE(time_stamp)) - MIN(DATE(time_stamp)) as active_days
    """
    return get_base_query(
        filters,
        select_clause,
        additional_where="user_id IS NOT NULL",
        group_by="user_id"
    )


def user_segmentation_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #9: User Segmentation (Time Range)
    - User session counts for segmentation
    """
    select_clause = """
        user_id,
        COUNT(DISTINCT session_id) as chat_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="user_id"
    )


def get_all_user_queries(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query to fetch all user queries for clustering (KPI #2).
    Returns all user inputs within the time range.
    """
    select_clause = """
        id,
        session_id,
        input as user_query
    """
    return get_base_query(
        filters,
        select_clause,
        additional_where="input IS NOT NULL AND input != ''",
        order_by="time_stamp"
    )


def time_patterns_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #10: Time Patterns
    - Hour of day distribution
    - Day of week distribution
    """
    select_clause = """
        EXTRACT(HOUR FROM time_stamp) as hour_of_day,
        EXTRACT(DOW FROM time_stamp) as day_of_week,
        COUNT(DISTINCT session_id) as session_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="EXTRACT(HOUR FROM time_stamp), EXTRACT(DOW FROM time_stamp)",
        order_by="hour_of_day, day_of_week"
    )


def conversation_length_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #11: Conversation Length
    - Messages per session
    """
    select_clause = """
        session_id,
        COUNT(*) as message_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="session_id"
    )


def platform_analytics_query(filters: AnalyticsFilters) -> Tuple[str, Dict[str, Any]]:
    """
    Query for KPI #12: Platform Analytics
    - Language, voice input, mobile usage
    """
    select_clause = """
        chat_language,
        is_voice_input,
        is_mobile_app,
        COUNT(DISTINCT session_id) as session_count,
        COUNT(DISTINCT user_id) as user_count
    """
    return get_base_query(
        filters,
        select_clause,
        group_by="chat_language, is_voice_input, is_mobile_app"
    )
