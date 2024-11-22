import logging
import time


class APILoggingMiddleware:
    """
    Middleware for logging API requests and responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("api_logger")

    def __call__(self, request):
        # Capture the start time of the request
        start_time = time.time()

        # Log request details
        self.logger.info(
            f"API Request: {request.method} {request.path} | Body: {request.body.decode('utf-8', 'ignore')}"
        )

        # Get the response
        response = self.get_response(request)

        # Calculate response time
        duration = time.time() - start_time

        # Log response details

        self.logger.info(
            f"API Response: {response.status_code} | Duration: {duration:.3f}s | "
            f"Method: {request.method} | Path: {request.path} | "
            f"Query Params: {request.GET.dict()} | "
            f"User: {getattr(request.user, 'username', 'Anonymous')} | "
            f"IP: {request.META.get('REMOTE_ADDR', '')} | "
            f"Response: {getattr(response, 'content', b'').decode('utf-8', 'ignore')}"
        )

        return response
