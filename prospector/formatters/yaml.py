import yaml

from prospector.formatters.base import Formatter

__all__ = ("YamlFormatter",)


# pylint: disable=too-few-public-methods
class YamlFormatter(Formatter):
    def render(self, summary=True, messages=True, profile=False, paths_relative_to=None):
        output = {}

        if summary:
            output["summary"] = self.summary

        if profile:
            output["profile"] = self.profile.as_dict()

        if messages:
            output["messages"] = [self._message_to_dict(m, paths_relative_to) for m in self.messages]

        return yaml.safe_dump(
            output,
            indent=2,
            default_flow_style=False,
            allow_unicode=True,
        )
