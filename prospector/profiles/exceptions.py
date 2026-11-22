from pathlib import Path


class ProfileNotFound(Exception):
    def __init__(self, name: str, profile_path: list[Path]) -> None:
        super().__init__()
        self.name = name
        self.profile_path = profile_path

    def __repr__(self) -> str:
        return "Could not find profile {}; searched in {}".format(
            self.name,
            ":".join(map(str, self.profile_path)),
        )


class CannotParseProfile(Exception):
    def __init__(self, filepath: str, parse_error: Exception) -> None:
        super().__init__()
        self.filepath = filepath
        self.parse_error = parse_error

    @property
    def file_format(self) -> str:
        return "TOML" if str(self.filepath).endswith(".toml") else "YAML"

    def get_parse_message(self) -> str:
        if not hasattr(self.parse_error, "problem_mark"):
            # TOML errors already carry their position in the message
            return str(self.parse_error)
        return (
            f"{self.parse_error.problem}\n"  # type: ignore[attr-defined]
            f"  on line {self.parse_error.problem_mark.line}: "
            f"char {self.parse_error.problem_mark.column}"
        )

    def __repr__(self) -> str:
        return f"Could not parse profile found at {self.filepath} - it is not valid {self.file_format}"
