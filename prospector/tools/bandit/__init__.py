from typing import TYPE_CHECKING, Any, Optional

from bandit.cli.main import _get_profile, _init_extensions
from bandit.core import docs_utils
from bandit.core.config import BanditConfig
from bandit.core.constants import RANKING
from bandit.core.manager import BanditManager

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


class BanditTool(ToolBase):
    manager: Optional[BanditManager] = None
    profile: Optional[str] = None
    config_file: Optional[str] = None
    agg_type = "file"
    severity = 0
    confidence = 0

    def configure(self, prospector_config: "ProspectorConfig", _: Any) -> None:
        options = prospector_config.tool_options("bandit")

        if "profile" in options:
            self.profile = options.pop("profile")

        if "config" in options:
            self.config_file = options.pop("config")

        if "severity" in options:
            self.severity = options.pop("severity")
            if not 0 <= self.severity <= 2:
                raise ValueError(f"severity {self.severity!r} must be between 0 and 2")

        if "confidence" in options:
            self.confidence = options.pop("confidence")
            if not 0 <= self.confidence <= 2:
                raise ValueError(f"confidence {self.confidence!r} must be between 0 and 2")

        b_conf = BanditConfig(config_file=self.config_file)
        disabled_messages = prospector_config.get_disabled_messages("bandit")
        if disabled_messages:
            b_conf.config.setdefault("skips", []).extend(disabled_messages)
        if options:
            b_conf.config.update(options)
            b_conf.validate(path="<prospector config>")
        profile = _get_profile(b_conf, self.profile, self.config_file)
        extension_mgr = _init_extensions()
        extension_mgr.validate_profile(profile)

        self.manager = BanditManager(b_conf, None, profile=profile)

    def run(self, found_files: FileFinder) -> list[Message]:
        assert self.manager is not None

        self.manager.files_list = sorted(found_files.files)
        self.manager.exclude_files = []

        if not self.manager.b_ts.tests:
            raise ValueError("No test will run for bandit")

        self.manager.run_tests()
        results = self.manager.get_issue_list(sev_level=RANKING[self.severity], conf_level=RANKING[self.confidence])
        messages = []
        for result in results:
            loc = Location(
                result.fname,
                None,
                "",
                result.lineno,
                result.col_offset,
                line_end=result.linerange[-1] if result.linerange else result.lineno,
                character_end=result.end_col_offset,
            )
            msg = Message("bandit", result.test_id, loc, result.text, doc_url=docs_utils.get_url(result.test_id))
            messages.append(msg)
        return messages
