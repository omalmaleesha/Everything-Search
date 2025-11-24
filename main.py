#!/usr/bin/env python3
"""Top-level wrapper so tests can execute `python main.py`.

This forwards to the package implementation in `search.main`.
"""
from search.main import main


if __name__ == "__main__":
    main()
