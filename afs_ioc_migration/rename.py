import dataclasses
import os.path
import typing

T = typing.TypeVar("T")
ORG = "pcdshub"


@dataclasses.dataclass(frozen=True)
class RepoInfo:
    name: str
    github_url: str
    github_ssh: str
    afs_source: str

    @classmethod
    def from_afs(cls: type[T], afs_source: str) -> T:
        name = rename(afs_source)
        github_url = f"https://github.com/{ORG}/{name}.git"
        github_ssh = f"git@github.com:{ORG}/{name}.git"
        return cls(
            name=name,
            github_url=github_url,
            github_ssh=github_ssh,
            afs_source=afs_source,
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
    """
    # Split the old path and take the last 3
    location, git_repo = os.path.split(old_path)
    iocs_path, area = os.path.split(location)
    _, ioc_literal = os.path.split(iocs_path)

    # check for "ioc" and one of the "afs_areas"
    if ioc_literal != "ioc":
        raise ValueError(f"{old_path} is not a valid afs ioc path.")
    if area not in afs_areas:
        raise ValueError(f"{old_path} has non-ecs area {area}")

    # bring it all together
    return "-".join(
        (ioc_literal, area_renames.get(area, area), git_repo.removesuffix(".git"))
    )
