import os
import logging
import antigravity  # Imported for the xkcd easter egg
from fastapi import FastAPI, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel  # <-- NEW: Imported for AI request validation
import psycopg2
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(
    title="Production API",
    description="A productionized FastAPI backend with PostgreSQL, Redis, and AI mock integration.",
    version="1.0.0"
)

# --- Helper Functions ---

# Database health check helper
def check_db_connection() -> str:
    conn = None
    try:
        # Prioritize DATABASE_URL if available, otherwise construct from env vars
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            logger.info("Connecting to DB using DATABASE_URL")
            conn = psycopg2.connect(db_url, connect_timeout=2)
        else:
            host = os.getenv("POSTGRES_HOST", "db")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "postgres")
            dbname = os.getenv("POSTGRES_DB", "postgres")
            logger.info(f"Connecting to DB at {host}:{port} as user={user}")
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname,
                connect_timeout=2
            )
        conn.close()
        return "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return "disconnected"

# Redis health check helper
def check_redis_connection() -> str:
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        logger.info(f"Connecting to Redis using URL: {redis_url}")
        client = redis.Redis.from_url(redis_url, socket_timeout=2)
        # Ping the redis server to verify active connection
        if client.ping():
            return "connected"
        return "disconnected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return "disconnected"

# --- Pydantic Models ---

# <-- NEW: AI Schema definition
class PromptRequest(BaseModel):
    prompt: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check(response: Response):
    db_status = check_db_connection()
    redis_status = check_redis_connection()
    
    overall_status = "healthy"
    if db_status == "disconnected" or redis_status == "disconnected":
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status
    }

@app.get("/antigravity", tags=["Easter Egg"])
def redirect_to_xkcd():
    # Use RedirectResponse to send the user to the classic comic
    logger.info("Redirecting user to antigravity comic...")
    return RedirectResponse(url="https://xkcd.com/353/")

# <-- NEW: AI / LLM Mock Endpoint
@app.post("/api/v1/generate", summary="Generate AI Response", tags=["AI Model"])
def generate_text(request: PromptRequest):
    """
    Mock AI endpoint. In a real production scenario, this would route 
    to an LLM service (like OpenAI API, vLLM, or a local HuggingFace container).
    """
    logger.info(f"Processing AI prompt: {request.prompt}")
    return {
        "model": "gpt-mock-v1",
        "input": request.prompt,
        "response": f"This is an AI generated response for: '{request.prompt}'",
        "processing_time_ms": 120
    }