from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import get_logger
from app.api import chat, faq

logger = get_logger()

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

# Include routers
app.include_router(chat.router)
app.include_router(faq.router)

@app.get("/")
async def root():
    return {
        "message": "Chatbot GNP API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
