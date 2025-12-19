"""
KPI computation functions.

Each function:
- Accepts AnalyticsFilters
- Executes SQL via db_client
- Returns structured JSON (frontend-ready)
"""

from typing import Dict, Any
from app.models.filters import AnalyticsFilters
from app.db import get_db_client
from app.db.queries import (
    session_metrics_query,
    volume_trends_query,
    user_engagement_query,
    user_retention_query,
    query_categories_query,
    returning_user_behavior_query,
    user_segmentation_query,
    get_all_user_queries,
    time_patterns_query,
    conversation_length_query,
    platform_analytics_query,
)
from app.analytics.clustering import cluster_queries
from app.analytics.sentiment import compute_sentiment_analysis


def compute_session_metrics(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #1: Session Metrics (Time Range)

    Returns:
        - total_sessions: Total session count
        - negative_feedback_sessions: Sessions with negative feedback
        - positive_feedback_sessions: Sessions with positive feedback
        - avg_response_time: Average response time in seconds
    """
    db = get_db_client()
    query, params = session_metrics_query(filters)

    result = db.execute_query(query, params, fetch_one=True)

    if not result:
        return {
            "total_sessions": 0,
            "negative_feedback_sessions": 0,
            "positive_feedback_sessions": 0,
            "avg_response_time": 0.0
        }

    data = result[0]

    return {
        "total_sessions": data.get("total_sessions", 0),
        "negative_feedback_sessions": data.get("negative_feedback_sessions", 0),
        "positive_feedback_sessions": data.get("positive_feedback_sessions", 0),
        "avg_response_time": round(float(data.get("avg_response_time", 0) or 0), 2),
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_pain_point_clustering(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #2: Pain Point Clustering (Time Range)

    Clusters all user queries into 5 predefined categories using LLM classification.

    Returns:
        - total_queries: Total number of queries analyzed
        - clusters: List of cluster objects with:
            - cluster_id: 0-4
            - cluster_name: Cluster description
            - count: Number of queries in this cluster
            - percentage: Percentage of total queries
            - example_queries: Sample queries from this cluster
    """
    db = get_db_client()
    query, params = get_all_user_queries(filters)

    # Fetch all user queries from the time range
    queries_data = db.execute_query(query, params)

    # Cluster using LLM
    clustering_result = cluster_queries(queries_data, max_examples_per_cluster=5)

    # Add filter info
    clustering_result["filters_applied"] = {
        "start_date": filters.start_date.isoformat(),
        "end_date": filters.end_date.isoformat(),
        "product_context": filters.product_context,
        "environment": filters.environment,
        "user_id": filters.user_id,
    }

    return clustering_result


def compute_volume_trends(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #3: Volume Trends (Time Range)

    Computes volume-related metrics:
    - Average sessions per day
    - Peak usage day (date + count)
    - Lowest usage day (date + count)

    Returns:
        - avg_sessions_per_day: Average number of sessions per day
        - peak_day: Date with highest session count
        - peak_day_sessions: Number of sessions on peak day
        - lowest_day: Date with lowest session count
        - lowest_day_sessions: Number of sessions on lowest day
        - daily_data: List of daily session counts
    """
    db = get_db_client()
    query, params = volume_trends_query(filters)

    # Fetch daily session counts
    daily_data = db.execute_query(query, params)

    if not daily_data:
        return {
            "avg_sessions_per_day": 0,
            "peak_day": None,
            "peak_day_sessions": 0,
            "lowest_day": None,
            "lowest_day_sessions": 0,
            "daily_data": [],
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Calculate metrics
    total_sessions = sum(row["session_count"] for row in daily_data)
    num_days = len(daily_data)
    avg_sessions = round(total_sessions / num_days, 2) if num_days > 0 else 0

    # Find peak and lowest days
    peak_day_data = max(daily_data, key=lambda x: x["session_count"])
    lowest_day_data = min(daily_data, key=lambda x: x["session_count"])

    return {
        "avg_sessions_per_day": avg_sessions,
        "peak_day": peak_day_data["date"].isoformat() if peak_day_data["date"] else None,
        "peak_day_sessions": peak_day_data["session_count"],
        "lowest_day": lowest_day_data["date"].isoformat() if lowest_day_data["date"] else None,
        "lowest_day_sessions": lowest_day_data["session_count"],
        "total_days": num_days,
        "total_sessions": total_sessions,
        "daily_data": [
            {
                "date": row["date"].isoformat() if row["date"] else None,
                "session_count": row["session_count"]
            }
            for row in daily_data
        ],
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_user_engagement(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #4: User Engagement (Time Range)

    Computes user engagement metrics:
    - Unique users
    - Total conversations
    - Average conversations per user

    Returns:
        - unique_users: Number of unique users
        - total_conversations: Total number of conversations/sessions
        - avg_conversations_per_user: Average conversations per user
    """
    db = get_db_client()
    query, params = user_engagement_query(filters)

    result = db.execute_query(query, params, fetch_one=True)

    if not result:
        return {
            "unique_users": 0,
            "total_conversations": 0,
            "avg_conversations_per_user": 0.0,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    data = result[0]
    unique_users = data.get("unique_users", 0)
    total_conversations = data.get("total_conversations", 0)

    avg_conversations = round(
        total_conversations / unique_users, 2
    ) if unique_users > 0 else 0.0

    return {
        "unique_users": unique_users,
        "total_conversations": total_conversations,
        "avg_conversations_per_user": avg_conversations,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_user_retention(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #5: User Retention (Time Range)

    Computes user retention metrics:
    - % returning users (users with 2+ sessions)
    - % one-time users (users with 1 session)

    Returns:
        - total_users: Total unique users
        - returning_users: Users with 2+ sessions
        - one_time_users: Users with 1 session
        - returning_users_percentage: % of returning users
        - one_time_users_percentage: % of one-time users
    """
    db = get_db_client()
    query, params = user_retention_query(filters)

    # Get user session counts
    user_data = db.execute_query(query, params)

    if not user_data:
        return {
            "total_users": 0,
            "returning_users": 0,
            "one_time_users": 0,
            "returning_users_percentage": 0.0,
            "one_time_users_percentage": 0.0,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Categorize users
    total_users = len(user_data)
    one_time_users = sum(1 for user in user_data if user["session_count"] == 1)
    returning_users = total_users - one_time_users

    # Calculate percentages
    returning_pct = round((returning_users / total_users) * 100, 2) if total_users > 0 else 0.0
    one_time_pct = round((one_time_users / total_users) * 100, 2) if total_users > 0 else 0.0

    return {
        "total_users": total_users,
        "returning_users": returning_users,
        "one_time_users": one_time_users,
        "returning_users_percentage": returning_pct,
        "one_time_users_percentage": one_time_pct,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_query_categories(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #6: Query Categories (Time Range)

    Categorizes sessions by query_category field.

    Returns:
        - total_sessions: Total sessions analyzed
        - categories: List of category objects with count and percentage
    """
    db = get_db_client()
    query, params = query_categories_query(filters)

    category_data = db.execute_query(query, params)

    if not category_data:
        return {
            "total_sessions": 0,
            "categories": [],
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    total_sessions = sum(row["session_count"] for row in category_data)

    categories = [
        {
            "category": row["query_category"] or "uncategorized",
            "session_count": row["session_count"],
            "percentage": round((row["session_count"] / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        }
        for row in category_data
    ]

    return {
        "total_sessions": total_sessions,
        "categories": categories,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_returning_user_behavior(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #8: Returning User Behavior (Time Range)

    Analyzes behavior of returning users.

    Returns:
        - returning_users_count: Number of users with 2+ sessions
        - avg_sessions_per_returning_user: Average sessions for returning users
        - most_active_user_id: User with most sessions
        - most_active_user_sessions: Session count of most active user
        - avg_days_between_first_last: Average days between first and last chat
        - longest_active_user_span_days: Longest span in days
    """
    db = get_db_client()
    query, params = returning_user_behavior_query(filters)

    user_data = db.execute_query(query, params)

    if not user_data:
        return {
            "returning_users_count": 0,
            "avg_sessions_per_returning_user": 0.0,
            "most_active_user_id": None,
            "most_active_user_sessions": 0,
            "avg_days_between_first_last": 0.0,
            "longest_active_user_span_days": 0,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Filter for returning users (2+ sessions)
    returning_users = [u for u in user_data if u["session_count"] >= 2]

    if not returning_users:
        return {
            "returning_users_count": 0,
            "avg_sessions_per_returning_user": 0.0,
            "most_active_user_id": None,
            "most_active_user_sessions": 0,
            "avg_days_between_first_last": 0.0,
            "longest_active_user_span_days": 0,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Calculate metrics
    avg_sessions = round(
        sum(u["session_count"] for u in returning_users) / len(returning_users), 2
    )

    most_active = max(returning_users, key=lambda x: x["session_count"])

    avg_days_span = round(
        sum(u["active_days"] for u in returning_users) / len(returning_users), 2
    )

    longest_span_user = max(returning_users, key=lambda x: x["active_days"])

    return {
        "returning_users_count": len(returning_users),
        "avg_sessions_per_returning_user": avg_sessions,
        "most_active_user_id": most_active["user_id"],
        "most_active_user_sessions": most_active["session_count"],
        "avg_days_between_first_last": avg_days_span,
        "longest_active_user_span_days": longest_span_user["active_days"],
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_user_segmentation(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #9: User Segmentation (Time Range)

    Segments users by chat activity level:
    - Low activity: 1 chat
    - Medium activity: 2-5 chats
    - High activity: 6+ chats

    Returns:
        - total_users: Total unique users
        - segments: List of segment objects with:
            - segment_name: Activity level name
            - user_count: Number of users in segment
            - percentage: Percentage of total users
    """
    db = get_db_client()
    query, params = user_segmentation_query(filters)

    user_data = db.execute_query(query, params)

    if not user_data:
        return {
            "total_users": 0,
            "segments": [],
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Categorize users into segments
    total_users = len(user_data)
    low_activity = sum(1 for u in user_data if u["chat_count"] == 1)
    medium_activity = sum(1 for u in user_data if 2 <= u["chat_count"] <= 5)
    high_activity = sum(1 for u in user_data if u["chat_count"] >= 6)

    # Build segments
    segments = [
        {
            "segment_name": "Low Activity (1 chat)",
            "user_count": low_activity,
            "percentage": round((low_activity / total_users) * 100, 2) if total_users > 0 else 0.0
        },
        {
            "segment_name": "Medium Activity (2-5 chats)",
            "user_count": medium_activity,
            "percentage": round((medium_activity / total_users) * 100, 2) if total_users > 0 else 0.0
        },
        {
            "segment_name": "High Activity (6+ chats)",
            "user_count": high_activity,
            "percentage": round((high_activity / total_users) * 100, 2) if total_users > 0 else 0.0
        }
    ]

    return {
        "total_users": total_users,
        "segments": segments,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_time_patterns(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #10: Time Patterns (Time Range)

    Analyzes usage patterns by time:
    - Hour of day distribution
    - Day of week distribution

    Returns:
        - by_hour: Session counts for each hour (0-23)
        - by_day: Session counts for each day of week (0=Sunday, 6=Saturday)
        - peak_hour: Hour with most sessions
        - peak_day: Day with most sessions
    """
    db = get_db_client()
    query, params = time_patterns_query(filters)

    time_data = db.execute_query(query, params)

    if not time_data:
        return {
            "by_hour": [],
            "by_day": [],
            "peak_hour": None,
            "peak_day": None,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Aggregate by hour
    hour_data = {}
    for row in time_data:
        hour = int(row["hour_of_day"])
        if hour not in hour_data:
            hour_data[hour] = 0
        hour_data[hour] += row["session_count"]

    # Aggregate by day of week
    day_data = {}
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for row in time_data:
        day = int(row["day_of_week"])
        if day not in day_data:
            day_data[day] = 0
        day_data[day] += row["session_count"]

    # Format hour data
    by_hour = [
        {"hour": h, "session_count": hour_data.get(h, 0)}
        for h in range(24)
    ]

    # Format day data
    by_day = [
        {"day": day_names[d], "day_number": d, "session_count": day_data.get(d, 0)}
        for d in range(7)
    ]

    # Find peaks
    peak_hour_data = max(by_hour, key=lambda x: x["session_count"]) if by_hour else None
    peak_day_data = max(by_day, key=lambda x: x["session_count"]) if by_day else None

    return {
        "by_hour": by_hour,
        "by_day": by_day,
        "peak_hour": peak_hour_data["hour"] if peak_hour_data else None,
        "peak_hour_sessions": peak_hour_data["session_count"] if peak_hour_data else 0,
        "peak_day": peak_day_data["day"] if peak_day_data else None,
        "peak_day_sessions": peak_day_data["session_count"] if peak_day_data else 0,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_conversation_length(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #11: Conversation Length (Time Range)

    Analyzes conversation depth by counting messages per session.

    Returns:
        - total_sessions: Total number of sessions
        - avg_messages_per_session: Average messages per session
        - distribution: Breakdown by conversation length buckets
        - longest_session_messages: Max messages in a single session
    """
    db = get_db_client()
    query, params = conversation_length_query(filters)

    session_data = db.execute_query(query, params)

    if not session_data:
        return {
            "total_sessions": 0,
            "avg_messages_per_session": 0.0,
            "distribution": [],
            "longest_session_messages": 0,
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Calculate metrics
    total_sessions = len(session_data)
    total_messages = sum(row["message_count"] for row in session_data)
    avg_messages = round(total_messages / total_sessions, 2) if total_sessions > 0 else 0.0

    # Categorize by length
    short = sum(1 for row in session_data if row["message_count"] <= 2)
    medium = sum(1 for row in session_data if 3 <= row["message_count"] <= 5)
    long = sum(1 for row in session_data if row["message_count"] >= 6)

    longest_session = max(row["message_count"] for row in session_data)

    distribution = [
        {
            "category": "Short (1-2 messages)",
            "session_count": short,
            "percentage": round((short / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        },
        {
            "category": "Medium (3-5 messages)",
            "session_count": medium,
            "percentage": round((medium / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        },
        {
            "category": "Long (6+ messages)",
            "session_count": long,
            "percentage": round((long / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        }
    ]

    return {
        "total_sessions": total_sessions,
        "avg_messages_per_session": avg_messages,
        "distribution": distribution,
        "longest_session_messages": longest_session,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_platform_analytics(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #12: Platform Analytics (Time Range)

    Analyzes user platform preferences:
    - Language distribution
    - Voice vs text input
    - Mobile vs web usage

    Returns:
        - by_language: Session/user counts per language
        - by_voice: Voice vs text input breakdown
        - by_mobile: Mobile vs web breakdown
    """
    db = get_db_client()
    query, params = platform_analytics_query(filters)

    platform_data = db.execute_query(query, params)

    if not platform_data:
        return {
            "by_language": [],
            "by_voice": [],
            "by_mobile": [],
            "filters_applied": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "product_context": filters.product_context,
                "environment": filters.environment,
                "user_id": filters.user_id,
            }
        }

    # Aggregate by language
    lang_aggregated = {}
    for row in platform_data:
        lang = row["chat_language"] or "unknown"
        if lang not in lang_aggregated:
            lang_aggregated[lang] = {"sessions": 0, "users": 0}
        lang_aggregated[lang]["sessions"] += row["session_count"]
        lang_aggregated[lang]["users"] += row["user_count"]

    total_sessions = sum(data["sessions"] for data in lang_aggregated.values())

    by_language = [
        {
            "language": lang,
            "session_count": data["sessions"],
            "user_count": data["users"],
            "percentage": round((data["sessions"] / total_sessions) * 100, 2) if total_sessions > 0 else 0.0
        }
        for lang, data in lang_aggregated.items()
    ]
    by_language.sort(key=lambda x: x["session_count"], reverse=True)

    # Aggregate by voice input
    voice_aggregated = {"text": 0, "voice": 0}
    for row in platform_data:
        if row["is_voice_input"]:
            voice_aggregated["voice"] += row["session_count"]
        else:
            voice_aggregated["text"] += row["session_count"]

    total_voice_sessions = voice_aggregated["text"] + voice_aggregated["voice"]

    by_voice = [
        {
            "input_type": "Text",
            "session_count": voice_aggregated["text"],
            "percentage": round((voice_aggregated["text"] / total_voice_sessions) * 100, 2) if total_voice_sessions > 0 else 0.0
        },
        {
            "input_type": "Voice",
            "session_count": voice_aggregated["voice"],
            "percentage": round((voice_aggregated["voice"] / total_voice_sessions) * 100, 2) if total_voice_sessions > 0 else 0.0
        }
    ]

    # Aggregate by mobile
    mobile_aggregated = {"web": 0, "mobile": 0}
    for row in platform_data:
        if row["is_mobile_app"]:
            mobile_aggregated["mobile"] += row["session_count"]
        else:
            mobile_aggregated["web"] += row["session_count"]

    total_mobile_sessions = mobile_aggregated["web"] + mobile_aggregated["mobile"]

    by_mobile = [
        {
            "platform": "Web",
            "session_count": mobile_aggregated["web"],
            "percentage": round((mobile_aggregated["web"] / total_mobile_sessions) * 100, 2) if total_mobile_sessions > 0 else 0.0
        },
        {
            "platform": "Mobile",
            "session_count": mobile_aggregated["mobile"],
            "percentage": round((mobile_aggregated["mobile"] / total_mobile_sessions) * 100, 2) if total_mobile_sessions > 0 else 0.0
        }
    ]

    return {
        "by_language": by_language,
        "by_voice": by_voice,
        "by_mobile": by_mobile,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }


def compute_sentiment_analysis_kpi(filters: AnalyticsFilters) -> Dict[str, Any]:
    """
    KPI #13: Sentiment Analysis (Time Range)

    Uses VADER sentiment analysis to analyze user message sentiment.
    No LLM calls - fast lexicon-based approach!

    Returns:
        - Total messages analyzed
        - Average sentiment score (-1 to 1)
        - Distribution by category (positive/neutral/negative)
        - Most positive and most negative message examples
    """
    db = get_db_client()

    # Get all user queries for the time range
    query, params = get_all_user_queries(filters)
    queries_data = db.execute_query(query, params)

    # Compute sentiment analysis
    sentiment_results = compute_sentiment_analysis(queries_data)

    return {
        **sentiment_results,
        "filters_applied": {
            "start_date": filters.start_date.isoformat(),
            "end_date": filters.end_date.isoformat(),
            "product_context": filters.product_context,
            "environment": filters.environment,
            "user_id": filters.user_id,
        }
    }
