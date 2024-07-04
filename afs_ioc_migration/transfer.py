from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi
from git import Repo

from .lock_repo import AlreadyLockedError, lock_file_repo
from .modify import add_gitignore, add_license_file
from .rename import ORG, RepoInfo


def migrate_repo(afs_path: str) -> None:
    # Lock the afs repo if it isn't locked
    print(f"Locking afs repo {afs_path}...")
    try:
        lock_file_repo(afs_path)
    except AlreadyLockedError:
        print(f"{afs_path} is already locked, continuing.")
    else:
        print(f"{afs_path} has been locked, continuing.")

    # Get the new name and other info
    info = RepoInfo.from_afs(afs_source=afs_path)

    # Check if the repo is already on github and if it has commits
    gh = GhApi()
    print(f"Checking for existing repo commits at {info.github_url}")
    try:
        gh.repos.get_commits(ORG, info.name)
    except HTTP4xxClientError as exc:
        if exc.code == 404:
            print(f"Repo {info.github_url} does not exist, continuing.")
            repo_exists = False
        elif exc.code == 409:
            print(
                f"Repo {info.github_url} exists but does not have commits, continuing."
            )
            repo_exists = True
        else:
            # Some unknown 4xx http error
            raise
    else:
        raise RuntimeError(f"Repo {info.github_url} exists and has commits, aborting.")

    # Create the blank repo if needed
    if not repo_exists:
        print(f"Creating repository at {info.github_url}")
        gh.repos.create_in_org(
            org=ORG,
            name=info.name,
            custom_properties={
                "repo_type": "EPICS IOC",
                "default": True,
                "master": True,
                "gh_pages": False,
                "status_checks": None,
            },
        )

    # Set repo topics
    gh.repos.replace_all_topics(
        owner=ORG,
        repo=info.name,
        names=[
            "EPICS",
            "IOC",
            "SLAC",
            "LCLS",
        ],
    )

    # Clone from afs to a temporary directory
    with TemporaryDirectory() as dir:
        print(f"Cloning from {afs_path}")
        repo = Repo.init(path=dir, mkdir=False)
        afs_remote = repo.create_remote(name="afs_remote", url=afs_path)
        afs_remote.fetch()
        afs_head = repo.create_head("afs_head", afs_remote.refs.afs_remote)
        afs_head.checkout()

        # Make and commit systemic modifications (.gitignore, license, maybe others)
        print("Adding license file")
        license = add_license_file(cloned_path=dir)
        commit(repo, license, "MAINT: adding standard license file")
        print("Adding gitignore")
        gitignore = add_gitignore(cloned_path=dir)
        commit(repo, gitignore, "MAINT: adding standard gitignore")

        # Push to the blank repo
        print("Pushing repo to github")
        github_remote = repo.create_remote(name="github_remote", url=info.github_ssh)
        github_remote.push()


def commit(repo: Repo, path: Path, msg: str) -> None:
    repo.index.add([str(path)])
    repo.index.write()
    repo.index.commit(msg)
