import time
from fastapi import Request, HTTPException
from typing import Dict, List

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.client_history: Dict[str, List[float]] = {}

    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in self.client_history:
            self.client_history[client_ip] = []
        
        # Filter out old requests outside the window
        self.client_history[client_ip] = [
            t for t in self.client_history[client_ip] if current_time - t < self.window_seconds
        ]
        
        if len(self.client_history[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Resource Congestion",
                    "message": f"Aegis is processing a mountain of briefs. Please grant us a moment to breathe ({self.window_seconds}s).",
                    "retry_after_seconds": self.window_seconds
                }
            )
        
        self.client_history[client_ip].append(current_time)

# Default: 10 requests per minute per IP
limiter = RateLimiter(requests_limit=10, window_seconds=60)
