# Atmosphere Codebase Audit

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Name** | `atmosphere-audio` |
| **Version** | 0.1.1 (core), 2.0.0 (Arcade) |
| **Language** | Python 3.8+ |
| **Build** | setuptools via `pyproject.toml` |
| **License** | MIT |
| **Dependencies** | numpy, scipy, fastapi, uvicorn, pydantic, requests |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                       │
│  Arcade TUI  │  Arcade WebSocket  │  CLI  │  REST API       │
├─────────────────────────────────────────────────────────────┤
│                  ORCHESTRATION LAYER                          │
│  ReverbPlatform  │  EchoesPlatform  │  AcousticRoutingNetwork│
├─────────────────────────────────────────────────────────────┤
│                    SERVICES LAYER                             │
│  DelayService  │  EchoService  │  ReverbService  │  Spatial  │
├─────────────────────────────────────────────────────────────┤
│                    MODELS LAYER                               │
│  AudioSignal  │  EffectParameters hierarchy  │  Dataclasses  │
├─────────────────────────────────────────────────────────────┤
│              INFRASTRUCTURE / CROSS-CUTTING                   │
│  Security  │  NetworkPresence  │  Metrics  │  Pipeline       │
└─────────────────────────────────────────────────────────────┘
```

### Effects Chain (core audio path)

```
Mono Input → DelayService → EchoService → ReverbService → SpatialAudioService → Stereo Output
```

Implemented in `src/reverb/core/platform.py:52` (`ReverbPlatform.process_signal`).

---

## 3. Module Map

### 3.1 Core Audio Modules (`src/`)

| Module | Path | Entry | Purpose |
|--------|------|-------|---------|
| **delay** | `src/delay/` | `core/delay_essence.py` | Time-based effects, tempo-sync, emotion modulation |
| **echo** | `src/echo/` | `core/core.py` | Signal reflection, OpenAI-integrated assistant (EchoesAssistantV2) |
| **reverb** | `src/reverb/` | `core/platform.py` | Spatial reverb with Schroeder filters, HRTF, Doppler |
| **routing** | `src/routing/` | `acoustic_routing/core/network.py` | Graph-based acoustic network topology |
| **atmosphere_audio** | `src/atmosphere_audio/` | `__init__.py` | Unified facade for all audio sub-modules |
| **security** | `src/security/` | `__init__.py` | Auth, JWT, API keys, audit logging |

### 3.2 Application Modules (top-level)

| Module | Path | Entry | Purpose |
|--------|------|-------|---------|
| **Arcade** | `Arcade/` | `enhanced_launcher.py` | AI terminal, TUI, learning companion, games |
| **Routing** | `Routing/` | `acoustic_routing.py` | 3D routing, circuit breaker, emotion-enhanced routing |
| **Delay** | `Delay/` | `__main__.py` | High-level delay module with auth |
| **Reverb** | `Reverb/` | `__main__.py` | High-level reverb demos |
| **api** | `api/` | `main.py` | FastAPI server, OpenAI chat endpoints |
| **i_o** | `i_o/` | `main.py` | Research platform, `!contact` protocol |
| **Routing/Cable** | `Routing/Cable/` | `main.py` | OpenAI search integration |

### 3.3 Supporting Systems

| Module | Path | Purpose |
|--------|------|---------|
| **mental-load-balancer** | `mental-load-balancer/` | Cognitive load metrics, joke engine |
| **network-visualizer-python** | `network-visualizer-python/` | Graph visualization, community detection |
| **automation** | `automation/` | DevOps, PowerShell modules |
| **ecosystem** | `ecosystem/` | Meta-integration module |

---

## 4. Code Patterns Catalog

### 4.1 Data Modeling — `@dataclass` with serialization

```python
@dataclass
class AudioSignal:
    data: List[List[float]]
    sample_rate: int = 44100
    channels: int = 1
    duration: Optional[float] = None

    def to_dict(self) -> dict: ...
    @staticmethod
    def from_dict(data: dict) -> "AudioSignal": ...
    @classmethod
    def create_mono(cls, data, sample_rate=44100) -> "AudioSignal": ...
```

**Where**: `src/reverb/models/signal.py`, `src/security/__init__.py`, `src/echo/models/items.py`

**Convention**:
- All models use `@dataclass` (not Pydantic `BaseModel`, except in network-visualizer)
- Serialization via `to_dict()` / `from_dict()` static methods
- Factory class methods (`create_mono`, `create_stereo`)
- Post-init validation via `__post_init__`

### 4.2 Parameter Hierarchy — Inheritance with defaults

```python
@dataclass
class EffectParameters:            # base
    enabled: bool = True
    wet_dry_mix: float = 0.5

@dataclass
class DelayParameters(EffectParameters):
    time_ms: float = 250.0
    feedback: float = 0.3

@dataclass
class ReverbParameters(EffectParameters):
    rt60: float = 1.0
    damping: float = 0.5
