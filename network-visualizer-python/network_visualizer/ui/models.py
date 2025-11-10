"""
Pydantic models for Network Visualizer API

Provides type-safe request/response validation following the Cable concept.
"""
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, HttpUrl


class NetworkLayout(str, Enum):
    """Available network layout algorithms."""
    SPRING = "spring"
    CIRCULAR = "circular"
    RANDOM = "random"
    SHELL = "shell"
    KAMADA_KAWAI = "kamada_kawai"


class VisualizationBackend(str, Enum):
    """Available visualization backends."""
    PLOTLY = "plotly"
    MATPLOTLIB = "matplotlib"
    NETWORKX = "networkx"


class CentralityMetric(str, Enum):
    """Available centrality metrics."""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"


class NetworkNode(BaseModel):
    """Represents a network node."""
    id: str
    x: float
    y: float
    degree: int
    label: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None


class NetworkEdge(BaseModel):
    """Represents a network edge."""
    source: str
    target: str
    x0: float
    y0: float
    x1: float
    y1: float
    weight: Optional[float] = None


class NetworkStatistics(BaseModel):
    """Network statistics."""
    num_nodes: int = Field(..., alias="nodes")
    num_edges: int = Field(..., alias="edges")
    density: float
    average_degree: Optional[float] = None
    is_connected: Optional[bool] = None
    num_components: Optional[int] = None


class CentralityScores(BaseModel):
    """Centrality scores for nodes."""
    metric: str
    scores: Dict[str, float]


class NetworkInfo(BaseModel):
    """Basic network information."""
    nodes: int
    edges: int
    density: float
    filename: Optional[str] = None
    name: Optional[str] = None


class NetworkVisualization(BaseModel):
    """Network visualization data."""
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    layout: NetworkLayout
    backend: VisualizationBackend


# Request Models
class LoadNetworkRequest(BaseModel):
    """Request to load a network from file."""
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    file_type: Optional[str] = None


class AnalyzeNetworkRequest(BaseModel):
    """Request to analyze a network."""
    metrics: List[CentralityMetric] = Field(
        default=[CentralityMetric.DEGREE, CentralityMetric.BETWEENNESS, CentralityMetric.CLOSENESS]
    )
    include_statistics: bool = True


class VisualizeNetworkRequest(BaseModel):
    """Request to generate network visualization."""
    layout: NetworkLayout = NetworkLayout.SPRING
    backend: VisualizationBackend = VisualizationBackend.PLOTLY
    show_labels: bool = False
    node_size_metric: Optional[CentralityMetric] = None
    edge_width_metric: Optional[str] = None


class SampleNetworkRequest(BaseModel):
    """Request to load a sample network."""
    name: Literal[
        "karate_club", "davis_southern_women", "florentine_families",
        "les_miserables", "football"
    ]


# Response Models
class APIResponse(BaseModel):
    """Base API response."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class LoadNetworkResponse(APIResponse):
    """Response for network loading."""
    network_info: Optional[NetworkInfo] = None


class AnalyzeNetworkResponse(APIResponse):
    """Response for network analysis."""
    analysis: Optional[Dict[str, Any]] = None
    statistics: Optional[NetworkStatistics] = None
    centrality: Optional[List[CentralityScores]] = None


class VisualizeNetworkResponse(APIResponse):
    """Response for network visualization."""
    visualization: Optional[NetworkVisualization] = None
    image: Optional[str] = None  # Base64 encoded image


class SampleNetworkResponse(APIResponse):
    """Response for sample network loading."""
    network_info: Optional[NetworkInfo] = None


class SamplesListResponse(APIResponse):
    """Response for available samples list."""
    samples: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    service: str = "network-visualizer"
    version: str = "2.0.0"


# Error Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: Dict[str, Any]
    detail: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error details."""
    field: str
    message: str
    value: Any
