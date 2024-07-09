from os import remove
from pathlib import Path
from shutil import copy, copytree
from typing import Any, Callable

import jinja2


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


def add_readme_file(cloned_path: str, repo_name: str) -> tuple[Path, list[Path]]:
    """
    Create a standard README.md.

    The contents of the readme will be:
    - Title with the repo name
    - Explanation that this is an EPICS IOC used at LCLS
    - The original contents of each pre-existing readme in the repo.

    See also readme_template.md for the template used.

    Returns a tuple of the new file and a list of the removed files, if any.
    If no file was removed, the second tuple element will be an empty list.
    """
    dst_path = Path(cloned_path) / "README.md"

    if dst_path.exists():
        raise RuntimeError(f"{dst_path} already exists.")

    # Find all other existing readme-like file to include
    original_paths = sorted(
        list(Path(cloned_path).glob("*readme*", case_sensitive=False))
    )
    original_readmes = []
    for path in original_paths:
        # Should either be one result or zero
        with path.open("r") as fd:
            original_readmes.append(fd.read())

    jinja_loader = jinja2.FileSystemLoader(Path(__file__).parent)
    jinja_env = jinja2.Environment(
        loader=jinja_loader,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template("readme_template.md")
    output_text = template.render(
        repo_name=repo_name,
        original_readme_info=list(
            zip([path.name for path in original_paths], original_readmes)
        ),
    )

    with dst_path.open("w") as fd:
        fd.write(output_text)

    if original_paths:
        for path in original_paths:
            remove(path)
    return dst_path, original_paths
