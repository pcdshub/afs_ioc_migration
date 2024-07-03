from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi
from git import Repo

from .lock_repo import AlreadyLockedError, lock_file_repo
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
        # Note: can also include custom_properties=dict here, but I think I want to import the migration tools and do it later
        gh.repos.create_in_org(org=ORG, name=info.name)

    # Clone from afs to a temporary directory
    with TemporaryDirectory() as dir:
        repo = Repo.init(path=dir, mkdir=False)
        afs_remote = repo.create_remote(name="afs_remote", url=afs_path)
        afs_remote.fetch()
        afs_head = repo.create_head("afs_head", afs_remote.refs.afs_remote)
        afs_head.checkout()

        # Make systemic modifications (.gitignore, license, maybe others)
        # TODO implement these modifications
        # Commit systemic modifications

        # Push to the blank repo
        github_remote = repo.create_remote(name="github_remote", url=info.github_ssh)
        github_remote.push()

    # Apply properties to the repo
