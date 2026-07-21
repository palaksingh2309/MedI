import time
import logging
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse

# Setup logger for prediction service
logger = logging.getLogger('prediction')

def get_client_ip(request):
    """
    Utility to fetch client IP address from request metadata.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def rate_limit(key_prefix="prediction_api", limit=60, period=60):
    """
    Custom Django API rate limiter decorator using cache.
    - limit: maximum number of requests allowed in the period.
    - period: time window in seconds.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Identify caller by user ID if logged in, otherwise client IP
            if request.user.is_authenticated:
                identifier = f"{key_prefix}_user_{request.user.id}"
            else:
                identifier = f"{key_prefix}_ip_{get_client_ip(request)}"

            current_count = cache.get(identifier, 0)

            if current_count >= limit:
                logger.warning(f"Rate limit exceeded for {identifier}. Current count: {current_count}")
                return JsonResponse(
                    {"error": "Too many requests. Please try again later."},
                    status=429
                )

            # Increment count
            cache.set(identifier, current_count + 1, period)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def log_prediction(user, disease, confidence, latency_ms):
    """
    Structured logger to record disease predictions, user information, and service latency.
    """
    username = user.username if (user and user.is_authenticated) else "Anonymous"
    logger.info(
        f"PREDICTION_LOG | User: {username} | Disease: {disease} | "
        f"Confidence: {confidence:.2f}% | Latency: {latency_ms:.2f}ms"
    )
