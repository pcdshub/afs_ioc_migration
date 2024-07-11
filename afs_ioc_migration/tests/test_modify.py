from pathlib import Path

import pytest

from ..modify import add_github_folder, add_gitignore, add_license_file, add_readme_file
from ..rename import RepoInfo


@pytest.fixture(scope="function")
def repo_info() -> RepoInfo:
    return RepoInfo.from_afs(
        afs_source="/fake/path/ioc/tst/pytester.git", org="pcdshub"
    )


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


def test_add_readme_file_none_existing(tmp_path: Path, repo_info: RepoInfo):
    path, _ = add_readme_file(str(tmp_path), repo_info)
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "README.md"
    with path.open("r") as fd:
        contents = fd.read()
    assert repo_info.name in contents
    assert repo_info.afs_source in contents
    assert "EPICS IOC" in contents
    assert "Original" not in contents


def test_add_readme_file_already_existing(tmp_path: Path, repo_info: RepoInfo):
    with (tmp_path / "README.md").open("w") as fd:
        fd.write("words")
    with pytest.raises(RuntimeError):
        add_readme_file(str(tmp_path), repo_info)


def test_add_readme_file_include_old(tmp_path: Path, repo_info: RepoInfo):
    old_readme_text1 = "very unique test text will not collide"
    old_readme_text2 = "another very unique test text wow"
    old_readme_path1 = tmp_path / "README"
    old_readme_path2 = tmp_path / "readme.txt"
    with old_readme_path1.open("w") as fd:
        fd.write(old_readme_text1)
    assert old_readme_path1.exists()
    with old_readme_path2.open("w") as fd:
        fd.write(old_readme_text2)
    assert old_readme_path2.exists()
    path, old_paths = add_readme_file(str(tmp_path), repo_info)
    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "README.md"
    assert old_paths[0] == old_readme_path1
    assert old_paths[1] == old_readme_path2
    assert not old_readme_path1.exists()
    assert not old_readme_path2.exists()
    with path.open("r") as fd:
        contents = fd.read()
    assert repo_info.name in contents
    assert repo_info.afs_source in contents
    assert "Original" in contents
    assert old_readme_text1 in contents
    assert old_readme_text2 in contents
    assert "# README" in contents
    assert "# readme.txt" in contents
