from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.middlewares.rate_limiter import RateLimiterMiddleware
from src.routes.v1 import orders, quotes
from src.websockets.websocket_routes import router as websocket_quote_router


# Define lifespan for handling the app's lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiate the RateLimiterMiddleware
    rate_limiter = RateLimiterMiddleware(app, rate_limit=60, window=60)
    app.state.rate_limiter = (
        rate_limiter  # Store it in app state for global access
    )
    yield  # This starts the app

    # Clean up Redis connection when the app shuts down
    await rate_limiter.close()


# FastAPI app instance with lifespan
app = FastAPI(
    title="OTC Crypto Trading API",
    description="API to fetch ticker data, historical data, and run price engine.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json",  # OpenAPI schema
    lifespan=lifespan,  # Register lifespan handler
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# Manually handle dispatch with RateLimiterMiddleware
@app.middleware("http")
async def custom_rate_limiter_middleware(request: Request, call_next):
    """
    Custom middleware that uses the RateLimiterMiddleware object to handle rate limiting.
    """
    rate_limiter = app.state.rate_limiter  # Access rate limiter from app state
    # Use the RateLimiterMiddleware's dispatch method
    return await rate_limiter.dispatch(request, call_next)


# Include routers for different API sections
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(websocket_quote_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.webp")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the OTC Crypto Trading API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
