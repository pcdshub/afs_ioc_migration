from pathlib import Path
from shutil import copy, copytree
from typing import Any, Callable


def add_file(
    cloned_path: str,
    source_name: str,
    dest_name: str,
    copy_func: Callable[[Path, Path], Any] = copy,
) -> Path:
    """Add some sample file to the repo, overriding the destination file."""
    src_path = Path(__file__).parent / source_name
    dst_path = Path(cloned_path) / dest_name
    copy_func(src_path, dst_path)
    return dst_path


def add_license_file(cloned_path: str) -> Path:
    """Add a standard SLAC license file to the repo."""
    return add_file(
        cloned_path=cloned_path, source_name="sample_license.md", dest_name="LICENSE.md"
    )


def add_gitignore(cloned_path: str) -> Path:
    """Add a standard EPICS IOC gitignore to the repo."""
    return add_file(
        cloned_path=cloned_path,
        source_name="sample_gitignore.txt",
        dest_name=".gitignore",
    )


def add_github_folder(cloned_path: str) -> Path:
    """Add a .github folder with PR and issue templates to the repo."""
    return add_file(
        cloned_path=cloned_path,
        source_name="sample_github_folder",
        dest_name=".github",
        copy_func=copytree,
    )
