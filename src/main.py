from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.middlewares.jwt_middleware import JWTAuthMiddleware
from src.middlewares.rate_limiter import RateLimiterMiddleware
from src.routes.v1 import auth, documents, orders, quotes
from src.websockets.websocket_routes import router as websocket_quote_router


# Define lifespan for handling the app's lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiate the RateLimiterMiddleware
    rate_limiter = RateLimiterMiddleware(app, rate_limit=60, window=60)
    app.state.rate_limiter = rate_limiter  # Store it in app state for global access
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

allowed_origins = [
    "http://localhost:3000",  # UI server URL (e.g., React or Angular)
    "http://localhost:8080",  # Another UI server URL or mobile app URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allow requests from these origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
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
