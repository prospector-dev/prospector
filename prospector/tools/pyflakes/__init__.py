from typing import TYPE_CHECKING, Any, Optional

from pyflakes.api import checkPath
from pyflakes.messages import Message as FlakeMessage
from pyflakes.reporter import Reporter

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig
__all__ = ("PyFlakesTool",)


# Prospector uses the same pyflakes codes as flake8 defines,
# see https://flake8.pycqa.org/en/latest/user/error-codes.html
# and https://github.com/PyCQA/flake8/blob/e817c63a/src/flake8/plugins/pyflakes.py
_MESSAGE_CODES = {
    "UnusedImport": "F401",
    "ImportShadowedByLoopVar": "F402",
    "ImportStarUsed": "F403",
    "LateFutureImport": "F404",
    "ImportStarUsage": "F405",
    "ImportStarNotPermitted": "F406",
    "FutureFeatureNotDefined": "F407",
    "PercentFormatInvalidFormat": "F501",
    "PercentFormatExpectedMapping": "F502",
    "PercentFormatExpectedSequence": "F503",
    "PercentFormatExtraNamedArguments": "F504",
    "PercentFormatMissingArgument": "F505",
    "PercentFormatMixedPositionalAndNamed": "F506",
    "PercentFormatPositionalCountMismatch": "F507",
    "PercentFormatStarRequiresSequence": "F508",
    "PercentFormatUnsupportedFormatCharacter": "F509",
    "StringDotFormatInvalidFormat": "F521",
    "StringDotFormatExtraNamedArguments": "F522",
    "StringDotFormatExtraPositionalArguments": "F523",
    "StringDotFormatMissingArgument": "F524",
    "StringDotFormatMixingAutomatic": "F525",
    "FStringMissingPlaceholders": "F541",
    "MultiValueRepeatedKeyLiteral": "F601",
    "MultiValueRepeatedKeyVariable": "F602",
    "TooManyExpressionsInStarredAssignment": "F621",
    "TwoStarredExpressions": "F622",
    "AssertTuple": "F631",
    "IsLiteral": "F632",
    "InvalidPrintSyntax": "F633",
    "IfTuple": "F634",
    "BreakOutsideLoop": "F701",
    "ContinueOutsideLoop": "F702",
    "ContinueInFinally": "F703",
    "YieldOutsideFunction": "F704",
    "ReturnWithArgsInsideGenerator": "F705",
    "ReturnOutsideFunction": "F706",
    "DefaultExceptNotLast": "F707",
    "DoctestSyntaxError": "F721",
    "ForwardAnnotationSyntaxError": "F722",
    "CommentAnnotationSyntaxError": "F723",
    "Redefined": "F810",
    "RedefinedWhileUnused": "F811",
    "RedefinedInListComp": "F812",
    "UndefinedName": "F821",
    "UndefinedExport": "F822",
    "UndefinedLocal": "F823",
    "DuplicateArgument": "F831",
    "UnusedVariable": "F841",
    "RaiseNotImplemented": "F901",
}

# The old prospector codes were deprecated in favour of using the codes
# defined by flake8. This maps the old codes to the new codes.
LEGACY_CODE_MAP = {
    "FL0001": "F401",
    "FL0002": "F811",
    "FL0003": "F812",
    "FL0004": "F402",
    "FL0005": "F403",
    "FL0006": "F821",
    "FL0008": "F822",
    "FL0009": "F823",
    "FL0010": "F831",
    "FL0011": "F810",
    "FL0012": "F404",
    "FL0013": "F841",
}


class ProspectorReporter(Reporter):
    def __init__(self, ignore: Optional[list[str]] = None) -> None:
        super().__init__(None, None)
        self._messages: list[Message] = []
        self.ignore = ignore or ()

    def record_message(  # pylint: disable=too-many-arguments
        self,
        filename: str,
        line: Optional[int] = None,
        character: Optional[int] = None,
        code: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        assert message is not None
        assert code is not None

        code = code or "F999"
        if code in self.ignore:
            return

        location = Location(
            path=filename,
            module=None,
            function=None,
            line=line,
            character=character,
        )
        self._messages.append(
            Message(
                source="pyflakes",
                code=code,
                location=location,
                message=message,
            )
        )

    def unexpectedError(self, filename: str, msg: str) -> None:
        self.record_message(
            filename=filename,
            code="F999",
            message=msg,
        )

    # pylint: disable=too-many-arguments
    def syntaxError(self, filename: str, msg: str, lineno: int, offset: int, text: str) -> None:
        self.record_message(
            filename=filename,
            line=lineno,
            character=offset,
            code="F999",
            message=msg,
        )

    def flake(self, message: FlakeMessage) -> None:
        code = _MESSAGE_CODES.get(message.__class__.__name__, "F999")

        self.record_message(
            filename=message.filename,
            line=message.lineno,
            character=(message.col + 1),
            code=code,
            message=message.message % message.message_args,
        )

    def get_messages(self) -> list[Message]:
        return self._messages


class PyFlakesTool(ToolBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.ignore_codes: list[str] = []

    def configure(self, prospector_config: "ProspectorConfig", _: Any) -> None:
        ignores = prospector_config.get_disabled_messages("pyflakes")
        # convert old style to new
        self.ignore_codes = [LEGACY_CODE_MAP.get(code, code) for code in ignores]

    def run(self, found_files: FileFinder) -> list[Message]:
        reporter = ProspectorReporter(ignore=self.ignore_codes)
        for filepath in found_files.python_modules:
            checkPath(str(filepath.absolute()), reporter)

        return reporter.get_messages()
