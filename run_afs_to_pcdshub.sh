#!/bin/bash
python -m afs_ioc_migration --org pcdshub --dry-run /afs/slac.stanford.edu/g/cd/swe/git/repos/package/epics/ioc/*/*.git /afs/slac.stanford.edu/g/cd/swe/git/repos/package/epics/ioc/xpp/ccm/*.git
