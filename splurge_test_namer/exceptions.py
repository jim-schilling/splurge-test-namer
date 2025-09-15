"""Custom domain-specific exceptions for splurge_test_namer.

This module defines expressive exception types used across the package so
consumers can catch specific error classes for file IO, renaming, and
sentinel parsing failures.

Copyright (c) 2025 Jim Schilling
License: MIT
"""


class SplurgeTestNamerError(Exception):
    """Base exception for splurge_test_namer errors."""

    pass


class SentinelReadError(SplurgeTestNamerError):
    """Raised when sentinel extraction from file fails."""

    pass


class FileRenameError(SplurgeTestNamerError):
    """Raised when file renaming fails."""

    pass


class FileReadError(SplurgeTestNamerError):
    """Raised when file reading fails."""

    pass


class FileWriteError(SplurgeTestNamerError):
    """Raised when file writing fails."""

    pass


class FileGlobError(SplurgeTestNamerError):
    """Raised when file globbing fails."""

    pass
