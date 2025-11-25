from search.main import scan_folder, prefix_search, substring_search
from pathlib import Path
import subprocess
import sys


# ---------------------------------------------------------
# TEST 1: scan_folder()
# ---------------------------------------------------------
# Purpose:
#   Verify that scan_folder() scans all files recursively and returns:
#     - all_paths      → list of full file paths
#     - file_names     → list of lowercase names (1:1 with all_paths)
#     - sorted_idx     → index list sorted by lowercase names
#     - sorted_names   → sorted lowercase names
#
# What it checks:
#   - All files detected (including in subfolders)
#   - Lowercase naming
#   - Sorted index matches sorted filenames
# ---------------------------------------------------------
def test_scan_folder(tmp_path):
    # Create sample files
    f1 = tmp_path / "Test1.TXT"
    f1.write_text("hello")

    f2 = tmp_path / "hello.md"
    f2.write_text("world")

    sub = tmp_path / "sub"
    sub.mkdir()
    f3 = sub / "index.HTML"
    f3.write_text("<html>")

    all_paths, file_names, sorted_idx, sorted_names = scan_folder(tmp_path)

    # There should be 3 files
    assert len(all_paths) == 3
    assert len(file_names) == 3
    assert len(sorted_idx) == 3
    assert len(sorted_names) == 3

    # Ensure lowercase normalization
    assert "test1.txt" in file_names
    assert "hello.md" in file_names
    assert "index.html" in file_names

    # Ensure sorted order accuracy
    assert sorted_names == sorted(file_names)


# ---------------------------------------------------------
# TEST 2: prefix_search()
# ---------------------------------------------------------
# Purpose:
#   Validate prefix_search() correctly returns paths whose
#   lowercase basename STARTS WITH query.
#
# What it checks:
#   - Only filenames starting with "app"
#   - Returned paths correspond to sorted order
# ---------------------------------------------------------
def test_prefix_search(tmp_path):
    # Build fake directory structure
    p1 = tmp_path / "apple.txt"
    p2 = tmp_path / "application.doc"
    p3 = tmp_path / "banana.txt"

    p1.write_text("A")
    p2.write_text("B")
    p3.write_text("C")

    all_paths, file_names, sorted_idx, sorted_names = scan_folder(tmp_path)

    results = prefix_search(all_paths, file_names, sorted_idx, sorted_names, "app")

    # Only two match
    assert len(results) == 2

    # Results must be correct files
    basenames = [Path(p).name for p in results]
    assert basenames == ["apple.txt", "application.doc"]


# ---------------------------------------------------------
# TEST 3: substring_search()
# ---------------------------------------------------------
# Purpose:
#   Verify substring_search() finds filenames containing
#   the search term anywhere.
#
# What it checks:
#   - Matching sources
#   - Order follows scanning order
# ---------------------------------------------------------
def test_substring_search(tmp_path):
    p1 = tmp_path / "my_index_video.mp4"
    p2 = tmp_path / "notes.txt"
    p3 = tmp_path / "index_backup.zip"

    p1.write_text("x")
    p2.write_text("x")
    p3.write_text("x")

    all_paths, file_names, sorted_idx, sorted_names = scan_folder(tmp_path)

    results = substring_search(all_paths, file_names, "index")

    assert len(results) == 2

    names = sorted([Path(p).name for p in results])

    assert names == ["index_backup.zip", "my_index_video.mp4"]



# ---------------------------------------------------------
# TEST 4: CLI – invalid path
# ---------------------------------------------------------
def test_cli_invalid_path():
    result = subprocess.run(
        [sys.executable, "main.py", "Z:/does/not/exist"],
        capture_output=True,
        text=True
    )

    assert "Folder does not exist" in result.stdout


# ---------------------------------------------------------
# TEST 5: CLI – start + exit cleanly
# ---------------------------------------------------------
def test_cli_start_and_exit(tmp_path):
    # Feed "exit" into the program
    result = subprocess.run(
        [sys.executable, "main.py", str(tmp_path)],
        input="exit\n",
        capture_output=True,
        text=True
    )

    assert "Indexing:" in result.stdout
    assert "Ready! Type your search:" in result.stdout
    assert "Goodbye!" in result.stdout
