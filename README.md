# AFS to GitHub IOC Migration

This repo is a collection of scripts intended to migrate LCLS repositories from the local AFS filesystem to GitHub.

The AFS filesystem is scheduled for imminent removal, so we need to migrate. Migrating to GitHub brings these repositories in-line with our other codebases.

## Usage
There is a top-level run_afs_to_pcdshub.sh script that performs a dry-run of the exact migration we intend to perform. When I use this for the real migration, I will simply edit this script to remove the --dry-run flag.

For more specific usage or testing, try "python -m afs_ioc_migration --help".

In order to use the github API, you'll need to create a fine-grained access token with access to all repositories in the target github organization with at least the following scopes:

- Administration: read and write
- Contents: read and write
- Custom properties: read and write
- Metadata: read-only

Then, you'll need to set the GITHUB_TOKEN environment variable to this access token. Then, the script will use your authentication to create the new repositories.

## What it does

- Locks the afs repo so it can't be pushed to any longer
- Creates a GitHub repo with an appropriate name and topics
- Add/modify the repo's license, gitignore, readme, and .github folder as appropriate.
- Push all branches and all tags to the GitHub repo
