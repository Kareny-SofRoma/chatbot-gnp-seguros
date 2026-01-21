from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import get_logger
from app.core.rate_limiter import rate_limiter
from app.core.env_validator import validate_environment
from app.core.exceptions import (
    ChatbotException,
    chatbot_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.api import chat, faq
from app.api.health import router as health_router

logger = get_logger()

# Validate environment variables on startup
logger.info("Validating environment variables...")
validate_environment(strict=True)
logger.info("✅ Environment validation passed")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot GNP API",
    description="API for GNP Insurance Chatbot with RAG",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(ChatbotException, chatbot_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Apply rate limiting to all requests except health checks and docs
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/health/detailed", "/health/ready", "/health/live", 
                            "/", "/docs", "/openapi.json", "/redoc"]:
        response = await call_next(request)
        return response
    
    # Check rate limit
    rate_limit_response = await rate_limiter.check_rate_limit(request)
    if rate_limit_response:
        return rate_limit_response
    
    # Proceed with request
    response = await call_next(request)
    return response

# Include routers
app.include_router(health_router)
app.include_router(chat.router)
app.include_router(faq.router)

@app.get("/")
async def root():
    return {
        "message": "Chatbot GNP API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Chatbot GNP API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS Origins: {settings.cors_origins}")
    logger.info("✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Chatbot GNP API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
