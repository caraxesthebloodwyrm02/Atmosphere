import os
import inspect
import importlib.util
from pathlib import Path

def analyze_codebase(base_path):
    print(f"Analyzing codebase at: {base_path}\n")
    
    # Traverse the directory structure
    for file_path in Path(base_path).rglob("*.py"):
        print(f"Directory: {file_path.parent}")
        print(f"  Found Python file: {file_path.name}")
        analyze_python_file(str(file_path))
        print()

def analyze_python_file(file_path):
    module_name = Path(file_path).stem
    try:
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            print(f"  Could not analyze {file_path}: spec or loader is None")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)        # Inspect the module
        print(f"  Inspecting module: {module_name}")
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                print(f"    Function: {name} - {inspect.signature(obj)}")
            elif inspect.isclass(obj):
                print(f"    Class: {name}")
    except Exception as e:
        print(f"  Could not analyze {file_path}: {e}")

if __name__ == "__main__":
    base_path = "e:/Projects/Atmosphere/Echoes"  # Replace with your codebase path
    analyze_codebase(base_path)