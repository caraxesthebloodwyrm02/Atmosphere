#!/usr/bin/env python3
"""
Ultra-Lightweight Smart Search Main Entry Point
MINIMAL DEPENDENCIES - MAXIMUM SPEED - ZERO COMPLEXITY
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from search_engine import SmartSearchOrchestrator

def main():
    """Ultra-simple main entry point"""
    parser = argparse.ArgumentParser(description='Smart Search - Ultra Fast')
    parser.add_argument('--mode', choices=['cli', 'api'], default='cli',
                       help='Run mode: cli or api')
    parser.add_argument('--files', nargs='*', help='Files to process')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--config', help='Config file path')

    args = parser.parse_args()

    # Initialize ultra-fast search engine
    config_path = args.config or "config/settings.yaml"
    engine = SmartSearchOrchestrator(config_path)

    if args.mode == 'api':
        # Start ultra-lightweight Flask API
        from api import create_web_interface
        app = create_web_interface()
        print("🚀 Smart Search API starting on http://localhost:5000")
        print(f"⚡ Tiny chunks: {engine.config['search']['chunk_size']} chars")
        app.run(host='localhost', port=5000, debug=False)

    elif args.mode == 'cli':
        if args.files:
            # Process files with tiny chunks
            print(f"⚡ Processing {len(args.files)} files with tiny chunks...")
            result = engine.add_documents(args.files)
            print(f"✅ Processed: {result['files_processed']} files")
            print(f"📦 Created: {result['chunks_created']} tiny chunks")
            if result['errors']:
                print(f"⚠️  Errors: {len(result['errors'])}")

        elif args.query:
            # Ultra-fast search
            print(f"🔍 Searching: '{args.query}'")
            results = engine.search(args.query)

            print(f"📊 Found {len(results)} results:")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                print(f"{i}. {result['file_name']} (Score: {result['score']})")
                print(f"   {result['content'][:100]}...")

        else:
            # Show stats
            stats = engine.get_stats()
            print("📈 Smart Search Stats:")
            print(f"   Documents: {stats['documents_processed']}")
            print(f"   Tiny Chunks: {stats['total_chunks']}")
            print(f"   Searches: {stats['searches_performed']}")
            print(".4f")
            print(f"   Chunk Size: {stats['chunk_size']} chars")

if __name__ == '__main__':
    main()
