from fastapi import FastAPI
from src.routes.v1 import quotes
from src.middlewares.rate_limiter import RateLimiterMiddleware

# FastAPI app instance
app = FastAPI(
    title="OTC Crypto Trading API",
    description="API to fetch ticker data, historical data, and run price engine.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Add rate limiter middleware globally
app.add_middleware(RateLimiterMiddleware, rate_limit=60, window=60)

# Include routers for different API sections
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])

@app.get("/")
async def root():
    return {"message": "Welcome to the OTC Crypto Trading API"}
