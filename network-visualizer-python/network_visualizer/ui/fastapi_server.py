"""
Network Visualizer FastAPI Server

A FastAPI server providing HTTP endpoints for network visualization and analysis.
Follows the Cable assistant pattern with clean routing and type-safe operations.
"""
import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .analyzer import NetworkAnalyzer
from .models import (
    LoadNetworkRequest, AnalyzeNetworkRequest, VisualizeNetworkRequest,
    SampleNetworkRequest, LoadNetworkResponse, AnalyzeNetworkResponse,
    VisualizeNetworkResponse, SampleNetworkResponse, SamplesListResponse,
    HealthResponse, ErrorResponse
)


# Initialize FastAPI app
app = FastAPI(
    title="Network Visualizer API",
    description="API for Network Analysis and Visualization - Cable-style architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the analyzer
def get_analyzer() -> NetworkAnalyzer:
    """Get NetworkAnalyzer instance."""
    return NetworkAnalyzer()


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and responses."""
    print(f"📡 Incoming: {request.method} {request.url}")
    response = await call_next(request)
    print(f"📤 Response: {response.status_code}")
    return response


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Network Visualizer API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Network loading endpoints
@app.post("/v1/network/load", response_model=LoadNetworkResponse)
async def load_network_from_file(
    file: UploadFile = File(...),
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Load network from uploaded file."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        file_type = Path(file.filename).suffix.lstrip('.')
        
        # Create request
        request = LoadNetworkRequest(
            file_type=file_type if file_type else None
        )
        
        # Load network
        network_info = analyzer.load_network(request, file_content)
        
        return LoadNetworkResponse(
            success=True,
            message=f"Network loaded successfully from {file.filename}",
            network_info=network_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/network/load/path", response_model=LoadNetworkResponse)
async def load_network_from_path(
    request: LoadNetworkRequest,
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Load network from file path."""
    try:
        if not request.file_path:
            raise HTTPException(status_code=400, detail="File path is required")
        
        network_info = analyzer.load_network(request)
        
        return LoadNetworkResponse(
            success=True,
            message=f"Network loaded successfully from {request.file_path}",
            network_info=network_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Sample network endpoints
@app.post("/v1/network/sample", response_model=SampleNetworkResponse)
async def load_sample_network(
    request: SampleNetworkRequest,
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Load a sample network."""
    try:
        network_info = analyzer.load_sample_network(request)
        
        return SampleNetworkResponse(
            success=True,
            message=f"Sample network '{request.name}' loaded successfully",
            network_info=network_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/samples", response_model=SamplesListResponse)
async def get_available_samples(
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Get list of available sample networks."""
    try:
        samples = analyzer.get_available_samples()
        
        return SamplesListResponse(
            success=True,
            samples=samples
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analysis endpoints
@app.post("/v1/network/analyze", response_model=AnalyzeNetworkResponse)
async def analyze_network(
    request: AnalyzeNetworkRequest,
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Analyze current network."""
    try:
        if not analyzer.has_network():
            raise HTTPException(status_code=400, detail="No network loaded")
        
        analysis = analyzer.analyze_network(request)
        
        return AnalyzeNetworkResponse(
            success=True,
            message="Network analysis completed",
            **analysis
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/network/stats")
async def get_network_statistics(
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Get current network statistics."""
    try:
        if not analyzer.has_network():
            raise HTTPException(status_code=400, detail="No network loaded")
        
        stats = analyzer.get_network_statistics()
        
        return {
            "success": True,
            "statistics": stats.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Visualization endpoints
@app.post("/v1/network/visualize", response_model=VisualizeNetworkResponse)
async def generate_visualization(
    request: VisualizeNetworkRequest,
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Generate network visualization."""
    try:
        if not analyzer.has_network():
            raise HTTPException(status_code=400, detail="No network loaded")
        
        if request.backend.value == "plotly":
            # Return interactive visualization data
            visualization = analyzer.generate_visualization(request)
            
            return VisualizeNetworkResponse(
                success=True,
                message="Interactive visualization generated",
                visualization=visualization
            )
        else:
            # Generate static image
            image_data = analyzer.generate_static_image(request)
            
            return VisualizeNetworkResponse(
                success=True,
                message="Static visualization generated",
                image=image_data
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@app.delete("/v1/network/clear")
async def clear_network(
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Clear current network."""
    try:
        analyzer.clear_network()
        
        return {
            "success": True,
            "message": "Network cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/network/status")
async def get_network_status(
    analyzer: NetworkAnalyzer = Depends(get_analyzer)
):
    """Get current network status."""
    try:
        has_network = analyzer.has_network()
        
        status = {
            "has_network": has_network,
            "network_loaded": bool(analyzer.current_network)
        }
        
        if has_network and analyzer.current_network:
            status.update({
                "nodes": len(analyzer.current_network.nodes),
                "edges": len(analyzer.current_network.edges),
                "has_layout": analyzer.current_layout is not None,
                "has_analysis": analyzer.current_analysis is not None
            })
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error={"message": exc.detail, "type": "http_error"},
            detail=exc.detail
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error={"message": str(exc), "type": "value_error"},
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error={"message": "Internal server error", "type": "server_error"},
            detail=str(exc) if os.getenv("DEBUG") else None
        ).dict()
    )


def start_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Start the FastAPI server.
    
    Args:
        host: Server host address
        port: Server port
        debug: Enable debug mode
    """
    print(f"🚀 Starting Network Visualizer API Server (Cable-style)")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print(f"💚 Health: http://{host}:{port}/health")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        reload=debug,
        log_level="debug" if debug else "info"
    )


if __name__ == "__main__":
    start_server(debug=True)
