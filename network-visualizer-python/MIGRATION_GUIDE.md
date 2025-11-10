# Migration Guide: Cable-style Routing

This guide explains how to migrate from the original Flask-based routing to the new Cable-inspired FastAPI architecture.

## Overview

The new routing structure follows the Cable assistant pattern with:
- **Type-safe operations** using Pydantic models
- **Clean separation of concerns** with dedicated analyzer class
- **Modern FastAPI** with automatic OpenAPI documentation
- **Backward compatibility** through Flask adapter

## Architecture Changes

### Before (Original Flask)
```
web_app.py
├── WebApp class
├── Mixed routing logic
├── Direct NetworkVisualizer usage
└── Manual request/response handling
```

### After (Cable-style)
```
models.py          # Pydantic request/response models
analyzer.py        # NetworkAnalyzer (Cable-style assistant)
fastapi_server.py  # New FastAPI server
flask_adapter.py   # Backward compatibility layer
```

## Key Benefits

1. **Type Safety**: All requests/responses validated with Pydantic
2. **Better Error Handling**: Structured error responses
3. **Auto Documentation**: OpenAPI/Swagger docs at `/docs`
4. **Async Support**: Native async request handling
5. **Validation**: Automatic input validation and serialization

## API Endpoints

### New FastAPI Endpoints (v1)
```
POST /v1/network/load          # Load from file upload
POST /v1/network/load/path     # Load from file path
POST /v1/network/sample        # Load sample network
GET  /v1/samples               # List available samples
POST /v1/network/analyze       # Analyze network
POST /v1/network/visualize     # Generate visualization
GET  /v1/network/stats         # Get statistics
DELETE /v1/network/clear       # Clear network
GET  /v1/network/status        # Get network status
GET  /health                    # Health check
```

### Legacy Flask Endpoints (Still Supported)
```
POST /api/network/load          # Same as before
POST /api/network/analyze       # Same as before
POST /api/network/visualize     # Same as before
GET  /api/network/sample/<name> # Same as before
GET  /api/network/stats         # Same as before
GET  /api/samples               # Same as before
```

## Migration Steps

### 1. Install New Dependencies
```bash
pip install -r requirements-fastapi.txt
```

### 2. Update Your Code

#### Option A: Use New FastAPI Server (Recommended)
```python
from network_visualizer.ui.fastapi_server import start_server

# Start the new server
start_server(host="0.0.0.0", port=8000, debug=True)
```

#### Option B: Keep Flask with New Backend (Backward Compatible)
```python
from network_visualizer.ui.flask_adapter import FlaskWebApp

# Same interface as before, but uses new backend
app = FlaskWebApp(host="localhost", port=5000, debug=True)
app.run()
```

### 3. Update Client Code (If Using New Endpoints)

#### Old Request Format
```javascript
// Legacy endpoint
fetch('/api/network/analyze', {
    method: 'POST',
    body: JSON.stringify({
        metrics: ['degree', 'betweenness']
    })
})
```

#### New Request Format
```javascript
// New endpoint with validation
fetch('/v1/network/analyze', {
    method: 'POST',
    body: JSON.stringify({
        metrics: ['degree', 'betweenness'],
        include_statistics: true
    })
})
```

## Request/Response Models

### Network Analysis
```python
from network_visualizer.ui.models import (
    AnalyzeNetworkRequest,
    CentralityMetric
)

request = AnalyzeNetworkRequest(
    metrics=[CentralityMetric.DEGREE, CentralityMetric.BETWEENNESS],
    include_statistics=True
)
```

### Visualization
```python
from network_visualizer.ui.models import (
    VisualizeNetworkRequest,
    NetworkLayout,
    VisualizationBackend
)

request = VisualizeNetworkRequest(
    layout=NetworkLayout.SPRING,
    backend=VisualizationBackend.PLOTLY,
    show_labels=True
)
```

## Error Handling

### New Structured Errors
```json
{
    "error": {
        "message": "No network loaded",
        "type": "value_error"
    },
    "detail": "No network loaded for analysis"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `422` - Validation Error (Pydantic)
- `500` - Internal Server Error

## Examples

### Load and Analyze a Network
```python
import httpx

# Load sample network
response = httpx.post("http://localhost:8000/v1/network/sample", json={
    "name": "karate_club"
})
network_info = response.json()

# Analyze network
response = httpx.post("http://localhost:8000/v1/network/analyze", json={
    "metrics": ["degree", "betweenness", "eigenvector"],
    "include_statistics": True
})
analysis = response.json()
```

### Generate Visualization
```python
# Generate interactive visualization
response = httpx.post("http://localhost:8000/v1/network/visualize", json={
    "layout": "spring",
    "backend": "plotly",
    "show_labels": True
})
viz_data = response.json()

# Generate static image
response = httpx.post("http://localhost:8000/v1/network/visualize", json={
    "layout": "circular",
    "backend": "matplotlib",
    "show_labels": False
})
image_data = response.json()["image"]  # Base64 encoded
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/test_fastapi_server.py
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Breaking Changes

### None for Legacy Users
If you continue using the Flask adapter (`flask_adapter.py`), there are **no breaking changes**. All existing endpoints work exactly as before.

### For New FastAPI Users
- Endpoint paths changed from `/api/*` to `/v1/*`
- Request/response format is stricter (Pydantic validation)
- Error responses have new structure

## Troubleshooting

### Import Errors
```python
# Make sure to import from the correct module
from network_visualizer.ui.fastapi_server import start_server  # New
# from network_visualizer.ui.web_app import WebApp  # Old (still works)
```

### Validation Errors
Check the Pydantic models in `models.py` for required fields and valid values.

### Performance
The new FastAPI server is generally faster due to async support, but you may need to adjust uvicorn settings for production.

## Next Steps

1. **Try the new server**: `python -m network_visualizer.ui.fastapi_server`
2. **Explore the docs**: Visit http://localhost:8000/docs
3. **Update clients**: Use the new v1 endpoints for type safety
4. **Migrate gradually**: Use Flask adapter during transition