```

**Where**: `src/reverb/models/signal.py:56-119`

### 4.3 Service Pattern — Constructor + process() + get_status()

```python
class XService:
    def __init__(self, default_params: XParameters = None):
        self.default_params = default_params or XParameters()

    def process(self, signal: AudioSignal, params=None) -> AudioSignal:
        params = params or self.default_params
        # ... processing

    def get_status(self) -> dict:
        return {"name": "...", "enabled": self.default_params.enabled}
```

**Where**: `src/reverb/services/delay_service.py`, `echo_service.py`, `reverb_service.py`, `spatial_service.py`

### 4.4 Platform/Orchestrator Pattern — Compose services into a chain

```python
class ReverbPlatform:
    def __init__(self, delay_params=None, echo_params=None, ...):
        self.delay_service = DelayService(delay_params)
        self.echo_service = EchoService(echo_params)
        ...

    def process_signal(self, signal):
        delayed = self.delay_service.process(signal)
        echoed = self.echo_service.process(delayed)
        ...
```

**Where**: `src/reverb/core/platform.py:18`

### 4.5 Protocol (structural typing)

```python
class AudioNode(Protocol):
    def process(self, buffer: np.ndarray, context: ProcessingContext) -> np.ndarray: ...
```

**Where**: `src/atmosphere_audio/pipeline/nodes.py:14`

### 4.6 Result/Error Pattern

```python
@dataclass
class ToolResult:
    success: bool
    result: Any
    error: str | None = None
    execution_time: float | None = None
```

**Where**: `src/echo/models/items.py`

### 4.7 Circuit Breaker / Resilience

```python
class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitBreaker:
    def __init__(self, name, failure_threshold=5, recovery_timeout=30.0):
        self._state = CircuitState.CLOSED
        self._metrics = CircuitBreakerMetrics()
```

**Where**: `Routing/circuit_breaker.py`

### 4.8 Manager/Singleton Pattern

```python
# Module-level singletons
user_manager = UserManager()
jwt_manager = JWTManager()
api_key_manager = APIKeyManager()
security_logger = SecurityLogger()
```

**Where**: `src/security/__init__.py`

### 4.9 FastAPI App Factory

```python
def create_app() -> FastAPI:
    app = FastAPI(title="...", version="...")
    app.add_middleware(CORSMiddleware, ...)
    setup_monitoring(app)
    app.include_router(router)
    return app
```

**Where**: `api/main.py`

### 4.10 Async Middleware (BaseHTTPMiddleware)

```python
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        return response
```

**Where**: `api/monitoring/middleware.py`

### 4.11 Network Presence (UDP discovery)

```python
class NetworkPresence:
    def __init__(self, device_id, broadcast_port=37020, presence_interval=30):
        self.known_devices: Dict[str, DeviceInfo] = {}
        self._lock = threading.Lock()

    def start(self):
        self._announce_thread = threading.Thread(target=..., daemon=True)
        self._listen_thread = threading.Thread(target=..., daemon=True)
```

**Where**: `src/atmosphere_audio/core/network.py`

### 4.12 File-System Event Dispatch

```python
class DispatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        tool_name = self._extract_tool_name(file_path)
        zone_name = self.routing.get(tool_name)
        self._dispatch_to_zone(tool_name, file_path, zone_name)
```

**Where**: `Arcade/dispatcher.py`

### 4.13 YAML-Driven Routing

```yaml
audio_tool: audio
visual_tool: visual
games_tool: games
network_visualizer: visual
```

**Where**: `Arcade/config/routing.yaml`

---

## 5. Configuration Hierarchy

```
Environment Variables (.env)
    ↓ overrides
YAML configs (routing.yaml, privacy_safety.yaml, tools.yaml)
    ↓ overrides
Python dataclass defaults (DelayParameters, SecurityConfig, etc.)
    ↓ overrides
