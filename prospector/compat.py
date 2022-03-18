from pathlib import Path


def is_relative_to(relpath: Path, otherpath: Path) -> bool:
    # is_relative_to was only added to Path in Python 3.9
    if hasattr(relpath, "is_relative_to"):
        return relpath.is_relative_to(otherpath)

    try:
        relpath.relative_to(otherpath)
    except ValueError:
        return False
    else:
        return True
