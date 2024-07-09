#!/bin/bash
# Transfer a dummy repo to pcdshub to see what happens
#
# Before running this script, set up a GITHUB_TOKEN environment variable
# as described in the afs_ioc_migration.transfer.migrate_repo docstring
#
# This script will:
# - Clone https://github.com/ZLLentz/test_afs_script to a subdirectory ioc/tst/test_afs_script as a bare repo
# - Run the core transfer function afs_ioc_migration.transfer.migrate_repo
#
# After the script runs, check if the repo http://github.com/pcdshub/ioc-tst-test_afs_script gets created
# and check what files it has.
#
# Note that the dummy repo has one commit, two branches, and a tag. All should be transferred.

set -e

THIS_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
TARGET_DIR="${THIS_DIR}"/test_transfer/ioc/tst
TARGET_REPO="${TARGET_DIR}"/test_afs_script.git
mkdir -p "${TARGET_DIR}"
if [ ! -d "${TARGET_REPO}" ]; then
    git clone --bare https://github.com/ZLLentz/test_afs_script "${TARGET_REPO}"
fi

REPO_ROOT="$(realpath "${THIS_DIR}"/../..)"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"
echo $PYTHONPATH

python -c "from afs_ioc_migration.transfer import migrate_repo; migrate_repo('${TARGET_REPO}')"
