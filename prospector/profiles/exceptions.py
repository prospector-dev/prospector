class ProfileNotFound(Exception):
    def __init__(self, name: str, profile_path: str) -> None:
        super().__init__()
        self.name = name
        self.profile_path = profile_path

    def __repr__(self) -> str:
        return "Could not find profile {}; searched in {}".format(
            self.name,
            ":".join(self.profile_path),
        )


class CannotParseProfile(Exception):
    def __init__(self, filepath: str, parse_error: Exception) -> None:
        super().__init__()
        self.filepath = filepath
        self.parse_error = parse_error

    def get_parse_message(self) -> str:
        return "{}\n  on line {} : char {}".format(
            self.parse_error.problem,  # type: ignore[attr-defined]
            self.parse_error.problem_mark.line,  # type: ignore[attr-defined]
            self.parse_error.problem_mark.column,  # type: ignore[attr-defined]
        )

    def __repr__(self) -> str:
        return "Could not parse profile found at %s - it is not valid YAML" % self.filepath
