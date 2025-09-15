"""Utility helpers for safe filesystem operations.

This module exposes a small set of helpers for reading and writing files,
performing safe renames with validation, and recursively globbing files.
These helpers centralize error handling and raise domain-specific
exceptions defined in :mod:`splurge_test_namer.exceptions`.

Copyright (c) 2025 Jim Schilling
License: MIT
"""

from pathlib import Path
from splurge_test_namer.exceptions import (
    FileReadError,
    FileWriteError,
    FileRenameError,
    FileGlobError,
)
import logging


LOGGER = logging.getLogger(__name__)


def configure_logging(verbose: bool = False) -> None:
    """Configure module logging level from CLI verbosity.

    Args:
        verbose: When True, sets level to DEBUG; otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


DOMAINS = ["utils"]


def safe_file_reader(path: Path, encoding: str = "utf-8") -> str:
    """Read a file and return its text contents.

    Args:
        path: Path to the file to read.
        encoding: Text encoding to use.

    Returns:
        The decoded file contents as a string.

    Raises:
        FileReadError: If the file could not be read.
    """
    try:
        return path.read_text(encoding=encoding)
    except Exception as e:
        LOGGER.debug("safe_file_reader failed for %s: %s", path, e)
        raise FileReadError(f"Failed to read file: {path}") from e


def safe_file_writer(path: Path, data: str, encoding: str = "utf-8") -> None:
    """Write data to a file safely.

    Args:
        path: Destination path.
        data: Text data to write.
        encoding: Text encoding to use.

    Raises:
        FileWriteError: If writing the file fails.
    """
    try:
        # Ensure parent directory exists and is a directory we can write into
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        elif not path.parent.is_dir():
            raise FileWriteError(f"Destination parent is not a directory: {path.parent}")
        path.write_text(data, encoding=encoding)
    except FileWriteError:
        raise
    except Exception as e:
        LOGGER.debug("safe_file_writer failed for %s: %s", path, e)
        raise FileWriteError(f"Failed to write file: {path}") from e


def safe_file_renamer(src: Path, dst: Path, overwrite: bool = False) -> None:
    """Safely rename ``src`` to ``dst`` with safety checks.

    This helper prevents accidental overwrites by default and ensures the
    destination parent directory exists and is a directory.

    Args:
        src: Source file path.
        dst: Destination file path.
        overwrite: If True, allow overwriting an existing destination file.

    Raises:
        FileRenameError: If the rename fails or validations fail.
    """
    try:
        if not src.exists():
            raise FileRenameError(f"Source does not exist: {src}")
        if dst.exists() and not overwrite:
            raise FileRenameError(f"Destination exists and overwrite is False: {dst}")
        if dst.parent.exists() and not dst.parent.is_dir():
            raise FileRenameError(f"Destination parent exists but is not a directory: {dst.parent}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Use replace to atomically move on the same filesystem when possible
        src.replace(dst)
    except FileRenameError:
        raise
    except Exception as e:
        LOGGER.debug("safe_file_renamer failed %s -> %s: %s", src, dst, e)
        raise FileRenameError(f"Failed to rename {src} to {dst}") from e


def safe_file_rglob(root: Path, pattern: str) -> list[Path]:
    """Perform a recursive glob and return matching file paths.

    Args:
        root: Root path to search under.
        pattern: Glob pattern (e.g. "*.py").

    Returns:
        List of matching Path objects.

    Raises:
        FileGlobError: On underlying filesystem errors.
    """
    try:
        return list(root.rglob(pattern))
    except Exception as e:
        LOGGER.debug("safe_file_rglob failed for %s %s: %s", root, pattern, e)
        raise FileGlobError(f"Failed to rglob {pattern} in {root}") from e


def resolve_module_to_paths(module_name: str, repo_root: Path) -> list[Path]:
    """Resolve a dotted module name to candidate file paths inside repo_root.

    Prefer module.py, then module/__init__.py. Returns empty list if nothing found.

    Args:
        module_name: Dotted module name (e.g. "pkg.sub.module").
        repo_root: Filesystem root to resolve against.

    Returns:
        Candidate Path objects found in the repository.
    """
    parts = module_name.split(".")
    candidates: list[Path] = []
    # Try module as file: repo_root/parts[0]/.../parts[-1].py
    file_path = repo_root.joinpath(*parts).with_suffix(".py")
    if file_path.exists():
        candidates.append(file_path)
    # Try package __init__.py: repo_root/parts[0]/.../parts[-1]/__init__.py
    pkg_init = repo_root.joinpath(*parts, "__init__.py")
    if pkg_init.exists():
        candidates.append(pkg_init)
    # fallback: try to find any file under repo_root that ends with the module path
    if not candidates:
        for p in repo_root.rglob(parts[-1] + ".py"):
            candidates.append(p)
    return candidates
