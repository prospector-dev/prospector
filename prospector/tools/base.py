import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from prospector.finder import FileFinder
from prospector.message import Message

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig

PEP8_IGNORE_LINE_CODE = re.compile(r"#\s*noqa:([^#]*[^# ])(\s*#.*)?$", re.IGNORECASE)


class ToolBase(ABC):
    @abstractmethod
    def configure(
        self, prospector_config: "ProspectorConfig", found_files: FileFinder
    ) -> Optional[tuple[Optional[Union[str, Path]], Optional[Iterable[Message]]]]:
        """
        Tools have their own way of being configured from configuration files
        on the current path - for example, a .pep8rc file. Prospector will use
        its own configuration settings unless this method discovers some
        tool-specific configuration that should be used instead.

        :return: A tuple: the first element is a string indicating how or where
                 this tool was configured from. For example, this can be a path
                 to the .pylintrc file used, if used. None means that prospector
                 defaults were used. The second element should be an iterable of
                 Message objects representing any issues which were found when
                 trying to load configuration - for example, bad values in a
                 .pylintrc file. It is also possible to simply return None if
                 neither value is useful.
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, found_files: FileFinder) -> list[Message]:
        """
        Actually run the tool and collect the various messages emitted by the tool.
        It is expected that this will convert whatever output of the tool into the
        standard prospector Message and Location objects.
        """
        raise NotImplementedError

    def get_ignored_codes(self, line: str) -> list[str]:
        """
        Return a list of error codes that the tool will ignore from a line of code.
        """
        del line  # unused
        return []
