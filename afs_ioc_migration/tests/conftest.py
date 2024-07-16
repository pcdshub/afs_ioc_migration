import subprocess

import pytest


def xfail_git_setup():
    try:
        user = subprocess.check_output(["git", "config", "--get", "user.name"])
        email = subprocess.check_output(["git", "config", "--get", "user.email"])
        ok = user and email
    except subprocess.CalledProcessError:
        ok = False
    if not ok:
        pytest.xfail(reason="git user.name or user.email not configured")
