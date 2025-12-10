import os
import sys
import time
import psutil
from bisect import bisect_left, bisect_right
from pathlib import Path

# ----------------------------
# Scan folder and build index using os.scandir
# ----------------------------
def scan_folder(root: Path):
    print(f"Indexing: {root}")
    start = time.time()

    entries = []  # store (lower_name, full_path)
    append = entries.append
    lower = str.lower

    stack = [root]  # stack for directories
    while stack:
        current_dir = stack.pop()
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        append((lower(entry.name), entry.path))
        except PermissionError:
            # Skip folders without permissions
            continue

    # Sort entries by lowercase name
    entries.sort(key=lambda x: x[0])

    names = [e[0] for e in entries]
    paths = [e[1] for e in entries]

    elapsed = time.time() - start
    print(f"Indexed {len(paths)} files in {elapsed:.2f}s")
    print(f"Memory Usage: {get_ram_usage_mb():.2f} MB")

    return names, paths


# ----------------------------
# Prefix search using bisect
# ----------------------------
def prefix_search(names, paths, query, limit=50):
    q = query.lower()
    lo = bisect_left(names, q)
    hi = bisect_right(names, q + "\uffff")
    return paths[lo:hi][:limit]


# ----------------------------
# Substring search (linear)
# ----------------------------
def substring_search(names, paths, query, limit=50):
    q = query.lower()
    results = []
    append = results.append
    for n, p in zip(names, paths):
        if q in n:
            append(p)
            if len(results) >= limit:
                break
    return results


# ----------------------------
# RAM usage helper
# ----------------------------
def get_ram_usage_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


# ----------------------------
# Main CLI
# ----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python fast_search.py <folder_path>")
        return

    root = Path(sys.argv[1])
    if not root.exists():
        print("Folder does not exist:", root)
        return

    names, paths = scan_folder(root)

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
            results = prefix_search(names, paths, query)
            t1 = time.perf_counter()

        elif cmd.startswith("substr "):
            query = cmd.split(" ", 1)[1]
            t0 = time.perf_counter()
            results = substring_search(names, paths, query)
            t1 = time.perf_counter()
        else:
            print("Unknown command")
            continue

        elapsed = t1 - t0
        if not results:
            print("No matches.\n")
            continue

        print(f"Found {len(results)} in {elapsed:.6f} seconds:")
        for p in results:
            print(p)
        print()


if __name__ == "__main__":
    main()
