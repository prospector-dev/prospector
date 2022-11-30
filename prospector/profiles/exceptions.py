class ProfileNotFound(Exception):
    def __init__(self, name, profile_path):
        super().__init__()
        self.name = name
        self.profile_path = profile_path

    def __repr__(self):
        return "Could not find profile {}; searched in {}".format(
            self.name,
            ":".join(self.profile_path),
        )


class CannotParseProfile(Exception):
    def __init__(self, filepath, parse_error):
        super().__init__()
        self.filepath = filepath
        self.parse_error = parse_error

    def get_parse_message(self):
        return "{}\n  on line {} : char {}".format(
            self.parse_error.problem,
            self.parse_error.problem_mark.line,
            self.parse_error.problem_mark.column,
        )

    def __repr__(self):
        return "Could not parse profile found at %s - it is not valid YAML" % self.filepath
