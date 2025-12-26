"""
Analytics API endpoints.

All endpoints are GET-only and accept filters as query parameters.
"""

from datetime import datetime
from typing import Optional, Literal
from fastapi import APIRouter, Query, Depends
from app.models.filters import AnalyticsFilters
from app.auth import verify_jwt
from app.analytics.kpis import (
    compute_session_metrics,
    compute_pain_point_clustering,
    compute_volume_trends,
    compute_user_engagement,
    compute_user_retention,
    compute_query_categories,
    compute_returning_user_behavior,
    compute_user_segmentation,
    compute_time_patterns,
    compute_conversation_length,
    compute_platform_analytics,
    compute_sentiment_analysis_kpi,
)

router = APIRouter()


@router.get("/session-metrics")
def get_session_metrics(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #1: Session Metrics**

    Returns session-level metrics for the given time range:
    - Total session count
    - Number of sessions with negative feedback
    - Number of sessions with positive feedback
    - Average response time (seconds)

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_session_metrics(filters)


@router.get("/pain-point-clustering")
def get_pain_point_clustering(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #2: Pain Point Clustering**

    Clusters user queries into 5 predefined categories using LLM classification:
    - Cluster 0: General branch hours / orders / pool questions
    - Cluster 1: Pump recommendations – product discovery
    - Cluster 2: Replacement filter parts – maintenance needs
    - Cluster 3: Stock availability by part number – inventory checks
    - Cluster 4: DE filter assembly – technical support

    **Note:** This endpoint may take longer to respond due to LLM classification.
    Currently limited to first 100 queries to avoid timeouts.

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_pain_point_clustering(filters)


@router.get("/volume-trends")
def get_volume_trends(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #3: Volume Trends**

    Returns volume-related analytics:
    - Average sessions per day
    - Peak usage day (date + session count)
    - Lowest usage day (date + session count)
    - Daily session counts over the entire time range

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_volume_trends(filters)


@router.get("/user-engagement")
def get_user_engagement(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #4: User Engagement**

    Returns user engagement metrics:
    - Unique users
    - Total conversations
    - Average conversations per user

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_user_engagement(filters)


@router.get("/user-retention")
def get_user_retention(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #5: User Retention**

    Returns user retention metrics:
    - Total users
    - Returning users (2+ sessions)
    - One-time users (1 session)
    - Percentage breakdowns

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_user_retention(filters)


@router.get("/query-categories")
def get_query_categories(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #6: Query Categories**

    Returns session counts grouped by query_category:
    - Total sessions
    - Breakdown by category with counts and percentages

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_query_categories(filters)


@router.get("/returning-user-behavior")
def get_returning_user_behavior(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #8: Returning User Behavior**

    Analyzes behavior of returning users (users with 2+ sessions):
    - Count of returning users
    - Average sessions per returning user
    - Most active user and their session count
    - Average days between first and last chat
    - Longest active user span in days

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_returning_user_behavior(filters)


@router.get("/user-segmentation")
def get_user_segmentation(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #9: User Segmentation**

    Segments users by chat activity level:
    - Low activity: 1 chat
    - Medium activity: 2-5 chats
    - High activity: 6+ chats

    Returns user counts and percentages for each segment.

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_user_segmentation(filters)


@router.get("/time-patterns")
def get_time_patterns(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #10: Time Patterns**

    Analyzes usage patterns by time of day and day of week:
    - Hour of day distribution (0-23)
    - Day of week distribution (Sunday-Saturday)
    - Peak usage hour and day

    Useful for understanding when users are most active.

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_time_patterns(filters)


@router.get("/conversation-length")
def get_conversation_length(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #11: Conversation Length**

    Analyzes conversation depth by counting messages per session:
    - Average messages per session
    - Distribution by conversation length (short/medium/long)
    - Longest conversation in the time range

    Helps understand user engagement depth.

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_conversation_length(filters)


@router.get("/platform-analytics")
def get_platform_analytics(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #12: Platform Analytics**

    Analyzes user platform and input preferences:
    - Language distribution (English, Spanish, etc.)
    - Voice vs text input usage
    - Mobile app vs web usage

    Helps optimize platform support and accessibility features.

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_platform_analytics(filters)


@router.get("/sentiment-analysis")
def get_sentiment_analysis(
    _: dict = Depends(verify_jwt),
    start_date: datetime = Query(
        ...,
        description="Start date for analytics time range (ISO 8601 format)",
        example="2024-01-01T00:00:00"
    ),
    end_date: datetime = Query(
        ...,
        description="End date for analytics time range (ISO 8601 format)",
        example="2024-12-31T23:59:59"
    ),
    product_context: Literal["pool", "landscape"] = Query(
        ...,
        description="Product context: 'pool' for Heritage Pool Plus, 'landscape' for Heritage Plus"
    ),
    environment: Optional[str] = Query(
        None,
        description="Filter by environment (e.g., 'production', 'staging')"
    ),
    user_id: Optional[str] = Query(
        None,
        description="Filter by specific user ID"
    ),
    user_type: Literal["all", "internal", "external"] = Query(
        "all",
        description="Filter by user type: 'all' (default), 'internal' (users in internal_users table), or 'external' (users not in internal_users table)"
    )
):
    """
    **KPI #13: Sentiment Analysis**

    Analyzes sentiment of user messages using VADER (Valence Aware Dictionary and sEntiment Reasoner).
    VADER is a lexicon-based sentiment analysis tool - extremely fast, no LLM calls!

    Returns:
    - Total messages analyzed
    - Average sentiment score (-1 to 1)
    - Distribution by category (positive/neutral/negative)
    - Most positive message examples with scores
    - Most negative message examples with scores

    **Sentiment Scoring:**
    - Positive: compound score >= 0.05
    - Neutral: compound score between -0.05 and 0.05
    - Negative: compound score <= -0.05

    **Product Context:**
    - `pool` → queries Heritage Pool Plus data (interaction_log)
    - `landscape` → queries Heritage Plus data (landscape_interaction_log)
    """
    filters = AnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        product_context=product_context,
        environment=environment,
        user_id=user_id,
        user_type=user_type
    )

    return compute_sentiment_analysis_kpi(filters)
