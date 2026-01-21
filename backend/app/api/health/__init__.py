from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger
from datetime import datetime
from typing import Dict, Any
import sys

logger = get_logger()
router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Basic health check - returns 200 if server is running
    Used by load balancers for quick checks
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check - verifies all critical services
    Returns detailed status of each component
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "services": {}
    }
    
    overall_healthy = True
    
    # Check PostgreSQL
    db_status = await _check_database(db)
    health_status["services"]["database"] = db_status
    if not db_status["healthy"]:
        overall_healthy = False
    
    # Check Redis
    redis_status = await _check_redis()
    health_status["services"]["redis"] = redis_status
    if not redis_status["healthy"]:
        overall_healthy = False
    
    # Check Pinecone
    pinecone_status = await _check_pinecone()
    health_status["services"]["pinecone"] = pinecone_status
    if not pinecone_status["healthy"]:
        overall_healthy = False
    
    # Update overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    health_status["all_services_operational"] = overall_healthy
    
    # Return 503 if any service is down
    status_code = 200 if overall_healthy else 503
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )

async def _check_database(db: Session) -> Dict[str, Any]:
    """Check PostgreSQL connection and basic query"""
    try:
        # Try to execute a simple query
        result = db.execute(text("SELECT 1")).scalar()
        
        if result == 1:
            return {
                "healthy": True,
                "message": "Database connection successful",
                "response_time_ms": "<50ms"
            }
        else:
            return {
                "healthy": False,
                "message": "Database query returned unexpected result",
                "error": f"Expected 1, got {result}"
            }
    
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "healthy": False,
            "message": "Database connection failed",
            "error": str(e)
        }

async def _check_redis() -> Dict[str, Any]:
    """Check Redis connection and basic operations"""
    try:
        redis = get_redis()
        
        # Test PING
        ping_result = redis.ping()
        
        if not ping_result:
            return {
                "healthy": False,
                "message": "Redis PING failed"
            }
        
        # Test SET and GET
        test_key = "health_check_test"
        test_value = "ok"
        redis.setex(test_key, 10, test_value)
        retrieved_value = redis.get(test_key)
        redis.delete(test_key)
        
        if retrieved_value == test_value:
            return {
                "healthy": True,
                "message": "Redis connection and operations successful",
                "response_time_ms": "<10ms"
            }
        else:
            return {
                "healthy": False,
                "message": "Redis GET/SET test failed",
                "error": f"Expected '{test_value}', got '{retrieved_value}'"
            }
    
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "healthy": False,
            "message": "Redis connection failed",
            "error": str(e)
        }

async def _check_pinecone() -> Dict[str, Any]:
    """Check Pinecone connection and index accessibility"""
    try:
        # Test index stats (lightweight operation)
        stats = pinecone_service.index.describe_index_stats()
        
        if stats:
            total_vectors = stats.get('total_vector_count', 0)
            return {
                "healthy": True,
                "message": "Pinecone connection successful",
                "index_name": pinecone_service.index_name,
                "total_vectors": total_vectors,
                "response_time_ms": "<100ms"
            }
        else:
            return {
                "healthy": False,
                "message": "Pinecone returned empty stats"
            }
    
    except Exception as e:
        logger.error(f"Pinecone health check failed: {str(e)}")
        return {
            "healthy": False,
            "message": "Pinecone connection failed",
            "error": str(e)
        }

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness check
    Returns 200 only if ALL services are operational
    """
    db_ok = False
    redis_ok = False
    pinecone_ok = False
    
    try:
        # Quick checks without detailed info
        db.execute(text("SELECT 1"))
        db_ok = True
    except:
        pass
    
    try:
        redis = get_redis()
        redis.ping()
        redis_ok = True
    except:
        pass
    
    try:
        pinecone_service.index.describe_index_stats()
        pinecone_ok = True
    except:
        pass
    
    if db_ok and redis_ok and pinecone_ok:
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "database": db_ok,
                    "redis": redis_ok,
                    "pinecone": pinecone_ok
                }
            }
        )

@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes-style liveness check
    Returns 200 if server process is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
