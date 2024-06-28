from pathlib import Path

from .rename import RepoInfo


def lock_file_repo(path: str) -> None:
    """
    Add a pre-recieve hook to a filepath repo to prevent further pushes.

    The intention is to run this prior to the migration so that no new
    changes are introduced during the move to github.
    """
    repo_info = RepoInfo.from_afs(path)
    hooks_dir = Path(repo_info.afs_source) / "hooks"
    if not hooks_dir.is_dir():
        raise ValueError(
            f"{path} is not a valid git repo, it has no hooks subdirectory."
        )
    pre_receive_path = hooks_dir / "pre-recieve"
    if pre_receive_path.exists():
        raise RuntimeError(
            f"There is already a pre-recieve hook at {pre_receive_path}."
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

    with pre_receive_path.open("w") as fd:
        fd.write(filled_hooks)

    pre_receive_path.chmod(0o775)
