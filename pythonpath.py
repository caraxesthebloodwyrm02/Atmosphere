import sys
from pathlib import Path

# Add the Echoes directory to sys.path
base_path = str(Path("e:/Projects/Atmosphere/Echoes").resolve())
if base_path not in sys.path:
    sys.path.append(base_path)

# Now you can import EchoesAssistantV2
# If you need EchoesAssistantV2, ensure the correct module name is used.
# For example, if the correct module is echoes_assistant_v2:
# from Echoes.echoes_assistant_v2 import EchoesAssistantV2
# Otherwise, remove the unused import:
# (Commented out since 'some_module' does not exist and import is unused)
# from Echoes.some_module import EchoesAssistantV2