"""exceptions.py
Custom domain-specific exceptions for splurge_test_namer."""


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
