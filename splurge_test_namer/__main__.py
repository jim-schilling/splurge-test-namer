"""Package entrypoint for splurge_test_namer.

Copyright (c) 2025 Jim Schilling
License: MIT
"""

if __name__ == "__main__":
    # Keep minimal to allow `python -m splurge_test_namer` to be importable.
    from .cli import main

    main()
