import os
import sys
import time
import psutil
from bisect import bisect_left, bisect_right
from pathlib import Path

# Build index into RAM (low memory mode)

def scan_folder(root: Path):
    all_paths = []
    #in first attemp i use (file name,file path) elements like this but its gets more 
    #memroy when storing so now i only store file path.
    print(f"Indexing: {root}")

    start = time.time()
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            all_paths.append(full_path)

    # Build prefix index by sorting paths using filename as key
    prefix_index = sorted(all_paths, key=lambda p: os.path.basename(p).lower())

    elapsed = time.time() - start
    print(f"Indexed {len(all_paths)} files in {elapsed:.2f}s")
    ram_mb = get_ram_usage_mb()
    print(f"Memory Usage: {ram_mb:.2f} MB")
    return all_paths, prefix_index


# Prefix search (using bisect on sorted keys)

def prefix_search(prefix_index, query, limit=50):
    q = query.lower()

    # Extract just the sorted names once
    keys = [os.path.basename(p).lower() for p in prefix_index]

    lo = bisect_left(keys, q)
    hi = bisect_right(keys, q + "\uffff")

    results = prefix_index[lo:hi]
    return results[:limit]


# Substring search (scan all paths)

def substring_search(all_paths, query, limit=50):
    q = query.lower()
    results = []

    for path in all_paths:
        name = os.path.basename(path).lower()
        if q in name:
            results.append(path)
            if len(results) >= limit:
                break

    return results

#get ram usage and show it

def get_ram_usage_mb():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    return mem_bytes / (1024 * 1024)



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
    all_paths, prefix_index = scan_folder(root)

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
            results = substring_search(all_paths, query)
            t1 = time.perf_counter()
            elapsed = t1 - t0

        else:
            print("Unknown command")
            continue

        if not results:
            print("No matches found.\n")
            continue

        print(f"Found {len(results)} result(s) in {elapsed:.10f} seconds:")
        for path in results:
            print(path)
        print()

if __name__ == "__main__":
    main()
