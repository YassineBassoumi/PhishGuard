"""
Rate Limit Utility Functions
Helper functions for managing rate limits
"""

from app.middleware import rate_limiter
from typing import Dict, List
from datetime import datetime, timedelta


def get_rate_limit_status(ip_address: str) -> Dict:
    """
    Get current rate limit status for an IP address
    
    Args:
        ip_address: IP address to check
        
    Returns:
        Dictionary with rate limit information
    """
    now = datetime.now()
    status = {
        "ip_address": ip_address,
        "endpoints": {},
        "total_requests": 0
    }
    
    if ip_address in rate_limiter.requests:
        for endpoint, request_history in rate_limiter.requests[ip_address].items():
            max_requests, window_seconds = rate_limiter._get_rate_limit(endpoint)
            window_start = now - timedelta(seconds=window_seconds)
            
            # Count requests in current window
            recent_requests = [
                (ts, count) for ts, count in request_history
                if ts > window_start
            ]
            total = sum(count for _, count in recent_requests)
            
            status["endpoints"][endpoint] = {
                "requests_in_window": total,
                "limit": max_requests,
                "remaining": max(0, max_requests - total),
                "window_seconds": window_seconds
            }
            status["total_requests"] += total
    
    return status


def clear_rate_limit(ip_address: str, endpoint: str = None) -> bool:
    """
    Clear rate limit records for an IP address
    
    Args:
        ip_address: IP address to clear
        endpoint: Optional specific endpoint to clear (clears all if None)
        
    Returns:
        True if records were cleared, False if no records found
    """
    if ip_address not in rate_limiter.requests:
        return False
    
    if endpoint:
        if endpoint in rate_limiter.requests[ip_address]:
            del rate_limiter.requests[ip_address][endpoint]
            return True
        return False
    else:
        del rate_limiter.requests[ip_address]
        return True


def get_top_requesters(limit: int = 10) -> List[Dict]:
    """
    Get top IP addresses by request count
    
    Args:
        limit: Maximum number of results to return
        
    Returns:
        List of dictionaries with IP and request count
    """
    now = datetime.now()
    ip_counts = {}
    
    for ip, endpoints in rate_limiter.requests.items():
        total = 0
        for endpoint, request_history in endpoints.items():
            # Count all requests (not just in window)
            total += sum(count for _, count in request_history)
        ip_counts[ip] = total
    
    # Sort by count and return top N
    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {"ip_address": ip, "total_requests": count}
        for ip, count in sorted_ips[:limit]
    ]


def get_rate_limit_stats() -> Dict:
    """
    Get overall rate limiting statistics
    
    Returns:
        Dictionary with global statistics
    """
    now = datetime.now()
    
    stats = {
        "total_ips_tracked": len(rate_limiter.requests),
        "total_endpoints_tracked": 0,
        "total_requests_tracked": 0,
        "most_hit_endpoints": {},
    }
    
    endpoint_counts = {}
    
    for ip, endpoints in rate_limiter.requests.items():
        stats["total_endpoints_tracked"] += len(endpoints)
        
        for endpoint, request_history in endpoints.items():
            total = sum(count for _, count in request_history)
            stats["total_requests_tracked"] += total
            
            if endpoint not in endpoint_counts:
                endpoint_counts[endpoint] = 0
            endpoint_counts[endpoint] += total
    
    # Get top 5 most hit endpoints
    sorted_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)
    stats["most_hit_endpoints"] = dict(sorted_endpoints[:5])
    
    return stats


def is_ip_rate_limited(ip_address: str, endpoint: str) -> bool:
    """
    Check if an IP is currently rate limited for a specific endpoint
    
    Args:
        ip_address: IP address to check
        endpoint: Endpoint path to check
        
    Returns:
        True if currently rate limited, False otherwise
    """
    now = datetime.now()
    
    if ip_address not in rate_limiter.requests:
        return False
    
    if endpoint not in rate_limiter.requests[ip_address]:
        return False
    
    max_requests, window_seconds = rate_limiter._get_rate_limit(endpoint)
    window_start = now - timedelta(seconds=window_seconds)
    
    request_history = rate_limiter.requests[ip_address][endpoint]
    recent_requests = [
        (ts, count) for ts, count in request_history
        if ts > window_start
    ]
    total = sum(count for _, count in recent_requests)
    
    return total >= max_requests
