from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from pathlib import Path
import json
import os
import statistics

import numpy as np
from scipy import signal
import uvicorn
from datetime import UTC, datetime

try:  # Attempt to use project-provided implementations when available
    from ecosystem import EnvironmentMap  # type: ignore
except (ImportError, AttributeError):
    class EnvironmentMap:
        """Lightweight fallback environment map for signal routing."""

        def __init__(self) -> None:
            self._nodes: Dict[str, Dict[str, object]] = {}
            self._connections: list[Dict[str, object]] = []

        def update_node(
            self,
            node_id: str,
            position: Optional[list[float]] = None,
            status: str = "active",
            **metadata: object,
        ) -> None:
            self._nodes[node_id] = {
                "position": position or [0.0, 0.0],
                "status": status,
                "metadata": metadata,
                "updated_at": datetime.now(UTC).isoformat(),
            }

        def connect_nodes(
            self,
            source: str,
            destination: str,
            weight: float = 1.0,
            metadata: Optional[Dict[str, object]] = None,
        ) -> None:
            self._connections.append(
                {
                    "source": source,
                    "destination": destination,
                    "weight": weight,
                    "metadata": metadata or {},
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

        def get_nodes(self) -> Dict[str, Dict[str, object]]:
            return self._nodes

        def get_connections(self) -> list[Dict[str, object]]:
            return self._connections


try:
    from i_o import SignalIO  # type: ignore
except (ImportError, AttributeError):
    class SignalIO:
        """Fallback IO handler that persists transmission logs locally."""

        def __init__(self, base_path: Path | None = None) -> None:
            self.base_path = base_path or Path("data")
            self.log_path = self.base_path / "logs" / "wave_signal_transmissions.jsonl"
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

        def log_transmission(self, transmission: "SignalTransmission") -> None:
            entry = transmission.model_dump(mode="json")
            entry["logged_at"] = datetime.now(UTC).isoformat()
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")


try:
    from metrics import EngagementAnalyzer  # type: ignore
except (ImportError, AttributeError):
    class EngagementAnalyzer:
        """Fallback engagement analytics that tracks simple aggregates."""

        def __init__(self) -> None:
            self._interactions: list[Dict[str, object]] = []

        def record_interaction(
            self,
            *,
            source: str,
            target: str,
            signal_strength: float,
            metadata: Optional[Dict[str, object]] = None,
        ) -> None:
            self._interactions.append(
                {
                    "source": source,
                    "target": target,
                    "signal_strength": signal_strength,
                    "metadata": metadata or {},
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

        def get_metrics(self) -> Dict[str, object]:
            if not self._interactions:
                return {
                    "total_interactions": 0,
                    "average_signal_strength": 0.0,
                    "last_interaction": None,
                }

            strengths = [entry["signal_strength"] for entry in self._interactions]
            return {
                "total_interactions": len(self._interactions),
                "average_signal_strength": statistics.fmean(strengths),
                "peak_signal_strength": max(strengths),
                "last_interaction": self._interactions[-1],
            }


app = FastAPI(
    title="Atmosphere Wave Signal API",
    description="REST API for wave signal processing and analysis",
    version="1.0.0",
)


class WaveSignal(BaseModel):
    frequency: float
    amplitude: float
    phase: float = 0.0
    timestamp: str = datetime.now(UTC).isoformat()
    metadata: Optional[Dict] = None

class SignalTransmission(BaseModel):
    source: str
    destination: str
    protocol: str = "HTTP/1.1"
    signal: WaveSignal
    environment: Optional[Dict] = None

class SignalProcessor:
    def __init__(self) -> None:
        self.signals: Dict[str, WaveSignal] = {}
        self.environment = EnvironmentMap()
        self.io_handler = SignalIO()
        self.analyzer = EngagementAnalyzer()
        self.sample_rate = 44_100
        self._default_duration = 1.0  # seconds

    def process_signal(self, signal_data: WaveSignal) -> Dict:
        """Process incoming wave signal."""
        times, waveform = self._synthesize_waveform(signal_data)

        processed = {
            "original": signal_data.dict(),
            "processed": self._apply_effects(signal_data, times, waveform),
            "spectrum": self._generate_spectrum(waveform),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return processed

    def _synthesize_waveform(self, signal_data: WaveSignal) -> tuple[np.ndarray, np.ndarray]:
        """Create a base sinusoidal waveform for downstream processing."""
        sample_count = int(self.sample_rate * self._default_duration)
        times = np.linspace(0.0, self._default_duration, sample_count, endpoint=False)
        waveform = signal_data.amplitude * np.sin(
            2 * np.pi * signal_data.frequency * times + signal_data.phase
        )
        return times, waveform

    def _apply_effects(
        self,
        signal_data: WaveSignal,
        times: np.ndarray,
        waveform: np.ndarray,
    ) -> Dict[str, Dict[str, object]]:
        """Apply delay, echo, and reverb style effects with configurable metadata."""
        return {
            "delay": self._apply_delay(signal_data, waveform),
            "echo": self._apply_echo(signal_data, waveform),
            "reverb": self._apply_reverb(signal_data, waveform),
            "waveform_preview": {
                "times": times[:200].tolist(),
                "amplitudes": waveform[:200].tolist(),
            },
        }

    def _apply_delay(self, signal_data: WaveSignal, waveform: np.ndarray) -> Dict[str, object]:
        """Simulate a simple delay line with configurable decay."""
        delay_seconds = float(signal_data.metadata.get("delay_seconds", 0.25)) if signal_data.metadata else 0.25
        decay = float(signal_data.metadata.get("delay_decay", 0.5)) if signal_data.metadata else 0.5
        delay_samples = max(1, int(self.sample_rate * delay_seconds))

        delayed = np.zeros(len(waveform) + delay_samples)
        delayed[: len(waveform)] += waveform
        delayed[delay_samples : delay_samples + len(waveform)] += waveform * decay

        return {
            "delay_seconds": delay_seconds,
            "decay": decay,
            "peak_amplitude": float(np.max(np.abs(delayed))),
            "preview": delayed[:200].tolist(),
        }

    def _apply_echo(self, signal_data: WaveSignal, waveform: np.ndarray) -> Dict[str, object]:
        """Generate a basic multi-tap echo effect."""
        taps = signal_data.metadata.get("echo_taps", [0.4, 0.25, 0.15]) if signal_data.metadata else [0.4, 0.25, 0.15]
        echo_wave = waveform.copy()
        for i, tap in enumerate(taps, start=1):
            offset = i * int(0.1 * self.sample_rate)
            padded = np.zeros(len(waveform) + offset)
            padded[: len(waveform)] = waveform
            echo_wave = np.pad(echo_wave, (0, offset))
            echo_wave[: len(padded)] += padded * tap

        return {
            "taps": taps,
            "rms": float(np.sqrt(np.mean(np.square(echo_wave)))),
            "preview": echo_wave[:200].tolist(),
        }

    def _apply_reverb(self, signal_data: WaveSignal, waveform: np.ndarray) -> Dict[str, object]:
        """Apply a lightweight Schroeder-style reverb approximation."""
        decay = float(signal_data.metadata.get("reverb_decay", 0.4)) if signal_data.metadata else 0.4
        comb_sizes = [int(self.sample_rate * t) for t in (0.0297, 0.0371, 0.0411)]
        reverb_wave = waveform.copy()
        for comb in comb_sizes:
            impulse = np.zeros(comb)
            impulse[0] = 1.0
            impulse[-1] = decay
            reverb_wave = np.convolve(reverb_wave, impulse)[: len(waveform)]

        return {
            "comb_sizes": comb_sizes,
            "decay": decay,
            "spectral_centroid": float(
                np.sum(np.abs(np.fft.rfft(reverb_wave)) * np.fft.rfftfreq(len(reverb_wave), 1 / self.sample_rate))
                / max(np.sum(np.abs(np.fft.rfft(reverb_wave))), 1e-6)
            ),
            "preview": reverb_wave[:200].tolist(),
        }

    def _generate_spectrum(self, waveform: np.ndarray) -> Dict[str, object]:
        """Generate frequency spectrum analysis."""
        frequencies, psd = signal.welch(waveform, fs=self.sample_rate)

        return {
            "frequencies": frequencies.tolist(),
            "power_spectrum": psd.tolist(),
        }

    def save_signal(self, signal_data: WaveSignal) -> str:
        """Persist the provided signal and return its identifier."""
        signal_id = f"sig_{datetime.now(UTC).timestamp()}"
        self.signals[signal_id] = signal_data
        return signal_id

processor = SignalProcessor()

@app.post("/api/v1/signals/transmit", response_model=Dict)
async def transmit_signal(transmission: SignalTransmission):
    """Endpoint for transmitting wave signals"""
    try:
        # Process the incoming signal
        result = processor.process_signal(transmission.signal)

        environment_payload = transmission.environment or {}
        extra_metadata = {
            key: value
            for key, value in environment_payload.items()
            if key not in {"position", "status"}
        }

        processor.environment.update_node(
            node_id=transmission.source,
            position=environment_payload.get("position"),
            status=environment_payload.get("status", "active"),
            **extra_metadata,
        )

        if (
            transmission.destination
            and hasattr(processor.environment, "connect_nodes")
        ):
            processor.environment.connect_nodes(
                transmission.source,
                transmission.destination,
                weight=environment_payload.get("link_weight", 1.0),
                metadata=extra_metadata or None,
            )

        # Log the transmission
        processor.io_handler.log_transmission(transmission)
        
        # Update engagement metrics
        processor.analyzer.record_interaction(
            source=transmission.source,
            target=transmission.destination,
            signal_strength=transmission.signal.amplitude
        )
        
        return {
            "status": "transmitted",
            "signal_id": processor.save_signal(transmission.signal),
            "processing_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/signals/{signal_id}", response_model=WaveSignal)
async def get_signal(signal_id: str):
    """Retrieve a stored signal by ID"""
    if signal_id not in processor.signals:
        raise HTTPException(status_code=404, detail="Signal not found")
    return processor.signals[signal_id]

@app.get("/api/v1/spectrum/{signal_id}")
async def get_spectrum(signal_id: str):
    """Get frequency spectrum for a signal"""
    if signal_id not in processor.signals:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    signal_data = processor.signals[signal_id]
    _, waveform = processor._synthesize_waveform(signal_data)
    spectrum = processor._generate_spectrum(waveform)
    
    return {
        "signal_id": signal_id,
        "spectrum": spectrum,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/environment")
async def get_environment():
    """Get current environment map"""
    return {
        "nodes": processor.environment.get_nodes(),
        "connections": processor.environment.get_connections(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/analytics/engagement")
async def get_engagement_metrics():
    """Get engagement analytics"""
    return processor.analyzer.get_metrics()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/signals", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    
    # Start the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)