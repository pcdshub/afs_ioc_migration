from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi
from git import Repo

from .lock_repo import AlreadyLockedError, lock_file_repo
from .modify import add_github_folder, add_gitignore, add_license_file
from .rename import ORG, RepoInfo


class RepoExistsError(RuntimeError): ...


def migrate_repo(afs_path: str) -> None:
    """
    Migrate an afs directory repo to pcdshub.

    Requires you set the $GITHUB_TOKEN environment
    variable to a fine-grained access token with
    the following permissions:

    - Administration: read and write
    - Contents: read and write
    - Custom properties: read and write
    - Metadata: read-only
    """
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
        gh.repos.list_commits(ORG, info.name)
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
        raise RepoExistsError(
            f"Repo {info.github_url} exists and has commits, aborting."
        )

    # Create the blank repo if needed
    if repo_exists:
        print("Repo already exists, skipping creation.")
    else:
        print(f"Creating repository at {info.github_url}")
        gh.repos.create_in_org(
            org=ORG,
            name=info.name,
            custom_properties={
                "type": "EPICS IOC",
                "protect_default": "true",
                "protect_master": "true",
                "protect_gh_pages": "false",
                "required_checks": "None",
            },
        )

    # Set repo topics
    print("Setting standard repo topics")
    gh.repos.replace_all_topics(
        owner=ORG,
        repo=info.name,
        names=[
            "epics",
            "epics-ioc",
        ],
    )

    with TemporaryDirectory() as path:
        # Clone from afs to a temporary directory
        print(f"Cloning HEAD from {afs_path} to {path} as master")
        repo = Repo.init(path=path, mkdir=False)
        afs_remote = repo.create_remote(name="afs_remote", url=afs_path)
        fetch_info = afs_remote.fetch(
            ["*:refs/remotes/afs_remote/*", "refs/tags/*:refs/tags/*"]
        )
        afs_head = repo.create_head("master", afs_remote.refs.HEAD)
        afs_head.checkout()

        # At this point, we have all branches and tags fetched.
        # The working directory is currently even with afs's head
        # The head is now named "master" locally,
        # regardless of whichever strange name it may have upstream.

        # Make and commit systemic modifications (.gitignore, license, maybe others)
        print("Adding license file")
        license = add_license_file(cloned_path=path)
        commit(repo, license, "MAINT: adding standard license file")
        print("Adding gitignore")
        gitignore = add_gitignore(cloned_path=path)
        commit(repo, gitignore, "MAINT: adding standard gitignore")
        print("Adding github templates")
        github_templates = add_github_folder(cloned_path=path)
        commit(repo, github_templates, "MAINT: add github templates")

        # Create a same-named head for every single branch on the afs remote
        for fetch in fetch_info:
            if "afs_remote/refs/heads" in fetch.name:
                print(f"Found branch named {fetch.remote_ref_path}")
                repo.create_head(str(fetch.remote_ref_path), fetch.ref)

        # Push all the heads and all the tags!
        print("Pushing all branches to github")
        github_remote = repo.create_remote(name="github_remote", url=info.github_ssh)
        github_remote.push("*")


def commit(repo: Repo, path: Path, msg: str) -> None:
    repo.index.add([str(path)])
    repo.index.write()
    repo.index.commit(msg)
