📊 Analytics Backend – Coding Instructions for Claude

Context

You are building a read-only analytics backend for a client-facing chatbot analytics console.

This backend:
	•	Is written in Python using FastAPI
	•	Runs on Google Cloud Run
	•	Exposes GET-only analytics endpoints
	•	Performs SQL-based aggregation + light orchestration
	•	Does not mutate data
	•	Does not perform frontend logic

There is no ETL pipeline. All analytics are computed on-demand from the database using SQL.

⸻

Database Context

There are two interaction tables with similar (but not identical) schemas:

1. interaction_log
	•	Represents Heritage Pool Plus (pool-related chatbot)
	•	Pool-related conversations

2. landscape_interaction_log
	•	Represents Heritage Plus (landscape-related chatbot)
	•	Landscape-related conversations

Both tables:
	•	Store chatbot interaction/session data
	•	Have overlapping but not identical schemas
	•	Should be queried depending on product context

You will be provided the CSV schemas for both tables.
You must not assume identical columns — inspect schemas carefully and handle differences explicitly.

⸻

Product Context Selection

All analytics queries must support a product context filter:
product_context = "pool" | "landscape"

Rules:
	•	"pool" → query interaction_log
	•	"landscape" → query landscape_interaction_log
	•	Never query both tables in a single request

This must be implemented cleanly and explicitly.

⸻

Canonical Filter Model (REQUIRED)

All analytics functions and endpoints must accept the same filter schema:

AnalyticsFilters:
  start_date: datetime (required)
  end_date: datetime (required)
  product_context: "pool" | "landscape" (required)
  environment: optional
  user_id: optional


  Filters must:
	•	Be validated by FastAPI
	•	Be applied at the SQL level
	•	Never be post-filtered in Python

⸻

Backend Structure (MANDATORY)

The backend must follow this structure exactly:

backend/app/
├── main.py                  # FastAPI entrypoint
├── api/                     # HTTP routes only
│   └── analytics.py
├── analytics/               # Business logic
│   ├── kpis.py
│   ├── clustering.py
│   ├── engagement.py
│   └── retention.py
├── db/
│   ├── client.py            # DB connection + execution
│   └── queries.py           # Raw SQL templates
├── models/
│   └── filters.py           # Pydantic models


Strict separation of concerns:
	•	api/ → HTTP + validation only
	•	analytics/ → orchestration + formatting
	•	db/ → SQL execution only

⸻

KPI Requirements (IMPLEMENT ALL)

Each KPI must be implemented as a standalone function that:
	•	Accepts AnalyticsFilters
	•	Selects the correct table based on product context
	•	Executes SQL
	•	Returns structured JSON (no frontend math)

⸻

1️⃣ Session Metrics (Time Range)

For a given filter range:
	•	Total session count
	•	Number of sessions with negative feedback
	•	Number of sessions with positive feedback
	•	Average session duration

⸻

2️⃣ Pain Point Clustering (Time Range)

Cluster all user queries into exactly 5 predefined clusters:

Cluster 0: General branch hours / orders / pool questions
Cluster 1: Pump recommendations – product discovery
Cluster 2: Replacement filter parts – maintenance needs
Cluster 3: Stock availability by part number – inventory checks
Cluster 4: DE filter assembly – technical support

Rules:
	•	Use LLM-based classification if needed
	•	If LLM is used, implement a clean abstraction that accepts an API key
	•	Do NOT hardcode cluster results
	•	Output cluster counts + example queries per cluster

⸻

3️⃣ Volume Trends (Time Range)

Compute:
	•	Average sessions per day
	•	Peak usage day (date + count)
	•	Lowest usage day (date + count)

⸻

4️⃣ User Engagement (Time Range)

Compute:
	•	Unique users
	•	Total conversations
	•	Average conversations per user

⸻

5️⃣ User Retention (Time Range)

Compute:
	•	% returning users
	•	% one-time users

⸻

6️⃣ Query Categories (Time Range)

Categorize sessions into the following buckets:

Product catalog
Compatible parts
Pricing / inventory
Invoice / payment
Product manuals
Orders
General conversation
Tutorial videos
Out of scope
Nearest branch

Return:
	•	Count per category
	•	Percent of total

⸻

7️⃣ Agent Tool Usage (Time Range)

Compute:
	•	Count of sessions by agent tool invoked
	•	Percent breakdown

Example output:

Product catalog: 1,643 sessions (32.6%)
Compatible parts: 696 sessions (13.8%)
...

8️⃣ Returning User Behavior (Time Range)

Compute:
	•	Average sessions per returning user
	•	Most active user (by session count)
	•	Average days between first and last chat
	•	Longest active user span (days)

⸻

9️⃣ User Segmentation (Time Range)

Segment users into:

Power users: 10+ chats
Regular users: 3–9 chats
Casual users: 2 chats
One-time users: 1 chat

Return:
	•	Count per segment
	•	Percent of total users

⸻

API Design Rules
	•	All endpoints must be GET
	•	All filters must be query params
	•	Endpoints must be Swagger-visible
	•	Responses must be frontend-ready JSON
	•	No authentication logic needed for now

Example endpoint:

GET /analytics/overview

Non-Goals (DO NOT IMPLEMENT)
	•	No frontend code
	•	No background jobs
	•	No materialized views
	•	No data mutation
	•	No infra automation
	•	No caching (unless trivial and local)

⸻

Definition of Done

The backend is complete when:
	•	FastAPI launches successfully
	•	Swagger UI exposes all analytics endpoints
	•	Filters can be edited in Swagger
	•	Responses change correctly with filters
	•	All KPIs above are implemented

⸻

Final Instruction

Do not invent requirements.
Do not collapse KPIs.
Do not skip SQL rigor.
Ask clarifying questions if schema ambiguity exists.


## Database Tables

There are TWO interaction tables with similar but NOT identical schemas.

### 1️⃣ interaction_log (Heritage Pool Plus – POOL CONTEXT)

Columns:
- id (integer, PK)
- time_stamp (timestamp)
- user_id (varchar(50))
- session_id (text)

- input (text)
- output (text)
- full_prompt (text)
- chat_history (text)
- context (text)

- user_feedback (varchar(20))  // positive | negative | null
- user_feedback_reason (text)

- message_id (varchar(255))
- query_category (enum)

- environment (varchar)
- chat_bubble (varchar)
- context_aware (varchar)
- chat_language (char(2))

- orch_1_time (double precision)
- orch_2_time (double precision)
- response_time (double precision)
- execution_flow_time (text)
- residual_time (numeric)

- errors (text)

- is_voice_input (boolean)
- original_transcription (varchar)

NOTE: interaction_log DOES NOT have is_mobile_app


### 2️⃣ landscape_interaction_log (Heritage Plus – LANDSCAPE CONTEXT)

Columns:
(All columns listed above PLUS:)

- is_mobile_app (boolean)

---

## Product Context Routing (MANDATORY)

Every analytics request includes:

product_context = “pool” | “landscape”

Rules:
- "pool" → query interaction_log
- "landscape" → query landscape_interaction_log
- NEVER query both tables in one request

---

## Canonical Filter Model

All analytics functions accept this filter model:

```python
AnalyticsFilters:
  start_date: datetime (required)
  end_date: datetime (required)
  product_context: "pool" | "landscape" (required)
  environment: optional
  user_id: optional

  Filters must be applied at the SQL layer.


strictly plan with the user before implementing anything