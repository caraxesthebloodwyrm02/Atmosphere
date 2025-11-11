#!/usr/bin/env python3
"""
Quick test script for Atmosphere Arcade Terminal NLP functionality.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from terminal_tui import TerminalTUI

async def test_nlp():
    """Test NLP command processing."""
    print("Testing NLP command processing...")

    # Create a terminal instance
    terminal = TerminalTUI()

    # Test some NLP commands
    test_commands = [
        "list files",
        "show directory",
        "go to desktop",
        "where am I",
        "system information",
        "clear the screen",
        "show help"
    ]

    print("\nTesting NLP commands:")
    for cmd in test_commands:
        processed = await terminal.process_nlp_command(cmd)
        print(f'"{cmd}" → "{processed}"')

    print("\nNLP testing complete!")

if __name__ == "__main__":
    asyncio.run(test_nlp())
