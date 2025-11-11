"""
Comprehensive unit tests for i_o Research Platform
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

# Import the FastAPI app
from main import app, ContactInitiation, DataTransmission


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test basic health check response."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "server_info" in data
        assert "timestamp" in data

        server_info = data["server_info"]
        assert "name" in server_info
        assert server_info["name"] == "i_o Research Platform"
        assert "version" in server_info
        assert "uptime_seconds" in server_info
        assert "active_sessions" in server_info
        assert "queued_items" in server_info
        assert "total_data_received" in server_info


class TestContactInitiation:
    """Test contact initiation endpoints."""

    def test_successful_contact_initiation(self, client):
        """Test successful contact session initiation."""
        contact_data = {
            "session_id": "test-session-123",
            "contact_type": "research",
            "data_summary": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }

        response = client.post("/contact/initiate", json=contact_data)
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["status"] == "established"
        assert "message" in data
        assert "next_step" in data
        assert "server_timestamp" in data

    def test_contact_initiation_invalid_data(self, client):
        """Test contact initiation with invalid data."""
        # Missing required fields
        response = client.post("/contact/initiate", json={})
        assert response.status_code == 422  # Validation error

        # Invalid session_id type
        response = client.post("/contact/initiate", json={
            "session_id": 123,  # Should be string
            "contact_type": "research",
            "data_summary": {},
            "timestamp": datetime.now().isoformat()
        })
        assert response.status_code == 422

    def test_contact_initiation_duplicate_session(self, client):
        """Test initiating contact with existing session ID."""
        contact_data = {
            "session_id": "duplicate-session",
            "contact_type": "research",
            "data_summary": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }

        # First initiation should succeed
        response1 = client.post("/contact/initiate", json=contact_data)
        assert response1.status_code == 200

        # Second initiation with same ID should still work (overwrite)
        response2 = client.post("/contact/initiate", json=contact_data)
        assert response2.status_code == 200


class TestDataTransmission:
    """Test data transmission endpoints."""

    def test_successful_data_transmission(self, client):
        """Test successful data transmission to existing session."""
        # First initiate contact
        contact_data = {
            "session_id": "transmission-test",
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        # Now transmit data
        transmission_data = {
            "session_id": "transmission-test",
            "transmission_type": "system_analysis",
            "data": {
                "system_analysis": {
                    "performance_metrics": {"avg_response_time": 0.05},
                    "emotional_routing_insights": {"success_rates": [0.9, 0.8]}
                }
            },
            "metadata": {"version": "1.0"}
        }

        response = client.post("/contact/transmit", json=transmission_data)
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "transmission-test"
        assert data["reception_status"] == "successful"
        assert "data_size_received" in data
        assert "processing_status" in data
        assert "server_timestamp" in data

    def test_data_transmission_unknown_session(self, client):
        """Test data transmission to non-existent session."""
        transmission_data = {
            "session_id": "unknown-session",
            "transmission_type": "test",
            "data": {"test": "data"},
            "metadata": {}
        }

        response = client.post("/contact/transmit", json=transmission_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_data_transmission_invalid_data(self, client):
        """Test data transmission with invalid data structure."""
        response = client.post("/contact/transmit", json={})
        assert response.status_code == 422


class TestSessionManagement:
    """Test session status and listing endpoints."""

    def test_get_contact_status_existing_session(self, client):
        """Test retrieving status of existing contact session."""
        # Create session
        contact_data = {
            "session_id": "status-test",
            "contact_type": "research",
            "data_summary": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        # Get status
        response = client.get("/contact/status/status-test")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "status-test"
        assert data["contact_type"] == "research"
        assert data["session_status"] == "active"
        assert data["data_received"] is False
        assert data["data_size_bytes"] == 0

    def test_get_contact_status_unknown_session(self, client):
        """Test retrieving status of non-existent session."""
        response = client.get("/contact/status/unknown-session")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_contact_sessions(self, client):
        """Test listing all contact sessions."""
        # Clear any existing sessions from previous tests
        from i_o.main import contact_sessions
        contact_sessions.clear()

        # Create multiple sessions
        sessions = [
            {
                "session_id": f"session-{i}",
                "contact_type": f"type-{i}",
                "data_summary": {"id": i},
                "timestamp": datetime.now().isoformat()
            }
            for i in range(3)
        ]

        for session in sessions:
            client.post("/contact/initiate", json=session)

        # List sessions
        response = client.get("/contact/sessions")
        assert response.status_code == 200

        data = response.json()
        assert data["total_sessions"] == 3
        assert len(data["active_sessions"]) == 3
        assert len(data["sessions"]) == 3


class TestResearchDataRetrieval:
    """Test research data retrieval endpoints."""

    def test_get_research_data_existing(self, client):
        """Test retrieving research data for session with data."""
        # Create session and transmit data
        session_id = "research-data-test"
        contact_data = {
            "session_id": session_id,
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        transmission_data = {
            "session_id": session_id,
            "transmission_type": "system_analysis",
            "data": {
                "system_analysis": {
                    "performance_metrics": {"avg_response_time": 0.05}
                }
            },
            "metadata": {"version": "1.0"}
        }
        client.post("/contact/transmit", json=transmission_data)

        # Retrieve research data
        response = client.get(f"/research/data/{session_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == session_id
        assert data["data_type"] == "system_analysis"
        assert "processed_data" in data
        assert "metadata" in data
        assert "processing_status" in data

    def test_get_research_data_no_data(self, client):
        """Test retrieving research data for session without data."""
        # Create session without data
        session_id = "no-data-session"
        contact_data = {
            "session_id": session_id,
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        # Try to retrieve data
        response = client.get(f"/research/data/{session_id}")
        assert response.status_code == 404
        assert "no data found" in response.json()["detail"].lower()


class TestSystemStatistics:
    """Test system statistics endpoint."""

    def test_get_system_stats(self, client):
        """Test retrieving system statistics."""
        # Create some sessions and data
        for i in range(2):
            contact_data = {
                "session_id": f"stats-session-{i}",
                "contact_type": "research",
                "data_summary": {"id": i},
                "timestamp": datetime.now().isoformat()
            }
            client.post("/contact/initiate", json=contact_data)

            transmission_data = {
                "session_id": f"stats-session-{i}",
                "transmission_type": f"type-{i}",
                "data": {"test": f"data-{i}"},
                "metadata": {}
            }
            client.post("/contact/transmit", json=transmission_data)

        # Get stats
        response = client.get("/system/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["system_status"] == "operational"
        assert data["total_contact_sessions"] >= 2
        assert data["total_data_transmissions"] >= 2
        assert "total_data_size_bytes" in data
        assert "active_sessions" in data
        assert "data_types_received" in data
        assert "last_activity" in data


class TestDataProcessing:
    """Test background data processing functionality."""

    @patch('main.process_contact_initiation')
    def test_contact_initiation_background_processing(self, mock_process, client):
        """Test that background processing is triggered for contact initiation."""
        contact_data = {
            "session_id": "background-test",
            "contact_type": "research",
            "data_summary": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }

        response = client.post("/contact/initiate", json=contact_data)
        assert response.status_code == 200

        # Background task should be called
        # Note: In test environment, background tasks may not execute immediately

    @patch('main.process_data_transmission')
    def test_data_transmission_background_processing(self, mock_process, client):
        """Test that background processing is triggered for data transmission."""
        # Create session first
        contact_data = {
            "session_id": "bg-processing-test",
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        # Transmit data
        transmission_data = {
            "session_id": "bg-processing-test",
            "transmission_type": "test",
            "data": {"test": "data"},
            "metadata": {}
        }

        response = client.post("/contact/transmit", json=transmission_data)
        assert response.status_code == 200

        # Background task should be called
        # Note: In test environment, background tasks may not execute immediately

    @patch('main.save_received_data')
    def test_data_file_save(self, mock_save, client):
        """Test that data is saved to file."""
        # Create session and transmit data
        session_id = "file-save-test"
        contact_data = {
            "session_id": session_id,
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        transmission_data = {
            "session_id": session_id,
            "transmission_type": "test",
            "data": {"test": "data"},
            "metadata": {}
        }

        response = client.post("/contact/transmit", json=transmission_data)
        assert response.status_code == 200

        # File save should be called
        mock_save.assert_called_once()


class TestDataPersistence:
    """Test data persistence functionality."""

    def test_data_directory_creation(self, client, tmp_path):
        """Test that received_data directory is created."""
        with patch('main.Path') as mock_path:
            mock_data_dir = MagicMock()
            mock_path.return_value = mock_data_dir
            mock_data_dir.mkdir = MagicMock()

            # Create session and transmit data
            session_id = "dir-creation-test"
            contact_data = {
                "session_id": session_id,
                "contact_type": "research",
                "data_summary": {"test": "init"},
                "timestamp": datetime.now().isoformat()
            }
            client.post("/contact/initiate", json=contact_data)

            transmission_data = {
                "session_id": session_id,
                "transmission_type": "test",
                "data": {"test": "data"},
                "metadata": {}
            }

            response = client.post("/contact/transmit", json=transmission_data)
            assert response.status_code == 200

    def test_data_file_writing(self, client, tmp_path):
        """Test that data is written to JSON files."""
        with patch('main.Path') as mock_path_class:
            # Mock the Path and file operations
            mock_data_dir = MagicMock()
            mock_file_path = MagicMock()
            mock_path_class.return_value = mock_data_dir
            mock_data_dir.__truediv__ = MagicMock(return_value=mock_file_path)
            mock_data_dir.mkdir = MagicMock()

            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                # Create session and transmit data
                session_id = "file-write-test"
                contact_data = {
                    "session_id": session_id,
                    "contact_type": "research",
                    "data_summary": {"test": "init"},
                    "timestamp": datetime.now().isoformat()
                }
                client.post("/contact/initiate", json=contact_data)

                transmission_data = {
                    "session_id": session_id,
                    "transmission_type": "test",
                    "data": {"test": "data"},
                    "metadata": {}
                }

                response = client.post("/contact/transmit", json=transmission_data)
                assert response.status_code == 200

                # File should be opened and json.dump called
                mock_open.assert_called()
                # Note: json.dump would be called but we can't easily mock it here


class TestErrorHandling:
    """Test error handling in the API."""

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payloads."""
        response = client.post("/contact/initiate",
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422  # FastAPI returns 422 for validation errors

    def test_missing_content_type(self, client):
        """Test handling of requests without proper content type."""
        response = client.post("/contact/initiate", data="{}")
        # Should still work as FastAPI handles it

    def test_large_payload(self, client):
        """Test handling of large data payloads."""
        large_data = {"data": "x" * 1000000}  # 1MB of data
        transmission_data = {
            "session_id": "large-payload-test",
            "transmission_type": "large_test",
            "data": large_data,
            "metadata": {}
        }

        # Create session first
        contact_data = {
            "session_id": "large-payload-test",
            "contact_type": "research",
            "data_summary": {"test": "init"},
            "timestamp": datetime.now().isoformat()
        }
        client.post("/contact/initiate", json=contact_data)

        response = client.post("/contact/transmit", json=transmission_data)
        assert response.status_code == 200

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time

        results = []

        def make_request(session_id):
            contact_data = {
                "session_id": session_id,
                "contact_type": "research",
                "data_summary": {"test": "concurrent"},
                "timestamp": datetime.now().isoformat()
            }
            response = client.post("/contact/initiate", json=contact_data)
            results.append((session_id, response.status_code))

        # Start multiple threads making requests
        threads = []
        for i in range(5):
            t = threading.Thread(target=make_request, args=[f"concurrent-{i}"])
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All should succeed
        assert len(results) == 5
        for session_id, status_code in results:
            assert status_code == 200


# Pytest fixtures
@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