Runtime parameters passed to process() / constructors
```

---

## 6. Initialization / Boot Sequence

### Root entry (`python -m atmosphere`)
1. `__main__.py` → `authenticate_user()` via `src/security/user_manager`
2. On success → `main()` function

### Arcade entry (`python -m Arcade`)
1. `Arcade/__main__.py` → `enhanced_launcher.main()`
2. FastAPI server starts with WebSocket terminal
3. Learning companion API loaded
4. Tool dispatcher watches filesystem for incoming tools

### Audio processing (`src/atmosphere_audio`)
1. Package import triggers `logging.NullHandler()` setup
2. Sub-modules (`delay`, `echo`, `reverb`, `routing`, `core`) imported
3. `ReverbPlatform` instantiated with optional parameter overrides
4. `process_signal()` runs the 4-stage effects chain

### API server (`api/`)
1. `create_app()` factory builds FastAPI instance
2. CORS, monitoring, and security middleware attached
3. Routes registered (`/chat`, `/health`, `/models`)
4. Uvicorn serves the app

---

## 7. Testing Architecture

| Config | Value |
|--------|-------|
| **Framework** | pytest >= 7.0 |
| **Test paths** | `tests/`, `Delay/`, `i_o/`, `mental-load-balancer/` |
| **Markers** | `slow`, `integration`, `unit`, `smoke`, `e2e` |
| **Coverage source** | `src`, `Delay`, `i_o`, `mental-load-balancer` |
| **Min coverage** | 50% (pyproject.toml), 80% (CI) |
| **Reports** | term-missing, html:htmlcov, xml |
| **CI** | GitHub Actions, Python 3.10, black + isort + flake8 + mypy |

---

## 8. Safety & Governance

From `Arcade/config/privacy_safety.yaml`:

- **Differential privacy**: epsilon=1.0 per session, delta=1e-5
- **Data minimization**: 24h retention, aggregates only
- **Consent**: per-session granularity, daily refresh, partial withdrawal supported
- **Minors (COPPA)**: guardian consent required, 6h max retention
- **Human oversight**: required when risk_score > 0.75
- **Ethical constraints**: manipulation detection, max 10 interventions/hour, incompatible intervention pair blocking
- **Bias monitoring**: 80% rule, auto-disable on bias detection
- **Audit**: append-only, SHA256 signed, 7-year retention
- **Emergency kill switch**: hardware GPIO, dual-signoff reboot

---

## 9. Key File Reference

### Core Implementations
- `src/reverb/core/platform.py` — Effects chain orchestrator
- `src/reverb/models/signal.py` — AudioSignal + parameter hierarchy
- `src/reverb/services/reverb_service.py` — Schroeder reverb (CombFilter, AllPassFilter)
- `src/reverb/services/spatial_service.py` — HRTF, Doppler, binaural
- `src/delay/core/delay_essence.py` — Delay engine with emotion modulation
- `src/echo/core/core.py` — EchoesAssistantV2 (1738 lines, OpenAI integration)
- `src/routing/acoustic_routing/core/network.py` — Graph routing
- `src/atmosphere_audio/pipeline/nodes.py` — AudioNode protocol + ProcessingContext

### Security
- `src/security/__init__.py` — UserManager, JWTManager, APIKeyManager, SecurityLogger
- `src/atmosphere_audio/core/security.py` — Security middleware (23KB)
- `Arcade/api/security.py` — Arcade API security

### Configuration
- `pyproject.toml` — Build, test, coverage config
- `Arcade/config/routing.yaml` — Tool-to-zone dispatch map
- `Arcade/config/tools.yaml` — Tool definitions
- `Arcade/config/privacy_safety.yaml` — Privacy/safety governance

### API Servers
- `api/main.py` — Root API server (FastAPI factory)
- `Arcade/api/server.py` — Arcade FastAPI server
- `i_o/main.py` — Research platform server
- `Routing/Cable/src/api.py` — Cable search API (Flask)

---

## 10. Synthesized Patterns for Custom Skills & Workflows

### Pattern: New Audio Service
```
1. Define parameters as @dataclass inheriting EffectParameters  (models/signal.py)
2. Create XService class with __init__(default_params), process(signal, params), get_status()
3. Register in ReverbPlatform constructor and chain
4. Add API endpoint if needed
```

### Pattern: New Tool for Arcade
```
1. Create tool module in Arcade/tools/
2. Add routing entry in Arcade/config/routing.yaml  (tool_name: zone)
3. Add tool definition in Arcade/config/tools.yaml
4. Dispatcher auto-discovers via filesystem events
```

### Pattern: New API Endpoint
```
1. Define route in appropriate router module
2. Apply security middleware (JWT or API key)
3. Add monitoring via MetricsMiddleware
4. Include in app factory's include_router()
```

### Pattern: New Data Model
```
1. Create @dataclass with typed fields and defaults
2. Add to_dict() and from_dict() methods
3. Add factory classmethods for common construction
4. Add __post_init__ validation if needed
```

### Pattern: New Integration Module
```
1. Create package with core/, api/, models/ subdirectories
2. Export public API in __init__.py via __all__
3. Add tests in module's test directory
4. Update pyproject.toml testpaths and coverage source
```

### Execution Workflow: Full Audio Pipeline
```
1. Instantiate ReverbPlatform(delay_params, echo_params, reverb_params, spatial_params)
2. Create AudioSignal via AudioSignal.create_mono(data) or create_stereo(left, right)
3. Call platform.process_signal(signal) for default chain
4. Or platform.process_with_custom_params(signal, ...) for overrides
5. Or platform.process_with_preset(signal, "hall") for presets
```

### Execution Workflow: Arcade Tool Dispatch
```
1. File lands in Arcade/incoming/
2. DispatcherHandler.on_created() fires
3. Tool name extracted from filename
4. routing.yaml consulted for zone mapping
5. Tool dispatched to zone handler
```

### Instructional Rules
```
- All models use @dataclass, not Pydantic BaseModel (except network-visualizer)
- Serialization is always to_dict/from_dict, not .json()/.parse()
- Services expose process() + get_status()
- Platforms compose services into ordered chains
- Threading uses daemon threads + threading.Lock()
- Async code uses asyncio.Lock() + BaseHTTPMiddleware
- Config flows: env → YAML → dataclass defaults → runtime params
- Tests use pytest markers (unit, integration, smoke, e2e, slow)
- Security singletons are module-level, imported directly
- Logging uses logging.getLogger(__name__) + NullHandler at package level
```
