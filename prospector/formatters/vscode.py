import os
import re

from prospector.formatters.base_summary import SummaryFormatter


class VSCodeFormatter(SummaryFormatter):
    """
    This formatter outputs messages in the same way as vscode prospector linter expects.
    """

    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        # this formatter will always ignore the summary and profile
        cur_loc = None
        output = []

        for message in sorted(self.messages):
            if cur_loc != message.location.path:
                cur_loc = message.location.path
                module_name = self._make_path(message.location.path).replace(os.path.sep, ".")
                module_name = re.sub(r"(\.__init__)?\.py$", "", module_name)

                header = f"************* Module {module_name}"
                output.append(header)

            template = "%(line)s,%(character)s,%(code)s,%(code)s:%(source)s %(message)s"
            output.append(
                template
                % {
                    "line": message.location.line,
                    "character": message.location.character,
                    "source": message.source,
                    "code": message.code,
                    "message": message.message.strip(),
                }
            )
        if profile:
            output.append("")
            output.append(self.render_profile())
        if summary:
            output.append("")
            output.append(self.render_summary())

        return "\n".join(output)
