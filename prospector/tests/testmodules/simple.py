
import os


class Checker(object):

    def do_check(self):
        raise NotImplementedError


class FileExistsChecker(Checker):

    def __init__(self, path):
        self._path = path

    def do_check(self):
        return os.path.exists(self._path)


class IsFileChecker(Checker):

    def __init__(self, path):
        self._path = path

    def do_check(self):
        return os.path.isfile(self._path)


def is_path_a_file(path):
    checkers = [FileExistsChecker(path), IsFileChecker(path)]
    check_passed = [ checker.do_check() for checker in checkers ]
    return all(check_passed)
