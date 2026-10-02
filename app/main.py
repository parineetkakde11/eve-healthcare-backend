import logging
from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, diagnostic, bookings, payments

# Configure structured console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for diagnostic test bookings and simulated payments.",
    version="1.0.0",
)

# Include routers
app.include_router(auth.router)
app.include_router(diagnostic.router)
app.include_router(bookings.router)
app.include_router(payments.router)

@app.get("/health", tags=["Health"])
def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }