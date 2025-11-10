import os
from pathlib import Path

def count_tokens(filepath):
    """Approximate token count: ~1 token per 4 characters for GPT models"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Rough approximation: 1 token ≈ 4 characters
    return len(content) // 4

def count_tokens_in_dir(directory, extensions=('.py', '.md', '.txt', '.yml', '.yaml', '.toml', '.json'), exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.venv', '.git', '__pycache__', 'dist', 'build', '.pytest_cache', 'node_modules'}
    
    # First, collect all file paths to know the total count
    file_paths = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(extensions):
                file_paths.append(os.path.join(root, file))
    
    total_tokens = 0
    processed = 0
    
    print(f"Found {len(file_paths)} files to process...")
    
    for filepath in file_paths:
        try:
            tokens = count_tokens(filepath)
            total_tokens += tokens
            processed += 1
            
            # Progress reporting every 10 files
            if processed % 10 == 0:
                print(f"Processed {processed}/{len(file_paths)} files, ~{total_tokens} tokens so far...")
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    return total_tokens, len(file_paths)

# Example usage
print("Starting token count (approximate)...")
total_tokens, files_count = count_tokens_in_dir('e:/Projects/Atmosphere')
print(f"\nApproximate total tokens: {total_tokens}")
print(f"Files processed: {files_count}")
print("Note: This is an approximation (1 token ≈ 4 characters). For exact count, use tiktoken with internet access.")