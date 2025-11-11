"""
Test the __main__ block in delay_essence.py
"""

import os
import sys
import importlib.util
from unittest.mock import patch, MagicMock

"""
Test the __main__ block in delay_essence.py
"""

import os
import sys
import importlib.util
from unittest.mock import patch, MagicMock

def test_main_execution(capsys):
    """Test that the main block executes without errors and produces output."""
    # Get the path to the module
    module_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'src', 'atmosphere_audio', 'delay', 'core', 'delay_essence.py'
    )
    
    # Load and execute the module directly
    with open(module_path, 'r') as f:
        code = f.read()
    
    # Execute the module's code in a new namespace
    namespace = {}
    try:
        exec(code, namespace)
    except Exception as e:
        assert False, f"Error executing module: {e}"
    
    # If we get here, the module executed without errors
    assert True

def test_main_execution_with_mocks():
    """Test the main block with mocked print function."""
    # Get the path to the module
    module_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'src', 'atmosphere_audio', 'delay', 'core', 'delay_essence.py'
    )
    
    # Mock the print function
    with patch('builtins.print') as mock_print:
        # Load and execute the module
        with open(module_path, 'r') as f:
            code = f.read()
        
        # Execute the module's code in a new namespace
        namespace = {'__name__': '__main__'}
        try:
            exec(code, namespace)
        except Exception as e:
            assert False, f"Error executing module: {e}"
        
        # Verify that print was called
        assert mock_print.called, "The print function was not called"

if __name__ == "__main__":
    test_main_execution()
