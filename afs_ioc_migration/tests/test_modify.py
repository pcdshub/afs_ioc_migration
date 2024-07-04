from pathlib import Path

from ..modify import add_github_folder, add_gitignore, add_license_file


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
