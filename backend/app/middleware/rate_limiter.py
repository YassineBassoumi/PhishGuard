"""
Rate Limiting Middleware
Prevents API abuse by limiting requests per IP address
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Tuple
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm
    
    Tracks requests per IP address and enforces limits based on endpoint
    """
    
    def __init__(self):
        # Store: {ip_address: {endpoint: [(timestamp, count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        # Track failed login attempts for brute force detection
        # Store: {ip_address: [(timestamp, username_attempted)]}
        self.failed_logins: Dict[str, list] = defaultdict(list)
        
        # Track IPs that have been flagged for brute force
        # Store: {ip_address: (timestamp, is_blocked)}
        self.brute_force_ips: Dict[str, Tuple[datetime, bool]] = {}
        
        self.lock = asyncio.Lock()
        self._cleanup_task = None
        
        # Brute force detection thresholds
        self.brute_force_threshold = 10  # Failed attempts before flagging
        self.brute_force_window = 300  # 5 minutes window
        self.brute_force_block_duration = 3600  # Block for 1 hour
        
        # Rate limit configurations (requests per minute)
        self.limits = {
            # Authentication endpoints - stricter limits
            "/api/auth/login": (5, 60),  # 5 requests per minute
            "/api/auth/register": (3, 60),  # 3 requests per minute
            "/api/password-reset/request": (3, 60),  # 3 requests per minute
            "/api/password-reset/reset": (5, 60),  # 5 requests per minute
            "/api/email-verification/resend": (3, 60),  # 3 requests per minute
            
            # 2FA endpoints
            "/api/2fa/setup": (5, 60),
            "/api/2fa/enable": (5, 60),
            "/api/2fa/disable": (5, 60),
            
            # Analysis endpoints - moderate limits
            "/api/analyze-email": (30, 60),  # 30 requests per minute
            "/api/analyze-url": (30, 60),  # 30 requests per minute
            "/api/analyze-bulk": (10, 60),  # 10 requests per minute (more expensive)
            
            # Email provider endpoints
            "/api/email/gmail/emails": (20, 60),
            "/api/email/outlook/emails": (20, 60),
            
            # General API endpoints
            "/api/stats": (30, 60),
            "/api/history": (30, 60),
            "/api/threat-distribution": (30, 60),
            
            # Admin endpoints - very strict
            "/api/admin/users": (10, 60),
            "/api/admin/ban": (5, 60),
            "/api/admin/unban": (5, 60),
            
            # Default limit for unspecified endpoints
            "default": (60, 60),  # 60 requests per minute
        }
    
    def _ensure_cleanup_task(self):
        """Ensure cleanup task is running"""
        if self._cleanup_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._cleanup_loop())
            except RuntimeError:
                # No event loop running yet, will be created on first request
                pass
    
    async def _cleanup_loop(self):
        """Background task to clean up old request records"""
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            await self._cleanup_old_requests()
    
    async def _cleanup_old_requests(self):
        """Remove request records older than 1 hour"""
        async with self.lock:
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            for ip in list(self.requests.keys()):
                for endpoint in list(self.requests[ip].keys()):
                    # Filter out old requests
                    self.requests[ip][endpoint] = [
                        (ts, count) for ts, count in self.requests[ip][endpoint]
                        if ts > cutoff_time
                    ]
                    
                    # Remove empty endpoint entries
                    if not self.requests[ip][endpoint]:
                        del self.requests[ip][endpoint]
                
                # Remove empty IP entries
                if not self.requests[ip]:
                    del self.requests[ip]
            
            # Clean up old failed login attempts
            failed_login_cutoff = datetime.now() - timedelta(seconds=self.brute_force_window)
            for ip in list(self.failed_logins.keys()):
                self.failed_logins[ip] = [
                    (ts, username) for ts, username in self.failed_logins[ip]
                    if ts > failed_login_cutoff
                ]
                if not self.failed_logins[ip]:
                    del self.failed_logins[ip]
            
            # Clean up old brute force blocks
            block_cutoff = datetime.now() - timedelta(seconds=self.brute_force_block_duration)
            for ip in list(self.brute_force_ips.keys()):
                block_time, is_blocked = self.brute_force_ips[ip]
                if block_time < block_cutoff:
                    del self.brute_force_ips[ip]
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (behind proxy)
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
    
    def _get_rate_limit(self, path: str) -> Tuple[int, int]:
        """Get rate limit configuration for endpoint"""
        # Try exact match first
        if path in self.limits:
            return self.limits[path]
        
        # Try prefix match for dynamic routes
        for endpoint_pattern, limit in self.limits.items():
            if endpoint_pattern != "default" and path.startswith(endpoint_pattern):
                return limit
        
        # Return default limit
        return self.limits["default"]
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request should be rate limited
        
        Returns:
            True if request is allowed
            False if rate limit exceeded
        """
        # Ensure cleanup task is running
        self._ensure_cleanup_task()
        
        ip = self._get_client_ip(request)
        path = request.url.path
        now = datetime.now()
        
        # Get rate limit for this endpoint
        max_requests, window_seconds = self._get_rate_limit(path)
        window_start = now - timedelta(seconds=window_seconds)
        
        async with self.lock:
            # Get request history for this IP and endpoint
            request_history = self.requests[ip][path]
            
            # Remove requests outside the time window
            request_history = [
                (ts, count) for ts, count in request_history
                if ts > window_start
            ]
            
            # Count total requests in window
            total_requests = sum(count for _, count in request_history)
            
            # Check if limit exceeded
            if total_requests >= max_requests:
                logger.warning(
                    f"Rate limit exceeded for IP {ip} on {path}: "
                    f"{total_requests}/{max_requests} requests in {window_seconds}s"
                )
                return False
            
            # Add current request
            request_history.append((now, 1))
            self.requests[ip][path] = request_history
            
            return True
    
    def get_rate_limit_headers(self, request: Request) -> Dict[str, str]:
        """Get rate limit headers for response"""
        ip = self._get_client_ip(request)
        path = request.url.path
        now = datetime.now()
        
        max_requests, window_seconds = self._get_rate_limit(path)
        window_start = now - timedelta(seconds=window_seconds)
        
        # Count requests in current window
        request_history = self.requests.get(ip, {}).get(path, [])
        request_history = [
            (ts, count) for ts, count in request_history
            if ts > window_start
        ]
        total_requests = sum(count for _, count in request_history)
        
        remaining = max(0, max_requests - total_requests)
        
        # Calculate reset time (end of current window)
        if request_history:
            oldest_request = min(ts for ts, _ in request_history)
            reset_time = oldest_request + timedelta(seconds=window_seconds)
            reset_seconds = int((reset_time - now).total_seconds())
        else:
            reset_seconds = window_seconds
        
        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_seconds),
            "X-RateLimit-Window": str(window_seconds),
        }
    
    async def record_failed_login(self, ip: str, username: str) -> bool:
        """
        Record a failed login attempt and check for brute force attack
        
        Returns:
            True if brute force attack detected (threshold exceeded)
            False otherwise
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.brute_force_window)
        
        async with self.lock:
            # Add failed attempt
            self.failed_logins[ip].append((now, username))
            
            # Clean old attempts
            self.failed_logins[ip] = [
                (ts, user) for ts, user in self.failed_logins[ip]
                if ts > window_start
            ]
            
            # Count recent failed attempts
            failed_count = len(self.failed_logins[ip])
            
            # Check if threshold exceeded
            if failed_count >= self.brute_force_threshold:
                # Mark IP as brute force attacker
                self.brute_force_ips[ip] = (now, True)
                
                logger.critical(
                    f"BRUTE FORCE ATTACK DETECTED from IP {ip}: "
                    f"{failed_count} failed login attempts in {self.brute_force_window}s"
                )
                
                return True
            
            return False
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked due to brute force"""
        if ip not in self.brute_force_ips:
            return False
        
        block_time, is_blocked = self.brute_force_ips[ip]
        now = datetime.now()
        
        # Check if block has expired
        if now - block_time > timedelta(seconds=self.brute_force_block_duration):
            del self.brute_force_ips[ip]
            return False
        
        return is_blocked
    
    def get_brute_force_stats(self, ip: str) -> Dict:
        """Get brute force attack statistics for an IP"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.brute_force_window)
        
        # Get recent failed attempts
        failed_attempts = [
            (ts, username) for ts, username in self.failed_logins.get(ip, [])
            if ts > window_start
        ]
        
        # Get unique usernames attempted
        usernames_attempted = list(set(username for _, username in failed_attempts))
        
        # Check if blocked
        is_blocked = self.is_ip_blocked(ip)
        block_info = None
        if is_blocked and ip in self.brute_force_ips:
            block_time, _ = self.brute_force_ips[ip]
            block_expires = block_time + timedelta(seconds=self.brute_force_block_duration)
            block_info = {
                "blocked_at": block_time.isoformat(),
                "expires_at": block_expires.isoformat(),
                "remaining_seconds": int((block_expires - now).total_seconds())
            }
        
        return {
            "ip_address": ip,
            "failed_attempts": len(failed_attempts),
            "threshold": self.brute_force_threshold,
            "window_seconds": self.brute_force_window,
            "usernames_attempted": usernames_attempted,
            "is_blocked": is_blocked,
            "block_info": block_info,
            "pattern": "automated" if len(failed_attempts) >= self.brute_force_threshold else "normal"
        }
    
    def get_all_brute_force_ips(self) -> list:
        """Get all IPs currently flagged for brute force attacks"""
        now = datetime.now()
        result = []
        
        for ip, (block_time, is_blocked) in self.brute_force_ips.items():
            # Check if still within block period
            if now - block_time <= timedelta(seconds=self.brute_force_block_duration):
                stats = self.get_brute_force_stats(ip)
                result.append(stats)
        
        return result


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on all requests
    """
    # Skip rate limiting for health check and docs
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json", "/api/health"]:
        return await call_next(request)
    
    # Check rate limit
    allowed = await rate_limiter.check_rate_limit(request)
    
    if not allowed:
        # Get rate limit info
        max_requests, window_seconds = rate_limiter._get_rate_limit(request.url.path)
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                "error": "too_many_requests",
                "retry_after": window_seconds
            },
            headers={
                "Retry-After": str(window_seconds),
                **rate_limiter.get_rate_limit_headers(request)
            }
        )
    
    # Process request and add rate limit headers to response
    response = await call_next(request)
    
    # Add rate limit headers
    headers = rate_limiter.get_rate_limit_headers(request)
    for key, value in headers.items():
        response.headers[key] = value
    
    return response
