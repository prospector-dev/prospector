import os
from pathlib import Path


class FatalProspectorException(Exception):
    """
    Exception used to indicate an internal prospector problem.
    Problems in prospector itself should raise this to notify
    the user directly. Errors in dependent tools should be
    caught and the user notified elegantly.
    """

    # (see also the --die-on-tool-error flag)

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class CouldNotHandleEncoding(Exception):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path


class PermissionMissing(Exception):
    def __init__(self, path: Path):
        docs_url = "https://prospector.landscape.io/en/master/profiles.html#ignoring-paths-and-patterns"
        what = f"directory {path}" if os.path.isdir(path) else f"the file {path}"
        error_msg = (
            f"The current user {os.getlogin()} does not have permission to open "
            f"{what}. Either fix permissions or tell prospector to skip it "
            f"by adding this path to `--ignore-paths` on the commandline "
            f"or in `ignore-paths` in the prospector profile (see {docs_url})"
        )
        super().__init__(error_msg)
