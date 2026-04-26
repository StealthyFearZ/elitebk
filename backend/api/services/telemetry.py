import time
import functools
from api.models import ChatTelemetry
import logging

logger = logging.getLogger(__name__)

def track_chat_performance(endpoint_name="Chat Process"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            is_success = True
            error_message = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                is_success = False
                error_message = str(e)
                logger.error(f'Chatbot failed at {endpoint_name}: {error_message}')
                raise e
            finally:
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000

                # get user involved if possible
                request = args[1] if len(args) > 1 and hasattr(args[1], 'user') else None
                user = request.user if request and request.user.is_authenticated else None

                ChatTelemetry.objects.create(
                    user=user,
                    endpoint=endpoint_name,
                    latency_ms=latency_ms,
                    is_success=is_success,
                    error_message=error_message
                )
        return wrapper
    return decorator