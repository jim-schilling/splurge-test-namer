"""splurge_test_namer package metadata.

This module exposes package-level metadata used by tests and documentation.

Copyright (c) 2025 Jim Schilling
License: MIT

Attributes:
        __domains__ (list[str]): Known module domains for tests and docs.
        __version__ (str): Package version string.
        __all__ (list[str]): Public symbols exported by the package.
"""

__domains__ = ["cli", "e2e", "integration", "misc", "namer", "parser", "regression", "utils"]
__version__ = "2025.0.0"

__all__ = ["__domains__", "__version__"]
