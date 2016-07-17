import os


def is_virtualenv(path):
    if os.name == 'nt':
        # Windows!
        clues = ('Scripts', 'lib', 'include')
    else:
        clues = ('bin', 'lib', 'include')

    try:
        dircontents = os.listdir(path)
    except (OSError, TypeError):
        # listdir failed, probably due to path length issues in windows
        return False

    if not all([clue in dircontents for clue in clues]):
        # we don't have the 3 directories which would imply
        # this is a virtualenvironment
        return False

    if not all([os.path.isdir(os.path.join(path, clue)) for clue in clues]):
        # some of them are not actually directories
        return False

    # if we do have all three directories, make sure that it's not
    # just a coincidence by doing some heuristics on the rest of
    # the directory
    if len(dircontents) > 7:
        # if there are more than 7 things it's probably not a virtualenvironment
        return False

    return True
