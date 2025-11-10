"""
FastAPI WebSocket Server for Arcade Terminal
Main server for web-based terminal access.
"""

import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

try:
    from .terminal_handler import TerminalHandler
    from .security import SecurityManager
    from .game_engine import GameEngine
    from .routing_integration import RoutingIntegration
    from .tool_integration import ToolIntegration
    from .learning_companion_api import router as learning_router
except ImportError:
    # For direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from terminal_handler import TerminalHandler
    from security import SecurityManager
    from game_engine import GameEngine
    from routing_integration import RoutingIntegration
    from tool_integration import ToolIntegration
    from learning_companion_api import router as learning_router

logger = logging.getLogger(__name__)

# Initialize components
security_manager = SecurityManager()
terminal_handler = TerminalHandler(
    sandbox_root=Path(__file__).parent.parent / "sandbox" / "virtual_fs",
    security_manager=security_manager
)
routing_integration = RoutingIntegration()
game_engine = GameEngine(routing_integration=routing_integration)
tool_integration = ToolIntegration()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting Arcade Terminal server...")

    # Initialize routing integration
    try:
        await routing_integration.initialize()
        logger.info("Routing integration initialized")
    except Exception as e:
        logger.warning(f"Routing integration not available: {e}")

    # Create sandbox directories
    sandbox_root = Path(__file__).parent.parent / "sandbox" / "virtual_fs"
    sandbox_root.mkdir(parents=True, exist_ok=True)

    logger.info("Arcade Terminal server started")
    yield
    # Shutdown
    logger.info("Shutting down Arcade Terminal server...")

    # Terminate all active sessions
    for session_id in list(terminal_handler.sessions.keys()):
        terminal_handler.terminate_session(session_id)

    # Close all WebSocket connections
    for connection in active_connections.values():
        try:
            await connection.close()
        except Exception:
            pass

    logger.info("Arcade Terminal server shutdown complete")

app = FastAPI(
    title="Arcade Terminal",
    description="Retro-style terminal entertainment space with emotionally-adaptive learning",
    version="1.0.0",
    lifespan=lifespan
)

# Include learning companion API
app.include_router(learning_router)

# Mount static files
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    return app


@app.get("/")
async def root():
    """Serve main arcade page"""
    index_file = web_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("""
    <html>
        <head><title>Arcade Terminal</title></head>
        <body>
            <h1>Arcade Terminal</h1>
            <p>Web interface not found. Please ensure web/index.html exists.</p>
        </body>
    </html>
    """)


@app.get("/arcade/status")
async def get_status():
    """Get server status"""
    return {
        "status": "running",
        "active_sessions": len(terminal_handler.sessions),
        "active_connections": len(active_connections),
        "routing": routing_integration.get_routing_status()
    }


@app.websocket("/arcade/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for terminal communication"""
    await websocket.accept()
    
    # Create session
    session_id = str(uuid.uuid4())
    active_connections[session_id] = websocket
    
    # Create terminal session
    try:
        terminal_session = terminal_handler.create_session(
            session_id=session_id,
            initial_directory=Path(__file__).parent.parent / "sandbox" / "virtual_fs"
        )
        
        # Create game session
        game_session = game_engine.create_session(session_id)
        
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Welcome to the Arcade Terminal! Type 'help' for commands.",
            "session_id": session_id,
            "location": game_session.current_location
        }
        await websocket.send_json(welcome_msg)
        
        logger.info(f"WebSocket connection established: {session_id}")
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get("type")
                
                if msg_type == "command":
                    # Handle command
                    command = message.get("command", "")
                    
                    # Check if it's a tool command
                    tool_cmd = tool_integration.parse_tool_command(command)
                    if tool_cmd:
                        # Execute tool with streaming output
                        async def stream_output(line: str):
                            await websocket.send_json({
                                "type": "tool_output",
                                "line": line,
                                "tool": tool_cmd['tool_name']
                            })
                        
                        result = await tool_integration.execute_tool(
                            tool_cmd['tool_name'],
                            tool_cmd['args'],
                            output_callback=stream_output
                        )
                        
                        await websocket.send_json({
                            "type": "tool_complete",
                            "tool": tool_cmd['tool_name'],
                            "result": result
                        })
                        continue
                    
                    # Check if it's a game command
                    game_result = game_engine.process_navigation_command(session_id, command)
                    
                    if game_result.get("success"):
                        # Send game response
                        await websocket.send_json({
                            "type": "game_response",
                            "result": game_result
                        })
                    
                    # Also execute in terminal (if command is allowed)
                    is_allowed, reason = security_manager.validate_command(command)
                    if is_allowed:
                        try:
                            stdout, stderr, return_code = terminal_handler.execute_command(
                                session_id,
                                command,
                                timeout=10.0
                            )
                            
                            # Send terminal output
                            await websocket.send_json({
                                "type": "terminal_output",
                                "stdout": stdout,
                                "stderr": stderr,
                                "return_code": return_code
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Command execution error: {e}"
                            })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": reason or "Command not allowed"
                        })
                
                elif msg_type == "resize":
                    # Handle terminal resize
                    cols = message.get("cols", 80)
                    rows = message.get("rows", 24)
                    # Terminal resize handling would go here
                    await websocket.send_json({
                        "type": "resize_ack",
                        "cols": cols,
                        "rows": rows
                    })
                
                elif msg_type == "ping":
                    # Heartbeat
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "get_status":
                    # Get game/terminal status
                    game_state = game_engine.get_game_state(session_id)
                    terminal_info = terminal_handler.get_session_info(session_id)
                    
                    await websocket.send_json({
                        "type": "status",
                        "game": game_state,
                        "terminal": terminal_info
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}"
                    })
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Server error: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
    finally:
        # Cleanup
        if session_id in active_connections:
            del active_connections[session_id]
        
        terminal_handler.terminate_session(session_id)
        game_engine.end_session(session_id)
        
        logger.info(f"Session cleaned up: {session_id}")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=7681,
        log_level="info",
        reload=True
    )

