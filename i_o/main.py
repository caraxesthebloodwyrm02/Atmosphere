#!/usr/bin/env python3
"""
i_o Research Platform Server
===========================

FastAPI server for receiving and processing Arcade terminal system data.
Handles !contact protocol communication and research data analysis.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="i_o Research Platform",
    description="Research platform for processing Arcade terminal system data and establishing !contact protocols",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for contact sessions and data
contact_sessions = {}
received_data = []
processing_queue = []

class ContactInitiation(BaseModel):
    """Model for contact initiation payload."""
    session_id: str
    contact_type: str
    data_summary: Dict[str, Any]
    timestamp: str

class DataTransmission(BaseModel):
    """Model for data transmission payload."""
    session_id: str
    transmission_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@app.get("/health")
async def health_check():
    """Health check endpoint for system monitoring."""
    return {
        "status": "healthy",
        "server_info": {
            "name": "i_o Research Platform",
            "version": "1.0.0",
            "uptime_seconds": time.time() - app.startup_time if hasattr(app, 'startup_time') else 0,
            "active_sessions": len(contact_sessions),
            "queued_items": len(processing_queue),
            "total_data_received": len(received_data)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/contact/initiate")
async def initiate_contact(contact: ContactInitiation, background_tasks: BackgroundTasks):
    """Initiate a !contact session with the Arcade system."""
    try:
        logger.info(f"Initiating contact session: {contact.session_id}")

        # Store session information
        contact_sessions[contact.session_id] = {
            "session_id": contact.session_id,
            "contact_type": contact.contact_type,
            "data_summary": contact.data_summary,
            "initiated_at": contact.timestamp,
            "status": "active",
            "last_activity": datetime.now().isoformat()
        }

        # Add to processing queue for analysis
        processing_queue.append({
            "type": "contact_initiation",
            "session_id": contact.session_id,
            "timestamp": datetime.now().isoformat(),
            "data": contact.dict()
        })

        # Trigger background processing
        background_tasks.add_task(process_contact_initiation, contact.session_id)

        return {
            "session_id": contact.session_id,
            "status": "established",
            "message": "!Contact session established successfully",
            "next_step": "transmit_analysis_data",
            "server_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Contact initiation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Contact initiation failed: {str(e)}")

@app.post("/contact/transmit")
async def transmit_data(transmission: DataTransmission, background_tasks: BackgroundTasks):
    """Receive comprehensive data transmission from Arcade system."""
    try:
        session_id = transmission.session_id

        if session_id not in contact_sessions:
            raise HTTPException(status_code=404, detail=f"Contact session {session_id} not found")

        logger.info(f"Receiving data transmission for session: {session_id}")

        # Store the received data
        data_entry = {
            "session_id": session_id,
            "transmission_type": transmission.transmission_type,
            "data": transmission.data,
            "metadata": transmission.metadata,
            "received_at": datetime.now().isoformat(),
            "data_size_bytes": len(json.dumps(transmission.data)),
            "processing_status": "received"
        }

        received_data.append(data_entry)

        # Update session
        contact_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        contact_sessions[session_id]["data_received"] = True
        contact_sessions[session_id]["data_size"] = data_entry["data_size_bytes"]

        # Add to processing queue
        processing_queue.append({
            "type": "data_transmission",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "data_size": data_entry["data_size_bytes"]
        })

        # Trigger background processing
        background_tasks.add_task(process_data_transmission, session_id, data_entry)

        # Save data to file for persistence
        save_received_data(data_entry)

        return {
            "session_id": session_id,
            "reception_status": "successful",
            "data_size_received": data_entry["data_size_bytes"],
            "processing_status": "queued",
            "message": "Arcade analysis data received and queued for processing",
            "server_timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data transmission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data transmission failed: {str(e)}")

@app.get("/contact/status/{session_id}")
async def get_contact_status(session_id: str):
    """Get the status of a contact session."""
    if session_id not in contact_sessions:
        raise HTTPException(status_code=404, detail=f"Contact session {session_id} not found")

    session = contact_sessions[session_id]

    # Find associated data
    session_data = [d for d in received_data if d["session_id"] == session_id]
    latest_data = session_data[-1] if session_data else None

    return {
        "session_id": session_id,
        "session_status": session["status"],
        "contact_type": session["contact_type"],
        "initiated_at": session["initiated_at"],
        "last_activity": session["last_activity"],
        "data_received": session.get("data_received", False),
        "data_size_bytes": session.get("data_size", 0),
        "reception_status": "confirmed" if session_data else "pending",
        "processing_status": latest_data["processing_status"] if latest_data else "not_started",
        "data_entries": len(session_data)
    }

@app.get("/contact/sessions")
async def list_contact_sessions():
    """List all active contact sessions."""
    return {
        "total_sessions": len(contact_sessions),
        "active_sessions": [s for s in contact_sessions.values() if s["status"] == "active"],
        "sessions": list(contact_sessions.values())
    }

@app.get("/research/data/{session_id}")
async def get_research_data(session_id: str):
    """Retrieve processed research data for a session."""
    session_data = [d for d in received_data if d["session_id"] == session_id]

    if not session_data:
        raise HTTPException(status_code=404, detail=f"No data found for session {session_id}")

    # Return the latest processed data
    latest_data = session_data[-1]

    return {
        "session_id": session_id,
        "data_type": latest_data["transmission_type"],
        "processed_data": latest_data["data"],
        "metadata": latest_data["metadata"],
        "processing_status": latest_data["processing_status"],
        "received_at": latest_data["received_at"]
    }

@app.get("/system/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    total_data_size = sum(d["data_size_bytes"] for d in received_data)

    return {
        "system_status": "operational",
        "total_contact_sessions": len(contact_sessions),
        "total_data_transmissions": len(received_data),
        "total_data_size_bytes": total_data_size,
        "processing_queue_length": len(processing_queue),
        "active_sessions": len([s for s in contact_sessions.values() if s["status"] == "active"]),
        "data_types_received": list(set(d["transmission_type"] for d in received_data)),
        "last_activity": max((d["received_at"] for d in received_data), default=None)
    }

async def process_contact_initiation(session_id: str):
    """Background processing for contact initiation."""
    try:
        logger.info(f"Processing contact initiation for session: {session_id}")

        # Simulate processing time
        await asyncio.sleep(0.1)

        # Update session status
        if session_id in contact_sessions:
            contact_sessions[session_id]["processing_status"] = "completed"

        logger.info(f"Contact initiation processing completed for session: {session_id}")

    except Exception as e:
        logger.error(f"Contact initiation processing failed for {session_id}: {e}")

async def process_data_transmission(session_id: str, data_entry: Dict[str, Any]):
    """Background processing for received data."""
    try:
        logger.info(f"Processing data transmission for session: {session_id}")

        # Extract key metrics for research analysis
        data = data_entry["data"]

        # Process system analysis data
        if "system_analysis" in data:
            analysis = data["system_analysis"]

            # Extract performance metrics
            perf_metrics = analysis.get("performance_metrics", {})
            emotional_insights = analysis.get("emotional_routing_insights", {})

            # Generate research insights
            research_insights = {
                "performance_rating": "excellent" if perf_metrics.get("avg_response_time", 1) < 0.01 else "good",
                "emotional_routing_active": len(emotional_insights.get("emotion_success_rates", {})) > 0,
                "system_stability": "high" if analysis.get("stability_analysis", {}).get("session_persistence", {}).get("session_retrieved", False) else "unknown",
                "analysis_completeness": f"{perf_metrics.get('total_operations_tested', 0)} operations analyzed"
            }

            # Update data entry with processing results
            data_entry["processing_status"] = "completed"
            data_entry["research_insights"] = research_insights
            data_entry["processed_at"] = datetime.now().isoformat()

        # Simulate processing time
        await asyncio.sleep(0.5)

        logger.info(f"Data transmission processing completed for session: {session_id}")

    except Exception as e:
        logger.error(f"Data transmission processing failed for {session_id}: {e}")
        data_entry["processing_status"] = "failed"
        data_entry["error"] = str(e)

def save_received_data(data_entry: Dict[str, Any]):
    """Save received data to file for persistence."""
    try:
        data_dir = Path("received_data")
        data_dir.mkdir(exist_ok=True)

        filename = f"{data_entry['session_id']}_{int(time.time())}.json"
        filepath = data_dir / filename

        with open(filepath, 'w') as f:
            json.dump(data_entry, f, indent=2, default=str)

        logger.info(f"Data saved to: {filepath}")

    except Exception as e:
        logger.error(f"Failed to save data: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize the server on startup."""
    app.startup_time = time.time()
    logger.info("i_o Research Platform server starting up...")

    # Create data directory if it doesn't exist
    data_dir = Path("received_data")
    data_dir.mkdir(exist_ok=True)

    logger.info("i_o Research Platform server ready to receive !contact transmissions")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("i_o Research Platform server shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
