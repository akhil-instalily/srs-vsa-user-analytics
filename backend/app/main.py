"""
FastAPI Analytics Backend for SRS VSA User Analytics

Read-only analytics backend for Heritage Pool Plus and Heritage Plus chatbot analytics.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_db_client

# Initialize FastAPI app
app = FastAPI(
    title="SRS VSA Analytics API",
    description="Read-only analytics backend for chatbot analytics console",
    version="1.0.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    print("=� Starting SRS VSA Analytics API...")
    print("=� Initializing database connection...")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    print("=� Shutting down SRS VSA Analytics API...")
    db_client = get_db_client()
    db_client.close()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "SRS VSA Analytics API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint that verifies database connectivity.

    Tests connection to both interaction_log and landscape_interaction_log tables.
    """
    db_client = get_db_client()
    connection_status = db_client.test_connection()

    if connection_status.get("status") == "connected":
        return {
            "status": "healthy",
            "database": connection_status
        }
    else:
        return {
            "status": "unhealthy",
            "database": connection_status
        }


# Import and include API routers
from app.api import analytics
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
