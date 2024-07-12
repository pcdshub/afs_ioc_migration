import subprocess
from pathlib import Path

import pytest

from ..lock_repo import AlreadyLockedError, lock_file_repo
from ..rename import RepoInfo


@pytest.fixture(scope="function")
def fake_ready_repo(tmp_path: Path) -> Path:
    """
    Path to something that looks like a standard repo that needs a lock.
    """
    repo = tmp_path / "ioc" / "common" / "fakeioc.git"
    hooks = repo / "hooks"
    hooks.mkdir(parents=True)
    return repo


@pytest.fixture(scope="function")
def fake_not_a_repo(tmp_path: Path):
    """
    Path to something that does not look like a standard repo.
    """
    repo = tmp_path / "asdf" / "asdg" / "what"
    hooks = repo / "hooks"
    hooks.mkdir(parents=True)
    return repo


@pytest.fixture(scope="function")
def fake_already_done_repo(fake_ready_repo: Path) -> Path:
    """
    Path to something that looks like a standard repo that we've already locked.
    """
    lock_file_repo(path=str(fake_ready_repo), org="pcdshub")
    return fake_ready_repo


@pytest.fixture(scope="function")
def fake_already_other_hook_repo(fake_ready_repo: Path) -> Path:
    """
    Path to something that looks like a standard repo that already has a hook.
    """
    already_hook = fake_ready_repo / "hooks" / "pre-receive"
    with already_hook.open("w") as fd:
        fd.write("echo 'locked!'\nexit 1\n")
    return fake_ready_repo


def test_hook_installed(fake_ready_repo: Path):
    expected_hooks = fake_ready_repo / "hooks" / "pre-receive"
    assert not expected_hooks.exists()
    lock_file_repo(path=str(fake_ready_repo), org="pcdshub")
    assert expected_hooks.is_file()


def test_hook_invalid(fake_not_a_repo: Path):
    with pytest.raises(ValueError):
        lock_file_repo(path=str(fake_not_a_repo), org="pcdshub")


def test_hook_already_done(fake_already_done_repo: Path):
    expected_hooks = fake_already_done_repo / "hooks" / "pre-receive"
    assert expected_hooks.exists()
    with pytest.raises(AlreadyLockedError):
        lock_file_repo(path=str(fake_already_done_repo), org="pcdshub")


def test_hook_already_other(fake_already_other_hook_repo: Path):
    expected_hooks = fake_already_other_hook_repo / "hooks" / "pre-receive"
    assert expected_hooks.exists()
    with expected_hooks.open("r") as fd:
        orig_text = fd.read()
    lock_file_repo(path=str(fake_already_other_hook_repo), org="pcdshub")
    assert expected_hooks.exists()
    with expected_hooks.open("r") as fd:
        new_text = fd.read()
    backup_hooks = fake_already_other_hook_repo / "hooks" / "pre-receive.bak.0"
    with backup_hooks.open("r") as fd:
        backup_text = fd.read()
    assert orig_text == backup_text
    assert new_text != orig_text


def test_hook_script(fake_ready_repo: Path):
    lock_file_repo(path=str(fake_ready_repo), org="pcdshub")
    completed_proc = subprocess.run(
        [str(fake_ready_repo / "hooks" / "pre-receive")],
        universal_newlines=True,
        capture_output=True,
    )
    assert completed_proc.returncode == 1
    repo_info = RepoInfo.from_afs(str(fake_ready_repo), org="pcdshub")
    assert repo_info.name in completed_proc.stdout
    assert repo_info.github_ssh in completed_proc.stdout
    assert repo_info.github_url in completed_proc.stdout
    assert repo_info.afs_source in completed_proc.stdout
