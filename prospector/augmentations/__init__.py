from pylint.checkers.base import BasicChecker, astroid
from pylint_plugin_utils import augment_visit


def allow_attribute_comments(chain, node):
    """
    This augmentation is to allow comments on class attributes, for example:

    class SomeClass(object):
        some_attribute = 5
        ''' This is a docstring for the above attribute '''
    """
    if isinstance(node.previous_sibling(), astroid.Assign) and \
            isinstance(node.parent, astroid.Class) and \
            isinstance(node.value.value, basestring):
        return
    chain()


def apply_augmentations(linter):
    augment_visit(linter, BasicChecker.visit_discard, allow_attribute_comments)