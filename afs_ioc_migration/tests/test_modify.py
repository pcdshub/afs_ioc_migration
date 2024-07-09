from pathlib import Path

import pytest

from ..modify import add_github_folder, add_gitignore, add_license_file, add_readme_file


def test_add_license_file(tmp_path: Path):
    path = add_license_file(str(tmp_path))
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "LICENSE.md"
    with (Path(__file__).parent.parent / "sample_license.md").open("r") as fd:
        expected_contents = fd.read()
    with path.open("r") as fd:
        actual_contents = fd.read()
    assert actual_contents == expected_contents


def test_add_gitignore(tmp_path: Path):
    path = add_gitignore(str(tmp_path))
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == ".gitignore"
    with (Path(__file__).parent.parent / "sample_gitignore.txt").open("r") as fd:
        expected_contents = fd.read()
    with path.open("r") as fd:
        actual_contents = fd.read()
    assert actual_contents == expected_contents


def test_add_github_folder(tmp_path: Path):
    path = add_github_folder(str(tmp_path))
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == ".github"
    for filename in ("ISSUE_TEMPLATE.md", "PULL_REQUEST_TEMPLATE.md"):
        sample_path = Path(__file__).parent.parent / "sample_github_folder" / filename
        with sample_path.open("r") as fd:
            expected_contents = fd.read()
        with (path / filename).open("r") as fd:
            actual_contents = fd.read()
        assert actual_contents == expected_contents


def test_add_readme_file_none_existing(tmp_path: Path):
    path, _ = add_readme_file(str(tmp_path), "test_name")
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "README.md"
    with path.open("r") as fd:
        contents = fd.read()
    assert "test_name" in contents
    assert "EPICS IOC" in contents
    assert "Original README" not in contents


def test_add_readme_file_already_existing(tmp_path: Path):
    with (tmp_path / "README.md").open("w") as fd:
        fd.write("words")
    with pytest.raises(RuntimeError):
        add_readme_file(str(tmp_path), "test_name")


def test_add_readme_file_include_old(tmp_path: Path):
    old_readme_text = "very unique test text will not collide"
    old_readme_path = tmp_path / "README"
    with old_readme_path.open("w") as fd:
        fd.write(old_readme_text)
    assert old_readme_path.exists()
    path, old_path = add_readme_file(str(tmp_path), "test_name")
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "README.md"
    assert old_path == old_readme_path
    assert not old_path.exists()
    with path.open("r") as fd:
        contents = fd.read()
    assert "test_name" in contents
    assert "EPICS IOC" in contents
    assert "Original README" in contents
    assert old_readme_text in contents
