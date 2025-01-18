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

            #   ={path}:{line}:{character}: [{msg_id}({symbol}), {obj}] {msg}
            # prospector/configuration.py:65:1: [missing-docstring(missing-docstring), build_default_sources] \
            # Missing function docstring

            template_location = (
                ""
                if message.location.path is None
                else "%(path)s"
                if message.location.line is None
                else "%(path)s:%(line)s"
                if message.location.character is None
                else "%(path)s:%(line)s:%(character)s"
            )
            template_code = (
                "(%(source)s)"
                if message.code is None
                else "%(code)s(%(source)s)"
                if message.location.function is None
                else "[%(code)s(%(source)s), %(function)s]"
            )
            template = (
                f"{template_location}: {template_code}: %(message)s"
                if template_location
                else f"{template_code}: %(message)s"
            )

            message_str = message.message.strip()
            if message.doc_url:
                message_str += f" (See: {message.doc_url})"
            output.append(
                template
                % {
                    "path": self._make_path(message.location),
                    "line": message.location.line,
                    "character": message.location.character,
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
