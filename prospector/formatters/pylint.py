import os
import re

from prospector.formatters.base_summary import SummaryFormatter


class PylintFormatter(SummaryFormatter):
    """
    This formatter outputs messages in the same way as pylint -f parseable , which is used by several
    tools to parse pylint output. This formatter is therefore a compatibility shim between tools built
    on top of pylint and prospector itself.
    """

    def render_messages(self) -> list[str]:
        cur_loc = None
        output = []
        for message in sorted(self.messages):
            if cur_loc != message.location.path:
                cur_loc = message.location.path
                module_name = str(self._make_path(message.location)).replace(os.path.sep, ".")
                module_name = re.sub(r"(\.__init__)?\.py$", "", module_name)

                header = f"************* Module {module_name}"
                output.append(header)

            #   ={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}
            # prospector/configuration.py:65: [missing-docstring(missing-docstring), build_default_sources] \
            # Missing function docstring

            template = "%(path)s:%(line)s: [%(code)s(%(source)s), %(function)s] %(message)s"
            output.append(
                template
                % {
                    "path": self._make_path(message.location),
                    "line": message.location.line,
                    "source": message.source,
                    "code": message.code,
                    "function": message.location.function,
                    "message": message.message.strip(),
                }
            )
        return output

    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        output: list[str] = []
        if messages:
            output.extend(self.render_messages())
        if profile:
            output.append("")
            output.append(self.render_profile())
        if summary:
            output.append("")
            output.append(self.render_summary())

        return "\n".join(output)
