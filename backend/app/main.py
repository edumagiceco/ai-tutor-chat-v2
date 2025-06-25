from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.api.v1.websocket import websocket_endpoint

# Create tables
Base.metadata.create_all(bind=engine)


class UTF8Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # JSON 응답인 경우에만 헤더 설정
        if response.headers.get("content-type", "").startswith("application/json"):
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up AI Tutor System...")
    yield
    # Shutdown
    print("Shutting down AI Tutor System...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add UTF-8 middleware
app.add_middleware(UTF8Middleware)

# Set CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:8081", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Tutor System API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# WebSocket endpoint
@app.websocket("/ws/{token}")
async def websocket_route(websocket: WebSocket, token: str):
    await websocket_endpoint(websocket, token)