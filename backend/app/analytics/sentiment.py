"""
Sentiment Analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).

KPI #13: Analyze sentiment of user messages without LLM calls.
VADER is a lexicon and rule-based sentiment analysis tool - extremely fast!
"""

from typing import List, Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def analyze_sentiment_batch(messages: List[str]) -> List[Dict[str, float]]:
    """
    Analyze sentiment of a batch of messages using VADER.

    Args:
        messages: List of user message strings

    Returns:
        List of sentiment scores for each message
        Each score dict contains: neg, neu, pos, compound
    """
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for message in messages:
        if not message or message.strip() == "":
            # Default neutral for empty messages
            results.append({
                "neg": 0.0,
                "neu": 1.0,
                "pos": 0.0,
                "compound": 0.0
            })
            continue

        # VADER returns: neg, neu, pos, compound
        # compound: normalized score from -1 (most negative) to +1 (most positive)
        scores = analyzer.polarity_scores(message)
        results.append(scores)

    return results


def categorize_sentiment(compound_score: float) -> str:
    """
    Categorize sentiment based on compound score.

    VADER compound score interpretation:
    - >= 0.05: Positive
    - <= -0.05: Negative
    - Between: Neutral

    Args:
        compound_score: VADER compound score (-1 to 1)

    Returns:
        Sentiment category: "positive", "neutral", or "negative"
    """
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"


def compute_sentiment_analysis(
    queries_data: List[Dict[str, Any]],
    max_examples_per_category: int = 5
) -> Dict[str, Any]:
    """
    Compute sentiment analysis for user queries.

    Args:
        queries_data: List of dicts with 'user_query' field
        max_examples_per_category: Max examples to return per sentiment category

    Returns:
        Dict with sentiment distribution and statistics
    """
    if not queries_data:
        return {
            "total_messages": 0,
            "sentiment_distribution": [],
            "avg_sentiment_score": 0.0,
            "most_positive_messages": [],
            "most_negative_messages": []
        }

    # Extract messages
    messages = [q.get("user_query", "") for q in queries_data]

    # Analyze sentiment
    sentiment_scores = analyze_sentiment_batch(messages)

    # Categorize and organize results
    categories = {
        "positive": {"count": 0, "messages": []},
        "neutral": {"count": 0, "messages": []},
        "negative": {"count": 0, "messages": []}
    }

    message_sentiments = []  # For finding most positive/negative

    for message, scores in zip(messages, sentiment_scores):
        category = categorize_sentiment(scores["compound"])
        categories[category]["count"] += 1

        # Store examples (up to max)
        if len(categories[category]["messages"]) < max_examples_per_category:
            categories[category]["messages"].append({
                "message": message,
                "score": scores["compound"]
            })

        message_sentiments.append({
            "message": message,
            "compound": scores["compound"]
        })

    # Calculate statistics
    total_messages = len(messages)
    avg_compound = sum(s["compound"] for s in sentiment_scores) / total_messages if total_messages > 0 else 0.0

    # Sort to find most positive/negative
    sorted_sentiments = sorted(message_sentiments, key=lambda x: x["compound"], reverse=True)
    most_positive = sorted_sentiments[:max_examples_per_category]
    most_negative = sorted_sentiments[-max_examples_per_category:][::-1]  # Reverse to show most negative first

    # Format distribution
    distribution = []
    for category_name in ["positive", "neutral", "negative"]:
        count = categories[category_name]["count"]
        distribution.append({
            "category": category_name,
            "count": count,
            "percentage": round((count / total_messages) * 100, 2) if total_messages > 0 else 0,
            "example_messages": [m["message"] for m in categories[category_name]["messages"]]
        })

    return {
        "total_messages": total_messages,
        "avg_sentiment_score": round(avg_compound, 3),
        "sentiment_distribution": distribution,
        "most_positive_messages": [
            {"message": m["message"], "score": round(m["compound"], 3)}
            for m in most_positive
        ],
        "most_negative_messages": [
            {"message": m["message"], "score": round(m["compound"], 3)}
            for m in most_negative
        ]
    }
