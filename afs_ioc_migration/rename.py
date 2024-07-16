import dataclasses
import typing
from pathlib import Path

T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True)
class RepoInfo:
    """
    Information about where an AFS repository will be transferred.
    """

    name: str
    github_url: str
    github_ssh: str
    afs_source: str
    area: str

    @classmethod
    def from_afs(cls: type[T], afs_source: str, org: str) -> T:
        """
        Create a RepoInfo instance given the pull path to the afs source.
        """
        name = rename(afs_source)
        area = name.split("-")[1]
        github_url = f"https://github.com/{org}/{name}.git"
        github_ssh = f"git@github.com:{org}/{name}.git"
        return cls(
            name=name,
            github_url=github_url,
            github_ssh=github_ssh,
            afs_source=afs_source,
            area=area,
        )


afs_areas = [
    "common",
    "cxi",
    "det",
    "fee",
    "hfx",
    "hpl",
    "kfe",
    "las",
    "lfe",
    "mec",
    "mfx",
    "rix",
    "rixs",
    "sxr",
    "tmo",
    "tst",
    "txi",
    "ued",
    "xcs",
    "xpp",
    "xrt",
]

area_renames = {
    "rixs": "rix",
}


def rename(old_path: str) -> str:
    """
    Given an old path or partial path to an afs repository, get the new name.

    The intent is to flatten filepath structures like so:

    - /some/long/path/ioc/common/gigECam.git -> ioc-common-gigECam

    We also support one layer deeper because it exists for some reason
    - /some/long/path/ioc/xpp/ccm/piMotion.git -> ioc-xpp-ccm-piMotion
    """
    # Split the old path and take the last 3
    path = Path(old_path).resolve()
    if path.parts[-3] == "ioc":
        ioc_literal = path.parts[-3]
        area = path.parts[-2]
        git_repo = path.parts[-1]
    elif path.parts[-4] == "ioc":
        ioc_literal = path.parts[-4]
        area = path.parts[-3]
        git_repo = "-".join(path.parts[-2:])
    else:
        raise ValueError(f"{old_path} is not a valid afs ioc path.")

    # check for "ioc" and one of the "afs_areas"
    if ioc_literal != "ioc":
        raise ValueError(f"{ioc_literal} is not the ioc literal (somehow??).")
    if area not in afs_areas:
        raise ValueError(f"{old_path} has non-ecs area {area}")

    # bring it all together
    return "-".join(
        (ioc_literal, area_renames.get(area, area), git_repo.removesuffix(".git"))
    )
