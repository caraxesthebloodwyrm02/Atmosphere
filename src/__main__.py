#!/usr/bin/env python3
"""
Source Modules Main Entry Point
Run with: python -m src
"""

from . import __version__, get_source_versions


def main():
    """Main entry point for source modules."""
    print("📦 Source Modules v{}".format(__version__))
    print("=" * 40)

    versions = get_source_versions()
    for module, version in versions.items():
        if version != "unknown":
            print(f"  {module}: v{version}")

    print("")
    print("Usage:")
    print("  python -m src.echo")
    print("  python -m src.delay")
    print("  python -m src.reverb")
    print("  python -m src.routing")


if __name__ == "__main__":
    main()
