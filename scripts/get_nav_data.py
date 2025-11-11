# scripts/generate_test_nav_data.py
import json
from pathlib import Path
from datetime import datetime

def get_coverage_summary():
    """Extract coverage data from .coverage file or pytest-cov output"""
    # Mock data - replace with actual coverage parsing
    return {
        "total": 16.0,  # Current coverage percentage
        "target": 80.0,
        "by_module": {
            "echo/core/core.py": 0,
            "delay/core/delay_essence.py": 22,
            "core/security.py": 59,
            "network_integration.py": 0
        }
    }

def get_test_status():
    """Get current test status from pytest output"""
    # Mock data - replace with actual test results
    return {
        "total_tests": 150,
        "failing": 42,
        "passing": 108,
        "last_run": datetime.now().isoformat()
    }

if __name__ == "__main__":
    data = {
        "coverage": get_coverage_summary(),
        "tests": get_test_status(),
        "last_updated": datetime.now().isoformat()
    }
    
    output_path = Path(__file__).parent.parent / "test_nav_data.json"
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Test Navigator data saved to {output_path}")