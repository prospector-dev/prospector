import hashlib
import json
from typing import Any

from prospector.formatters.base import Formatter

__all__ = ("GitlabFormatter",)


class GitlabFormatter(Formatter):
    """
    This formatter outputs messages in the GitLab Code Quality report format.
    https://docs.gitlab.com/ci/testing/code_quality/#code-quality-report-format
    """

    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        output: list[dict[str, Any]] = []
        fingerprints = set()

        if messages:
            for message in sorted(self.messages):
                # Make sure that we do not get a fingerprint that is already in use
                # by adding in the previously generated one.
                message_hash = ":".join([str(message.location.path), str(message.location.line), message.code])
                sha256_hash = hashlib.sha256(message_hash.encode())
                MAX_ITERATIONS = 1000
                iteration_count = 0
                while sha256_hash.hexdigest() in fingerprints:
                    # In cases of hash collisions, new hashes will be generated.
                    sha256_hash.update(sha256_hash.hexdigest().encode())
                    iteration_count += 1
                    if iteration_count > MAX_ITERATIONS:
                        raise RuntimeError("Maximum iteration limit reached while resolving hash collisions.")

                fingerprint = sha256_hash.hexdigest()
                fingerprints.add(fingerprint)

                output.append(
                    {
                        "type": "issue",
                        "check_name": message.code,
                        "description": f"{message.source}[{message.code}]: {message.message.strip()}",
                        "severity": "major",
                        "location": {
                            "path": str(self._make_path(message.location)),
                            "lines": {"begin": message.location.line, "end": message.location.line_end},
                        },
                        "fingerprint": fingerprint,
                    }
                )

        return json.dumps(output, indent=2)
