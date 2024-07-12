import argparse
import dataclasses
import glob
import logging
import sys
import time
from typing import Iterable

from .transfer import migrate_repo

logger = logging.getLogger("afs_ioc_migration")


@dataclasses.dataclass
class MainArgs:
    org: str = ""
    stop_on_error: bool = False
    dry_run: bool = False
    verbose: bool = False
    paths: Iterable[str] = ()


parser = argparse.ArgumentParser(
    "afs_ioc_migration",
    description="Migrate afs filesystem EPICS IOC repositories to GitHub.",
)
parser.add_argument(
    "--org",
    action="store",
    default="pcdshub",
    help="The name of the github organization to migrate repositories to.",
)
parser.add_argument(
    "--stop-on-error",
    action="store_true",
    help="If provided, we'll stop at the first error instead of proceeding to the next file.",
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="If provided, we won't make any real changes to the afs or github areas, and we'll prepare the repo clones in the user's current directory for inspection.",
)
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Show additional debug statements",
)
parser.add_argument(
    "paths",
    action="store",
    nargs="+",
    help="Paths to the .git file bare repositories to migrate. Accepts specific filenames and globs.",
)


def main(args: MainArgs) -> int:
    first_loop = True
    n_errors = 0
    for user_glob in args.paths:
        for user_path in glob.glob(user_glob):
            if first_loop:
                first_loop = False
            else:
                # Slightly pace out the migrations to help avoid API rate limits
                # Github recommends waiting 1s between mutative requests
                # We make 2 mutative requests per call (create repo, replace topics)
                # So, we sleep 2 seconds
                logger.debug("Sleeping 2s to avoid rate limits")
                time.sleep(2)
            logger.info(
                f"Migrating {user_path} to org={args.org} with dry_run={args.dry_run}"
            )
            try:
                migrate_repo(afs_path=user_path, org=args.org, dry_run=args.dry_run)
            except Exception:
                if args.stop_on_error:
                    raise
                else:
                    logger.exception(f"Exception while transferring {user_path}")
                n_errors += 1

    return n_errors


if __name__ == "__main__":
    args = MainArgs()
    parser.parse_args(namespace=args)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
