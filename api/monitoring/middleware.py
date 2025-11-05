"""Monitoring and observability components."""

import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect metrics for each request."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Initialize metrics
        method = request.method
        path = request.url.path
        
        try:
            # Process the request and capture response
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            status_code = response.status_code
            
            # Log request details
            logger.info(
                f"Request: {method} {path} - Status: {status_code} - Duration: {duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Log errors
            logger.error(f"Error processing request: {method} {path} - {str(e)}")
            raise

class TracingMiddleware(BaseHTTPMiddleware):
    """OpenTelemetry tracing middleware."""
    
    async def dispatch(self, request: Request, call_next):
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            try:
                # Add request details to span
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.route", request.url.path)
                
                # Process request
                response = await call_next(request)
                
                # Add response details
                span.set_attribute("http.status_code", response.status_code)
                span.set_status(Status(StatusCode.OK))
                
                return response
                
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise

def setup_monitoring(app):
    """Configure monitoring middleware and tools."""
    
    # Add metrics collection
    app.add_middleware(MetricsMiddleware)
    
    # Add distributed tracing
    app.add_middleware(TracingMiddleware)
    
    # Add any additional monitoring setup
    # e.g., Prometheus metrics endpoint, health checks, etc.