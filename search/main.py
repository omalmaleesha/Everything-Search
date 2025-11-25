import os
import sys
import time
import psutil
from bisect import bisect_left, bisect_right
from pathlib import Path
from array import array

# Build index into RAM (low memory + fast)
def scan_folder(root: Path):
    print(f"Indexing: {root}")

    start = time.time()

    all_paths = []
    file_names = []           # only lowercase names
    offsets = array('I')      # map original index → sorted index later

    # Scan all files
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full = os.path.join(dirpath, f)
            all_paths.append(full)
            file_names.append(f.lower())

    # Sort by name, but keep indices only
    sorted_idx = sorted(range(len(file_names)), key=lambda i: file_names[i])

    # Build list of sorted names (NO slicing during search)
    sorted_names = [file_names[i] for i in sorted_idx]

    elapsed = time.time() - start
    print(f"Indexed {len(all_paths)} files in {elapsed:.2f}s")
    print(f"Memory Usage: {get_ram_usage_mb():.2f} MB")

    return all_paths, file_names, sorted_idx, sorted_names


# Prefix search
def prefix_search(all_paths, file_names, sorted_idx, sorted_names, query, limit=50):
    q = query.lower()

    # Binary search on sorted names
    lo = bisect_left(sorted_names, q)
    hi = bisect_right(sorted_names, q + "\uffff")

    results = []

    for si in sorted_idx[lo:hi][:limit]:
        results.append(all_paths[si])

    return results


# Substring search
def substring_search(all_paths, file_names, query, limit=50):
    q = query.lower()
    results = []

    for i, name in enumerate(file_names):
        if q in name:
            results.append(all_paths[i])
            if len(results) >= limit:
                break

    return results


def get_ram_usage_mb():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    return mem_bytes / (1024 * 1024)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_search.py <folder_path>")
        return

    root = Path(sys.argv[1])
    if not root.exists():
        print("Folder does not exist:", root)
        return

    all_paths, file_names, sorted_idx, sorted_names = scan_folder(root)

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
            results = prefix_search(all_paths, file_names, sorted_idx, sorted_names, query)
            t1 = time.perf_counter()

        elif cmd.startswith("substr "):
            query = cmd.split(" ", 1)[1]
            t0 = time.perf_counter()
            results = substring_search(all_paths, file_names, query)
            t1 = time.perf_counter()

        else:
            print("Unknown command")
            continue

        elapsed = t1 - t0

        if not results:
            print("No matches.\n")
            continue

        print(f"Found {len(results)} in {elapsed:.10f} seconds:")
        for p in results:
            print(p)
        print()


if __name__ == "__main__":
    main()
