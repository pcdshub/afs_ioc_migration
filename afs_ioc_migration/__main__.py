import argparse
import dataclasses
import glob
import logging
import sys

from .transfer import migrate_repo

logger = logging.getLogger("afs_ioc_migration")


@dataclasses.dataclass
class MainArgs:
    stop_on_error: bool = False
    dry_run: bool = False
    paths: tuple[str, ...] = ()


parser = argparse.ArgumentParser("afs_ioc_migration")
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
    "paths",
    action="store",
    nargs="+",
    type=tuple,
    help="Paths to the .git file bare repositories to migrate. Accepts specific filenames and globs.",
)


def main(args: MainArgs) -> int:
    n_errors = 0
    for user_glob in args.paths:
        for user_path in glob.glob(user_glob):
            logger.info(f"Migrating {user_path} with dry_run={args.dry_run}")
            try:
                migrate_repo(afs_path=user_path, dry_run=args.dry_run)
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
    sys.exit(main(args))
