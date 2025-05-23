from pathlib import Path
from shutil import copy

from .rename import RepoInfo


class AlreadyLockedError(RuntimeError): ...


def lock_file_repo(path: str, org: str) -> None:
    """
    Add a pre-receive hook to a filepath repo to prevent further pushes.

    The intention is to run this prior to the migration so that no new
    changes are introduced during the move to github.
    """
    repo_info = RepoInfo.from_afs(afs_source=path, org=org)
    hooks_dir = Path(repo_info.afs_source) / "hooks"
    if not hooks_dir.is_dir():
        hooks_dir = Path(repo_info.afs_source) / ".git" / "hooks"
        if not hooks_dir.is_dir():
            raise ValueError(
                f"{path} is not a valid git repo, it has no hooks subdirectory."
            )

    template_path = Path(__file__).parent / "hook_template.txt"
    with template_path.open("r") as fd:
        template = fd.read()

    filled_hooks = template.format(
        name=repo_info.name,
        github_url=repo_info.github_url,
        github_ssh=repo_info.github_ssh,
        afs_source=repo_info.afs_source,
    )

    pre_receive_path = hooks_dir / "pre-receive"
    if pre_receive_path.exists():
        with pre_receive_path.open("r") as fd:
            existing = fd.read()
        if filled_hooks == existing:
            raise AlreadyLockedError(
                f"There is already our pre-receive hook at {pre_receive_path}."
            )
        else:
            # Find an available backup name
            for index in range(99):
                backup_path = hooks_dir / f"pre-receive.bak.{index}"
                if not backup_path.exists():
                    copy(pre_receive_path, backup_path)
                    break

    with pre_receive_path.open("w") as fd:
        fd.write(filled_hooks)

    pre_receive_path.chmod(0o775)
