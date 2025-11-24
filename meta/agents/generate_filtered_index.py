#!/usr/bin/env python3
"""Generate The_Real_Index.md respecting .agentignore patterns."""

import os
import hashlib
import pathlib
from datetime import datetime

PROJECT_ROOT = pathlib.Path("/home/robb/projects/maf-local")
IGNORE_FILE = PROJECT_ROOT / "meta/agents/.agentignore"
OUTPUT_FILE = PROJECT_ROOT / "meta/agents/The_Real_Index.md"

def load_ignore_patterns():
    """Load patterns from .agentignore."""
    patterns = []
    if IGNORE_FILE.exists():
        with open(IGNORE_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path_str, patterns):
    """Check if path matches any ignore pattern."""
    for pattern in patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            if path_str.startswith(pattern) or ('/' + pattern) in path_str:
                return True
        # Handle wildcard patterns
        elif '*' in pattern:
            import fnmatch
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Check filename only for patterns like *.log
            if fnmatch.fnmatch(os.path.basename(path_str), pattern):
                return True
        # Handle exact matches
        elif pattern in path_str:
            return True
    return False

def get_file_info(file_path):
    """Get hash, size, and modified time for a file."""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        stat = file_path.stat()
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        return file_hash, size, modified
    except Exception as e:
        return None, None, None

def main():
    patterns = load_ignore_patterns()
    print(f"Loaded {len(patterns)} ignore patterns: {patterns}")
    
    entries = []
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Get relative path
        rel_root = os.path.relpath(root, PROJECT_ROOT)
        
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(
            os.path.join(rel_root, d) + '/', patterns
        )]
        
        for file in files:
            rel_path = os.path.join(rel_root, file)
            if rel_path.startswith('./'):
                rel_path = rel_path[2:]
            
            # Skip if matches ignore pattern
            if should_ignore(rel_path, patterns):
                continue
            
            file_path = pathlib.Path(root) / file
            file_hash, size, modified = get_file_info(file_path)
            
            if file_hash:
                entries.append(f"{rel_path} | {file_hash} | {size} | {modified}")
    
    # Sort entries
    entries.sort()
    
    # Write to output
    with open(OUTPUT_FILE, 'w') as f:
        for entry in entries:
            f.write(entry + '\n')
    
    print(f"\n✓ Generated {OUTPUT_FILE}")
    print(f"✓ Total files indexed: {len(entries)}")
    print(f"✓ File size check: {'PASS' if len(entries) < 1000 else 'WARNING - over 1000 lines'}")

if __name__ == "__main__":
    main()
