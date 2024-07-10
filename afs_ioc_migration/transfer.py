import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi
from git import Repo

from .lock_repo import AlreadyLockedError, lock_file_repo
from .modify import add_github_folder, add_gitignore, add_license_file, add_readme_file
from .rename import ORG, RepoInfo

logger = logging.getLogger(__name__)


class RepoExistsError(RuntimeError): ...


def migrate_repo(afs_path: str, dry_run: bool) -> None:
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
    if dry_run:
        logger.info(f"Dry run: skip locking {afs_path}")
    else:
        logger.info(f"Locking afs repo {afs_path}...")
        try:
            lock_file_repo(afs_path)
        except AlreadyLockedError:
            logger.info(f"{afs_path} is already locked, continuing.")
        else:
            logger.info(f"{afs_path} has been locked, continuing.")

    # Get the new name and other info
    info = RepoInfo.from_afs(afs_source=afs_path)

    # Check if the repo is already on github and if it has commits
    gh = GhApi()
    logger.info(f"Checking for existing repo commits at {info.github_url}")
    try:
        gh.repos.list_commits(ORG, info.name)
    except HTTP4xxClientError as exc:
        if exc.code == 404:
            logger.info(f"Repo {info.github_url} does not exist, continuing.")
            repo_exists = False
        elif exc.code == 409:
            logger.info(
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
        logger.info("Repo already exists, skipping creation.")
    elif dry_run:
        logger.info("Dry run: skipping repository creation.")
    else:
        logger.info(f"Creating repository at {info.github_url}")
        gh.repos.create_in_org(
            org=ORG,
            name=info.name,
            visibility="internal",
            custom_properties={
                "type": "EPICS IOC",
                "protect_default": "true",
                "protect_master": "true",
                "protect_gh_pages": "false",
                "required_checks": "None",
            },
        )

    # Set repo topics
    if dry_run:
        logger.info("Dry run: Skip setting standard repo topics")
    else:
        logger.info("Setting standard repo topics")
        gh.repos.replace_all_topics(
            owner=ORG,
            repo=info.name,
            names=[
                "epics",
                "epics-ioc",
                f"ecs-epics-ioc-{info.area}",
            ],
        )

    with TemporaryDirectory() as path:
        if dry_run:
            top_path = Path("afs_ioc_migration_dry_run") / info.name
            top_path.mkdir(exist_ok=True)
            path = top_path / info.name
            path.mkdir(exist_ok=False)
            logger.info("Dry run: create repo in cwd at {path}")
        # Clone from afs to a temporary directory
        logger.info(f"Cloning HEAD from {afs_path} to {path} as master")
        repo = Repo.init(path=path, mkdir=False)
        afs_remote = repo.create_remote(name="afs_remote", url=afs_path)
        fetch_info = afs_remote.fetch(
            ["*:refs/remotes/afs_remote/*", "refs/tags/*:refs/tags/*"]
        )
        logger.info("Checking out HEAD as master")
        afs_head = repo.create_head("master", afs_remote.refs.HEAD)
        afs_head.checkout()

        # At this point, we have all branches and tags fetched.
        # The working directory is currently even with afs's head
        # The head is now named "master" locally,
        # regardless of whichever strange name it may have upstream.

        # Make and commit systemic modifications (.gitignore, license, others)
        logger.info("Adding license file")
        license = add_license_file(cloned_path=path)
        commit(repo, license, "MAINT: adding standard license file")
        logger.info("Adding gitignore")
        gitignore = add_gitignore(cloned_path=path)
        commit(repo, gitignore, "MAINT: adding standard gitignore")
        logger.info("Adding github templates")
        github_templates = add_github_folder(cloned_path=path)
        commit(repo, github_templates, "MAINT: add github templates")
        logger.info("Updating readme")
        new_readme, old_readmes = add_readme_file(cloned_path=path, repo_name=info.name)
        if old_readmes:
            repo.index.remove([str(p) for p in old_readmes])
        commit(repo, new_readme, "MAINT: update readme")

        # Time to push everything
        # Create a same-named head for every single branch on the afs remote
        for fetch in fetch_info:
            if "afs_remote/refs/heads" in fetch.name:
                logger.info(f"Found branch named {fetch.remote_ref_path}")
                repo.create_head(str(fetch.remote_ref_path), fetch.ref)
        if dry_run:
            logger.info("Dry run: skipping github push")
        else:
            logger.info("Pushing all branches and tags to github")
            github_remote = repo.create_remote(
                name="github_remote", url=info.github_ssh
            )
            github_remote.push("*")


def commit(repo: Repo, path: Path, msg: str) -> None:
    repo.index.add([str(path)])
    repo.index.write()
    repo.index.commit(msg)
