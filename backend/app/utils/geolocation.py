"""
Geolocation utility
Converts IP addresses to geographic locations
"""

import httpx
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


async def get_location_from_ip(ip_address: str) -> str:
    """
    Get geographic location from IP address
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Location string (e.g., "Paris, France" or "IP: 1.2.3.4" if lookup fails)
    """
    # Skip localhost/private IPs
    if ip_address in ['Unknown', '127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return f'Local Network (IP: {ip_address})'
    
    try:
        # Use ip-api.com (free, no API key required, 45 requests/minute)
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f'http://ip-api.com/json/{ip_address}',
                params={'fields': 'status,country,city,query'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    city = data.get('city', '')
                    country = data.get('country', '')
                    
                    if city and country:
                        return f'{city}, {country}'
                    elif country:
                        return country
                    else:
                        return f'IP: {ip_address}'
                else:
                    logger.warning(f"IP geolocation failed for {ip_address}: {data.get('message', 'Unknown error')}")
                    return f'IP: {ip_address}'
            else:
                logger.warning(f"IP geolocation API returned status {response.status_code}")
                return f'IP: {ip_address}'
                
    except httpx.TimeoutException:
        logger.warning(f"IP geolocation timeout for {ip_address}")
        return f'IP: {ip_address}'
    except Exception as e:
        logger.error(f"Failed to get location for IP {ip_address}: {str(e)}")
        return f'IP: {ip_address}'


async def get_location_details(ip_address: str) -> Dict[str, str]:
    """
    Get detailed location information from IP address
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Dictionary with location details (city, country, region, etc.)
    """
    # Skip localhost/private IPs
    if ip_address in ['Unknown', '127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return {
            'city': 'Local Network',
            'country': 'Local',
            'region': '',
            'ip': ip_address
        }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f'http://ip-api.com/json/{ip_address}',
                params={'fields': 'status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,query'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    return {
                        'city': data.get('city', ''),
                        'country': data.get('country', ''),
                        'region': data.get('regionName', ''),
                        'ip': data.get('query', ip_address),
                        'timezone': data.get('timezone', ''),
                        'isp': data.get('isp', '')
                    }
                else:
                    return {
                        'city': '',
                        'country': '',
                        'region': '',
                        'ip': ip_address
                    }
            else:
                return {
                    'city': '',
                    'country': '',
                    'region': '',
                    'ip': ip_address
                }
                
    except Exception as e:
        logger.error(f"Failed to get location details for IP {ip_address}: {str(e)}")
        return {
            'city': '',
            'country': '',
            'region': '',
            'ip': ip_address
        }
