from pathlib import Path
from shutil import copy


def add_file(cloned_path: str, source_name: str, dest_name: str) -> Path:
    """Add some sample file to the repo, overriding the destination file."""
    src_path = Path(__file__).parent / source_name
    dst_path = Path(cloned_path) / dest_name
    copy(src_path, dst_path)
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
