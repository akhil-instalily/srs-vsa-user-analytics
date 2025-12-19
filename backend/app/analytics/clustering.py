"""
Pain Point Clustering using Groq LLM.

KPI #2: Cluster user queries into 5 predefined categories.
"""

import os
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Predefined cluster definitions
CLUSTER_DEFINITIONS = {
    0: "General branch hours / orders / pool questions",
    1: "Pump recommendations – product discovery",
    2: "Replacement filter parts – maintenance needs",
    3: "Stock availability by part number – inventory checks",
    4: "DE filter assembly – technical support"
}


def classify_query_batch(queries: List[str], groq_api_key: str = None) -> List[int]:
    """
    Classify a batch of user queries into predefined clusters using Groq.

    Args:
        queries: List of user query strings
        groq_api_key: Optional Groq API key (defaults to env var)

    Returns:
        List of cluster IDs (0-4) corresponding to each query
    """
    if not groq_api_key:
        groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=groq_api_key)

    # Few-shot prompt with clear examples for each cluster
    few_shot_prompt = """You are classifying customer queries for a pool and landscape supply company into 5 categories.

Categories and Examples:

Cluster 0: General branch hours, order status, locations, general pool/landscape questions
Examples:
- "What are your hours?"
- "Where is the nearest branch?"
- "How do I track my order?"
- "What pool chemicals do you recommend?"

Cluster 1: Pump recommendations and product discovery (customer looking for product suggestions)
Examples:
- "What pumps do you carry?"
- "I need a variable speed pump recommendation"
- "Looking for a pentair heat pump"
- "Best pump for above ground pool?"

Cluster 2: Replacement filter parts and maintenance needs (customer needs specific parts for maintenance)
Examples:
- "I need a hayward skimmer basket"
- "Replacement grid assembly for filter"
- "Filter cartridge for C5030"
- "Need O-rings for my pump"

Cluster 3: Stock availability and inventory checks by part number
Examples:
- "Do you have part# 12345 in stock?"
- "Is the F5B available?"
- "Do you carry CX580XRE?"
- "Stock check on hayward SP1091LX"

Cluster 4: DE filter assembly and technical support (technical help, installation, troubleshooting)
Examples:
- "How do I assemble a DE filter?"
- "My filter is leaking, help?"
- "Installation guide for grid assembly"
- "Troubleshoot pump not priming"

Respond ONLY with the cluster number (0-4). Do not use thinking tags. Just output the number."""

    results = []

    # Process ALL queries (no limit - user will control via date range)
    for query in queries:
        if not query or query.strip() == "":
            results.append(0)  # Default to cluster 0 for empty queries
            continue

        # Build classification prompt for this query
        prompt = f"""{few_shot_prompt}

Query to classify: "{query}"

Cluster number:"""

        try:
            completion = client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_completion_tokens=100,  # Increased to allow model to complete thinking process
                stream=False,
            )

            # Extract cluster number from response
            response_text = completion.choices[0].message.content.strip()

            # Try to extract the number
            cluster_id = None
            for char in response_text:
                if char.isdigit():
                    cluster_id = int(char)
                    break

            # Validate cluster ID
            if cluster_id is not None and 0 <= cluster_id <= 4:
                results.append(cluster_id)
            else:
                results.append(0)  # Default to cluster 0 if invalid

        except Exception as e:
            print(f"Error classifying query: {e}")
            results.append(0)  # Default to cluster 0 on error

    return results


def cluster_queries(
    queries_data: List[Dict[str, Any]],
    max_examples_per_cluster: int = 5
) -> Dict[str, Any]:
    """
    Cluster user queries and return counts + examples.

    Args:
        queries_data: List of dicts with 'user_query' field
        max_examples_per_cluster: Max number of example queries to return per cluster

    Returns:
        Dict with cluster counts and examples
    """
    if not queries_data:
        return {
            "total_queries": 0,
            "clusters": []
        }

    # Extract query strings
    query_strings = [q.get("user_query", "") for q in queries_data]

    # Classify queries
    cluster_ids = classify_query_batch(query_strings)

    # Organize results by cluster
    cluster_results = {i: {"queries": [], "count": 0} for i in range(5)}

    for query, cluster_id in zip(query_strings, cluster_ids):
        cluster_results[cluster_id]["count"] += 1
        if len(cluster_results[cluster_id]["queries"]) < max_examples_per_cluster:
            cluster_results[cluster_id]["queries"].append(query)

    # Format output
    clusters = []
    for cluster_id in range(5):
        clusters.append({
            "cluster_id": cluster_id,
            "cluster_name": CLUSTER_DEFINITIONS[cluster_id],
            "count": cluster_results[cluster_id]["count"],
            "percentage": round(
                (cluster_results[cluster_id]["count"] / len(query_strings)) * 100, 2
            ) if query_strings else 0,
            "example_queries": cluster_results[cluster_id]["queries"]
        })

    return {
        "total_queries": len(query_strings),
        "clusters": clusters
    }
