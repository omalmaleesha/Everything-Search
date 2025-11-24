#!/usr/bin/env python3

import cmd
import os
import sys
import time
from bisect import bisect_left, bisect_right
from pathlib import Path

# Build index into RAM

def scan_folder(root: Path):
    all_files = []
    print(f"Indexing: {root}")

    start = time.time()
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            f_low = f.lower()
            full = os.path.join(dirpath, f)
            all_files.append((f_low, full))
    
    # Prefix index: sorted list
    prefix_index = sorted(all_files, key=lambda x: x[0])

    elapsed = time.time() - start
    print(f"Indexed {len(all_files)} files in {elapsed:.2f}s")
    return all_files, prefix_index


# Prefix search (very fast with bisect)

def prefix_search(prefix_index, query, limit=50):
    q = query.lower()
    keys = [x[0] for x in prefix_index]

    lo = bisect_left(keys, q)
    hi = bisect_right(keys, q + "\uffff")

    return prefix_index[lo:hi][:limit]

# Substring search (fast because in RAM)

def substring_search(all_files, query, limit=50):
    q = query.lower()
    results = []
    for name, path in all_files:
        if q in name:
            results.append((name, path))
            if len(results) >= limit:
                break
    return results


# Main CLI

def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_search.py <folder_path>")
        return

    root = Path(sys.argv[1])
    if not root.exists():
        print("Folder does not exist:", root)
        return

    # Build in-memory index
    all_files, prefix_index = scan_folder(root)

    print("\nReady! Type your search:")
    print("  search <text>    -> prefix search")
    print("  substr <text>    -> substring search")
    print("  exit             -> quit\n")

    while True:
        cmd = input("> ").strip()
        if cmd in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        if cmd.startswith("search "):
            query = cmd.split(" ", 1)[1]

            t0 = time.perf_counter()
            results = prefix_search(prefix_index, query)
            t1 = time.perf_counter()
            elapsed = t1 - t0

        elif cmd.startswith("substr "):
            query = cmd.split(" ", 1)[1]

            t0 = time.perf_counter()
            results = substring_search(all_files, query)
            t1 = time.perf_counter()
            elapsed = t1 - t0
        
        else:
            print("Unknown command")
            continue

        if not results:
            print("No matches found.\n")
            continue

        print(f"Found {len(results)} result(s) in {elapsed:.10f} seconds:")
        for name, path in results:
            print(path)
        print()

    # When program closes → RAM cleared automatically


if __name__ == "__main__":
    main()
