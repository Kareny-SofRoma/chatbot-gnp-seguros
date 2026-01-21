from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.redis_client import get_redis
from app.core.logger import get_logger
import time
from typing import Optional

logger = get_logger()

class RateLimiter:
    """
    Simple but effective rate limiter using Redis
    Limits requests per IP address
    """
    
    def __init__(
        self,
        requests_per_minute: int = 20,
        requests_per_hour: int = 100,
        requests_per_day: int = 500
    ):
        self.redis = get_redis()
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
    
    async def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """
        Check if request exceeds rate limits
        Returns JSONResponse with 429 if exceeded, None if OK
        """
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check all time windows
        limits = [
            (60, self.requests_per_minute, "minute"),
            (3600, self.requests_per_hour, "hour"),
            (86400, self.requests_per_day, "day")
        ]
        
        for window_seconds, max_requests, window_name in limits:
            key = f"rate_limit:{client_ip}:{window_name}"
            
            try:
                # Get current count
                current = self.redis.get(key)
                
                if current is None:
                    # First request in this window
                    self.redis.setex(key, window_seconds, 1)
                else:
                    current_count = int(current)
                    
                    if current_count >= max_requests:
                        # Rate limit exceeded
                        ttl = self.redis.ttl(key)
                        logger.warning(
                            f"Rate limit exceeded for {client_ip} - "
                            f"{current_count}/{max_requests} requests per {window_name}"
                        )
                        
                        return JSONResponse(
                            status_code=429,
                            content={
                                "error": "Rate limit exceeded",
                                "message": f"Demasiadas peticiones. Por favor, espera {ttl} segundos.",
                                "retry_after": ttl,
                                "limit": f"{max_requests} requests per {window_name}"
                            },
                            headers={
                                "Retry-After": str(ttl),
                                "X-RateLimit-Limit": str(max_requests),
                                "X-RateLimit-Remaining": "0",
                                "X-RateLimit-Reset": str(int(time.time()) + ttl)
                            }
                        )
                    
                    # Increment counter
                    self.redis.incr(key)
            
            except Exception as e:
                # If Redis fails, log but don't block request
                logger.error(f"Rate limiter error: {str(e)}")
                # Fail open - allow request if rate limiter is broken
                continue
        
        return None
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request
        Handles proxies and load balancers
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"

# Global instance
rate_limiter = RateLimiter(
    requests_per_minute=20,  # 20 requests por minuto
    requests_per_hour=100,   # 100 requests por hora
    requests_per_day=500     # 500 requests por día
)
