"""util_helpers.py
Safe file operations for reading, writing, renaming, and rglob."""

from pathlib import Path
from splurge_test_namer.exceptions import FileReadError, FileWriteError, FileRenameError, FileGlobError
from typing import List
import logging

LOGGER = logging.getLogger(__name__)


def configure_logging(verbose: bool = False) -> None:
    """Configure module logging level from CLI verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


DOMAINS = ["utils"]


def safe_file_reader(path: Path, encoding: str = "utf-8") -> str:
    """Safely read file contents, raising FileReadError on error."""
    try:
        return path.read_text(encoding=encoding)
    except Exception as e:
        raise FileReadError(f"Failed to read file: {path}") from e


def safe_file_writer(path: Path, data: str, encoding: str = "utf-8") -> None:
    """Safely write data to file, raising FileWriteError on error."""
    try:
        path.write_text(data, encoding=encoding)
    except Exception as e:
        raise FileWriteError(f"Failed to write file: {path}") from e


def safe_file_renamer(src: Path, dst: Path) -> None:
    """Safely rename src to dst, raising FileRenameError on error."""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.replace(dst)
    except Exception as e:
        raise FileRenameError(f"Failed to rename {src} to {dst}") from e


def safe_file_rglob(root: Path, pattern: str) -> List[Path]:
    """Safely perform rglob, raising FileGlobError on error."""
    try:
        return list(root.rglob(pattern))
    except Exception as e:
        raise FileGlobError(f"Failed to rglob {pattern} in {root}") from e


def resolve_module_to_paths(module_name: str, repo_root: Path) -> List[Path]:
    """Resolve a dotted module name to candidate file paths inside repo_root.

    Prefer module.py, then module/__init__.py. Returns empty list if nothing found.
    """
    parts = module_name.split(".")
    candidates: List[Path] = []
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
            # ensure that the file path contains the module's parent directories (best-effort)
            candidates.append(p)
    return candidates
