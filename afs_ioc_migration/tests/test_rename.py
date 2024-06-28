from __future__ import annotations

import pytest

from ..rename import rename


@pytest.mark.parametrize(
    "old,new",
    [
        (
            "/afs/slac/g/cd/swe/git/repos/package/epics/ioc/common/ims.git",
            "ioc-common-ims",
        ),
        (
            "/afs/slac/g/cd/swe/git/repos/package/epics/ioc/common/ads-ioc.git",
            "ioc-common-ads-ioc",
        ),
        (
            "/afs/slac/g/cd/swe/git/repos/package/epics/ioc/xcs/gigECam.git",
            "ioc-xcs-gigECam",
        ),
        (
            "/afs/slac/g/cd/swe/git/repos/package/epics/ioc/rixs/thermotek.git",
            "ioc-rix-thermotek",
        ),
        ("/some/random/path", ValueError),
        (
            "/afs/slac/g/cd/swe/git/repos/package/epics/ioc/lcls/accelerator_thing.git",
            ValueError,
        ),
    ],
)
def test_rename(old: str, new: str | type[Exception]):
    if isinstance(new, str):
        assert rename(old) == new
    elif issubclass(new, Exception):
        with pytest.raises(new):
            rename(old)
    else:
        raise TypeError(f"Unexpect type in test_rename, {new} is {type(new)}")
