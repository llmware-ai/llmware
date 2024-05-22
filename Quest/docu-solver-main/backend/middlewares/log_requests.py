import time
from starlette.middleware.base import BaseHTTPMiddleware

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        formatted_process_time = '{0:.2f}'.format(process_time * 1000)
        print(f"{request.method} {request.url} completed in {formatted_process_time}ms")
        return response
