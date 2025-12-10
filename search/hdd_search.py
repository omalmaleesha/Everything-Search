import os
import sys
import time
import pickle
from bisect import bisect_left, bisect_right
from pathlib import Path

INDEX_FILE = "hdd_index.pkl"

def scan_folder(root: Path):
    print(f"Indexing HDD folder: {root}")
    start = time.time()

    entries = []
    append = entries.append
    lower = str.lower
    stack = [root]

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
            continue

    entries.sort(key=lambda x: x[0])
    names = [e[0] for e in entries]
    paths = [e[1] for e in entries]

    # Save index to file for faster reload next time
    with open(INDEX_FILE, "wb") as f:
        pickle.dump((names, paths), f)

    print(f"Indexed {len(paths)} files in {time.time() - start:.2f}s")
    return names, paths


def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "rb") as f:
            return pickle.load(f)
    return None, None


def prefix_search(names, paths, query, limit=50):
    q = query.lower()
    lo = bisect_left(names, q)
    hi = bisect_right(names, q + "\uffff")
    return paths[lo:hi][:limit]


def substring_search(names, paths, query, limit=50):
    q = query.lower()
    results = []
    for n, p in zip(names, paths):
        if q in n:
            results.append(p)
            if len(results) >= limit:
                break
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python hdd_search.py <folder_path>")
        return

    root = Path(sys.argv[1])

    # Try to load saved index for HDD
    names, paths = load_index()
    if names is None or paths is None:
        names, paths = scan_folder(root)
    else:
        print(f"Loaded saved HDD index with {len(paths)} files")

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
            results = prefix_search(names, paths, query)
        elif cmd.startswith("substr "):
            query = cmd.split(" ", 1)[1]
            results = substring_search(names, paths, query)
        else:
            print("Unknown command")
            continue

        if not results:
            print("No matches.\n")
            continue

        print(f"Found {len(results)} results:")
        for p in results:
            print(p)
        print()


if __name__ == "__main__":
    main()
