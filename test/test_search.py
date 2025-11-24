from search.main import scan_folder, prefix_search, substring_search
from pathlib import Path
import subprocess
import sys


# ---------------------------------------------------------
# TEST 1: scan_folder()
# ---------------------------------------------------------
# Purpose:
#   Ensure scan_folder() correctly scans directories, collects files,
#   converts filenames to lowercase, and returns (all_files, prefix_index).
#
# Input:
#   tmp_path → a temporary directory created by pytest.
#
# Output:
#   all_files → list of (lowercase_filename, full_path)
#   prefix_index → sorted list based on lowercase filenames
#
# What it checks:
#   - All files in the folder are detected.
#   - Filenames are converted to lowercase.
#   - Files in subfolders are also detected.
# ---------------------------------------------------------
def test_scan_folder(tmp_path):
    # Create sample files to simulate a real folder
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "Test2.md").write_text("world")   # Mixed case on purpose
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "index.html").write_text("<html>")

    # Run the scanning function
    all_files, prefix_index = scan_folder(tmp_path)

    # There should be 3 files total
    assert len(all_files) == 3
    assert len(prefix_index) == 3

    # Extract only the lowercase filenames returned
    names = [name for name, path in all_files]

    # Ensure filenames are normalized to lowercase
    assert "test1.txt" in names
    assert "test2.md" in names
    assert "index.html" in names


# ---------------------------------------------------------
# TEST 2: prefix_search()
# ---------------------------------------------------------
# Purpose:
#   Test that prefix_search() returns files whose names START
#   with the given prefix.
#
# Input:
#   A small in-memory list representing the prefix index.
#
# Output:
#   A filtered list of matching results.
#
# What it checks:
#   - Only items whose names start with "app" are returned.
#   - Results are in sorted order.
# ---------------------------------------------------------
def test_prefix_search():
    data = [
        ("apple.txt", "/fake/apple.txt"),
        ("application.doc", "/fake/application.doc"),
        ("banana.txt", "/fake/banana.txt"),
    ]
    prefix_index = sorted(data, key=lambda x: x[0])

    # Search for prefix "app"
    results = prefix_search(prefix_index, "app")

    assert len(results) == 2                      # Only two items start with "app"
    assert results[0][0] == "apple.txt"
    assert results[1][0] == "application.doc"


# ---------------------------------------------------------
# TEST 3: substring_search()
# ---------------------------------------------------------
# Purpose:
#   Ensure substring_search() returns files whose names CONTAIN
#   the search term anywhere.
#
# Input:
#   In-memory list of filenames.
#
# Output:
#   List of matching file entries.
#
# What it checks:
#   - Files containing "index" anywhere in the name are found.
#   - Order is based on position in the array.
# ---------------------------------------------------------
def test_substring_search():
    data = [
        ("movie_index.mp4", "/fake/movie_index.mp4"),
        ("myfile.txt", "/fake/myfile.txt"),
        ("index_backup.zip", "/fake/index_backup.zip"),
    ]

    results = substring_search(data, "index")

    assert len(results) == 2                      # Two files contain "index"
    assert results[0][0] == "movie_index.mp4"
    assert results[1][0] == "index_backup.zip"


# ---------------------------------------------------------
# TEST 4: CLI – invalid path
# ---------------------------------------------------------
# Purpose:
#   Ensure running the CLI with a non-existing folder prints
#   the correct error message.
#
# Input:
#   Running `python main.py Z:/does/not/exist`
#
# Output:
#   Printed message containing "Folder does not exist".
#
# What it checks:
#   - The script handles missing folders safely.
# ---------------------------------------------------------
def test_cli_invalid_path():
    result = subprocess.run(
        [sys.executable, "main.py", "Z:/does/not/exist"],
        capture_output=True,
        text=True
    )

    assert "Folder does not exist" in result.stdout


# ---------------------------------------------------------
# TEST 5: CLI – start and exit
# ---------------------------------------------------------
# Purpose:
#   Test the full CLI boot-up flow:
#   1. Script starts
#   2. Folder is indexed
#   3. CLI waits for input
#   4. User types "exit"
#   5. Script terminates gracefully
#
# Input:
#   - Temporary folder path
#   - Program input: "exit\n"
#
# Output:
#   Lines printed by the program.
#
# What it checks:
#   - Startup indexing message appears
#   - Help instructions appear
#   - "Goodbye!" appears when exiting
# ---------------------------------------------------------
def test_cli_start_and_exit(tmp_path):
    result = subprocess.run(
        [sys.executable, "main.py", str(tmp_path)],
        input="exit\n",
        capture_output=True,
        text=True
    )

    assert "Indexing:" in result.stdout
    assert "Ready! Type your search:" in result.stdout
    assert "Goodbye!" in result.stdout
