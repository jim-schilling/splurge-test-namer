"""Utility helpers for safe filesystem operations.

This module exposes a small set of helpers for reading and writing files,
performing safe renames with validation, and recursively globbing files.
These helpers centralize error handling and raise domain-specific
exceptions defined in :mod:`splurge_test_namer.exceptions`.

Copyright (c) 2025 Jim Schilling
License: MIT
"""

from pathlib import Path
import importlib.util
import logging
from splurge_test_namer.exceptions import (
    FileReadError,
    FileWriteError,
    FileRenameError,
    FileGlobError,
)


LOGGER = logging.getLogger(__name__)


def configure_logging(verbose: bool = False, debug: bool = False) -> None:
    """Configure module logging level from CLI verbosity.

    Args:
        verbose: When True, sets level to INFO.
        debug: When True, sets level to DEBUG and includes filename:lineno.
    """
    # Priority: debug > verbose > default(INFO)
    if debug:
        level = logging.DEBUG
        fmt = "%(levelname)s: %(filename)s:%(lineno)d: %(message)s"
    elif verbose:
        level = logging.INFO
        fmt = "%(levelname)s: %(message)s"
    else:
        level = logging.WARNING
        fmt = "%(levelname)s: %(message)s"
    # Configure basic logging once (idempotent for simple CLI runs)
    logging.basicConfig(level=level, format=fmt)


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

    # If still not found, attempt to resolve via importlib (installed packages
    # or modules available on sys.path). This avoids importing the module code;
    # we only inspect the import spec to discover source file locations.
    if not candidates:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec:
                # If spec.origin points to a file, add it
                if spec.origin and spec.origin != "namespace":
                    candidates.append(Path(spec.origin))
                # If it's a package, prefer __init__.py inside submodule_search_locations
                if spec.submodule_search_locations:
                    for loc in spec.submodule_search_locations:
                        init = Path(loc) / "__init__.py"
                        if init.exists():
                            candidates.append(init)
        except Exception:
            # Be conservative — silently ignore resolution failures
            pass

    # Final fallback: search the working directory for a file that matches the
    # dotted module path. This helps in monorepo or workspace layouts where the
    # package might not be under the provided repo_root but is present in the
    # workspace.
    if not candidates:
        try:
            cwd = Path.cwd()
            file_candidate = cwd.joinpath(*parts).with_suffix(".py")
            if file_candidate.exists():
                candidates.append(file_candidate)
            else:
                # as a last resort, search for any file ending with the module name
                for p in cwd.rglob(parts[-1] + ".py"):
                    candidates.append(p)
        except Exception:
            pass

    # Log resolution outcome for debugging
    try:
        logger = logging.getLogger(__name__)
        if candidates:
            logger.debug(
                "resolve_module_to_paths: module '%s' resolved to %s", module_name, [str(p) for p in candidates]
            )
        else:
            logger.debug("resolve_module_to_paths: module '%s' not found under repo_root or sys.path", module_name)
    except Exception:
        # Keep resolver robust even if logging fails
        pass

    return candidates


def resolve_module_to_paths_with_member_fallback(module_name: str, repo_root: Path) -> list[Path]:
    """Resolve module paths, with fallback to strip trailing attributes.

    When callers present dotted names that include a class or attribute
    (e.g. 'pkg.module.Class'), try progressively stripping the last component
    and re-resolving until a file is found or only the top-level package
    remains.
    """
    base = module_name
    while base:
        paths = resolve_module_to_paths(base, repo_root)
        if paths:
            return paths
        if "." not in base:
            break
        base = base.rsplit(".", 1)[0]
    return []
