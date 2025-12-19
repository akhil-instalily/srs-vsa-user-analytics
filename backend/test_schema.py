"""
Test script to explore database schema and sample data
"""

import sys
sys.path.append('/Users/akhilreddy/Documents/srs-vsa-user-analytics/backend')

from app.db import get_db_client

db = get_db_client()

print("=" * 80)
print("EXPLORING DATABASE SCHEMA")
print("=" * 80)

# Get schema for interaction_log
print("\n1. INTERACTION_LOG SCHEMA (Pool Context)")
print("-" * 80)
schema_query = """
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'interaction_log'
ORDER BY ordinal_position;
"""
columns = db.execute_query(schema_query)
for col in columns:
    print(f"  {col['column_name']:30s} | {col['data_type']:20s} | Nullable: {col['is_nullable']}")

# Get sample row
print("\n2. SAMPLE ROW FROM INTERACTION_LOG")
print("-" * 80)
sample = db.execute_query("SELECT * FROM interaction_log LIMIT 1;", fetch_one=True)
if sample:
    for key, value in sample[0].items():
        print(f"  {key:30s} = {str(value)[:50]}")

# Get schema for landscape_interaction_log
print("\n3. LANDSCAPE_INTERACTION_LOG SCHEMA (Landscape Context)")
print("-" * 80)
schema_query_landscape = """
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'landscape_interaction_log'
ORDER BY ordinal_position;
"""
columns_landscape = db.execute_query(schema_query_landscape)
for col in columns_landscape:
    print(f"  {col['column_name']:30s} | {col['data_type']:20s} | Nullable: {col['is_nullable']}")

# Get sample row
print("\n4. SAMPLE ROW FROM LANDSCAPE_INTERACTION_LOG")
print("-" * 80)
sample_landscape = db.execute_query("SELECT * FROM landscape_interaction_log LIMIT 1;", fetch_one=True)
if sample_landscape:
    for key, value in sample_landscape[0].items():
        print(f"  {key:30s} = {str(value)[:50]}")

# Check query_category values
print("\n5. DISTINCT QUERY_CATEGORY VALUES (interaction_log)")
print("-" * 80)
categories = db.execute_query("""
SELECT query_category, COUNT(*) as count
FROM interaction_log
WHERE query_category IS NOT NULL
GROUP BY query_category
ORDER BY count DESC;
""")
for cat in categories:
    print(f"  {cat['query_category']:40s} | Count: {cat['count']}")

# Check user_feedback values
print("\n6. DISTINCT USER_FEEDBACK VALUES (interaction_log)")
print("-" * 80)
feedback = db.execute_query("""
SELECT user_feedback, COUNT(*) as count
FROM interaction_log
WHERE user_feedback IS NOT NULL
GROUP BY user_feedback
ORDER BY count DESC;
""")
for fb in feedback:
    print(f"  {fb['user_feedback']:20s} | Count: {fb['count']}")

print("\n" + "=" * 80)
print("SCHEMA EXPLORATION COMPLETE")
print("=" * 80)
