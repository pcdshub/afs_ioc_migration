import subprocess
from pathlib import Path

import pytest

from ..transfer import migrate_repo


def test_transfer_dry_run(tmp_path: Path):
    try:
        subprocess.run(["git", "config", "--get", "user.name"])
    except subprocess.CalledProcessError:
        pytest.xfail(reason="git user.name and user.email not configured")
    # Basic setup: an afs-ioc-like repo with one commit
    afs_path = tmp_path / "ioc" / "tst" / "dry_run"
    src_path = tmp_path / "repo"

    subprocess.run(["git", "init", str(src_path)])
    subprocess.run(["touch", str(src_path / "some_file.txt")])
    subprocess.run(["git", "add", "some_file.txt"], cwd=str(src_path))
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(src_path))
    subprocess.run(["git", "clone", "--bare", str(src_path), str(afs_path)])

    # Verify that the afs path exists before proceeding
    assert (afs_path / "HEAD").is_file()

    def get_paths(prefix: str | Path) -> list[Path]:
        """
        Retrn a list of the paths that should be created.
        """
        path = Path(prefix)
        return [
            path / ".github" / "ISSUE_TEMPLATE.md",
            path / ".github" / "PULL_REQUEST_TEMPLATE.md",
            path / ".gitignore",
            path / "LICENSE.md",
            path / "README.md",
        ]

    # The source IOC should be missing all the files
    for path in get_paths(src_path):
        assert not path.exists()

    def get_commits(path: str | Path) -> list[str]:
        text = subprocess.check_output(
            ["git", "log", "--pretty=format:%s"], cwd=str(path), universal_newlines=True
        )
        return text.strip().split("\n")

    # The source IOC should only have an initial commit
    assert get_commits(src_path) == ["Initial commit"]

    # With dry run, we assemble a repo and return the path without uploading it
    repo_temp_path = migrate_repo(
        afs_path=str(afs_path), org="pcdshub", dry_run=True, dry_run_dir=str(tmp_path)
    )

    # The temp IOC should have all the new afs_paths
    for path in get_paths(repo_temp_path):
        assert path.exists()

    # The temp IOC should have the initial commit and more
    after_commits = get_commits(repo_temp_path)
    assert "Initial commit" in after_commits
    assert len(after_commits) > 1
