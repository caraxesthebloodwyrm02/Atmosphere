import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.search_engine import SmartSearchOrchestrator

def main():
    files_to_index = [
        "E:\\projects\\atmosphere\\openapi.documented.yml",
        "E:\\projects\\atmosphere\\__main__.py",
        "E:\\projects\\atmosphere\\__init__.py",
        "E:\\projects\\atmosphere\\WARNING [youtube] -DVyjdw4t9I Some.txt",
        "E:\\projects\\atmosphere\\VTEC Sound & Emotion Analysis.md",
        "E:\\projects\\atmosphere\\api\\__main__.py",
        "E:\\projects\\atmosphere\\api\\__init__.py",
        "E:\\projects\\atmosphere\\api\\standalone_middleware_check.py",
        "E:\\projects\\atmosphere\\api\\server.py",
        "E:\\projects\\atmosphere\\api\\requirements.txt",
        "E:\\projects\\atmosphere\\api\\README.md",
        "E:\\projects\\atmosphere\\api\\openai_onboarding_report_20251105_001353.txt",
        "E:\\projects\\atmosphere\\api\\openai_client_config_20251105_001402.json",
        "E:\\projects\\atmosphere\\api\\onboard_client.py",
        "E:\\projects\\atmosphere\\Security Violation Remediation.md",
        "E:\\projects\\atmosphere\\COVERAGE.md",
        "E:\\projects\\atmosphere\\code_backup.py",
        "E:\\projects\\atmosphere\\codecov.yml",
        "E:\\projects\\atmosphere\\ci.yml",
        "E:\\projects\\atmosphere\\check_echoes_config.py",
        "E:\\projects\\atmosphere\\business_initiative_analyzer.py",
        "E:\\projects\\atmosphere\\breakfast_assistant.py",
        "E:\\projects\\atmosphere\\breakfast.py",
        "E:\\projects\\atmosphere\\binocular_monitor.py",
        "E:\\projects\\atmosphere\\api\\monitoring\\middleware.py",
        "E:\\projects\\atmosphere\\api\\middleware_check.py",
        "E:\\projects\\atmosphere\\api\\example.py",
        "E:\\projects\\atmosphere\\api\\connection_test.py",
        "E:\\projects\\atmosphere\\network-visualizer-python\\tests\\test_core.py",
        "E:\\projects\\atmosphere\\network-visualizer-python\\setup.py",
        "E:\\projects\\atmosphere\\network-visualizer-python\\requirements.txt",
        "E:\\projects\\atmosphere\\network-visualizer-python\\README.md",
        "E:\\projects\\atmosphere\\network-visualizer-python\\pyproject.toml",
        "E:\\projects\\atmosphere\\test_ucr.log",
        "E:\\projects\\atmosphere\\api\\middleware\\security.py",
        "E:\\projects\\atmosphere\\api\\main.py",
        "E:\\projects\\atmosphere\\api\\integration_test.py",
        "E:\\projects\\atmosphere\\test_audio_generator.py",
        "E:\\projects\\atmosphere\\binocular\\todo_monitor_20251105_044956.json",
        "E:\\projects\\atmosphere\\binocular\\todo_monitor_20251105_044335.json",
        "E:\\projects\\atmosphere\\binocular\\monitor_state.json",
        "E:\\projects\\atmosphere\\api\\config\\security_config.py",
        "E:\\projects\\atmosphere\\api\\config\\security.py",
        "E:\\projects\\atmosphere\\api\\config\\env.py",
        "E:\\projects\\atmosphere\\api\\client.py",
        "E:\\projects\\atmosphere\\automation\\setup.ps1",
        "E:\\projects\\atmosphere\\automation\\README.md",
        "E:\\projects\\atmosphere\\test_audio_analysis\\medium_quality.wav",
        "E:\\projects\\atmosphere\\test_audio_analysis\\low_quality.wav",
        "E:\\projects\\atmosphere\\test_audio_analysis\\high_quality.wav"
    ]

    print(f"Starting to index {len(files_to_index)} files from E:\\projects\\atmosphere...")
    engine = SmartSearchOrchestrator()
    result = engine.add_documents(files_to_index)
    print("Indexing complete.")
    print(f"  Files processed: {result['files_processed']}")
    print(f"  Chunks created: {result['chunks_created']}")
    if result['errors']:
        print(f"  Errors encountered: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    - {error}")

if __name__ == "__main__":
    main()
