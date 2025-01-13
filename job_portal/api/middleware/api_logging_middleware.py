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

        # Attach custom fields for structured logging
        request_data = {
            "request_method": request.method,
            "request_path": request.path,
            "request_body": request.body.decode("utf-8", "ignore"),
        }

        # Log request details as structured data
        self.logger.info("API Request", extra=request_data)

        # Get the response
        response = self.get_response(request)

        # Calculate response time
        duration = time.time() - start_time

        self.logger.info(
            f"API Response: {response.status_code} | Duration: {duration:.3f}s | "
            f"Method: {request.method} | Path: {request.path} | "
            f"Query Params: {request.GET.dict()} | "
            f"User: {getattr(request.user, 'username', 'Anonymous')} | "
            f"IP: {request.META.get('REMOTE_ADDR', '')} | "
            f"Response: {getattr(response, 'content', b'').decode('utf-8', 'ignore')}"
        )

        # Attach custom fields for structured logging
        response_data = {
            "response_status_code": response.status_code,
            "duration": duration,
            "user": getattr(request.user, "username", "Anonymous"),
            "ip": request.META.get("REMOTE_ADDR", ""),
            "response_content": getattr(response, "content", b"").decode(
                "utf-8", "ignore"
            ),
        }

        # Log response details as structured data
        self.logger.info("API Response", extra=response_data)

        return response
