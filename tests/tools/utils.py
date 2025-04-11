from pathlib import Path
from unittest import TestCase

from prospector.finder import FileFinder


class TestCaseWithFiles(TestCase):
    def get_test_files(self, name: str) -> FileFinder:
        return FileFinder(Path(__file__).parent / name)
