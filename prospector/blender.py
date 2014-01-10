# This module contains the logic for "blending" of errors.
# Since prospector runs multiple tools with overlapping functionality, this module
# exists to merge together equivalent warnings from different tools for the same
# line. For example, both pyflakes and pylint will generate an "Unused Import"
# warning on the same line. This is obviously redundant, so we remove duplicates.
from collections import defaultdict

BLEND = (
    (  # Unused Import
        ('pylint', 'W0611'),
        ('pyflakes', 'FL0001')
    ),
    (  # Syntax Error
        # prefer this error as it will highlight diffs, but not be present for syntax errors not caused by diffs
        ('dodgy', 'diff'),
        ('pylint', 'E0001'),
        ('pyflakes', 'FL9998'),
        ('pep8', 'E901'),
        ('mccabe', 'MC0000')
    ),
    (  # Undefined local variable
        ('pylint', 'E0602'),
        ('pyflakes', 'FL0006')
    ),
    (  # Unused variable
        ('pylint', 'W0612'),
        ('pyflakes', 'FL0013'),
    ),
    (  # Mixed tabs and spaces
        ('pep8', 'E101'),
        ('pylint', 'W0313')
    ),
    (  # Import from __future__ not first import
        ('pylint', 'W0410'),
        ('pyflakes', 'FL0012')
    ),
    (  # Line too long
        ('pep8', 'E501'),
        ('pylint', 'C0301')
    ),
    (  # Trailing whitespace
        ('pep8', 'W291'),
        ('pylint', 'C0303'),
    ),
    (  # No newline at end of file
        ('pep8', 'W292'),
        ('pylint', 'C0304')
    ),
    (  # line ends with semi-colon
        ('pep8', 'E703'),
        ('pylint', 'W0301')
    ),
    (  # multiple statements on one line
        ('pep8', 'E702'),
        ('pylint', 'C0321')
    ),
    (  # incorrect indendation
        ('pep8', 'E111'),
        ('pylint', 'W0311')
    ),
    (  # comma not followed by a space
        ('pep8', 'E231'),
        ('pylint', 'C0324')
    ),
    (  # missing whitespace around operator
        ('pep8', 'E225'),
        ('pylint', 'C0322')
    ),
    (  # missing whitespace around operator
        ('pep8', 'E225'),
        ('pylint', 'C0323')
    ),
    (  # undefined name in __all__
        ('pylint', 'E0603'),
        ('pyflakes', 'FL0008')
    ),
    (  # duplicate argument in function definition
        ('pylint', 'E0108'),
        ('pyflakes', 'FL0010')
    ),
    (  # redefinition of unused function
        ('pyflakes', 'FL0002'),
        ('pylint', 'E0102'),
    )
)

# BLEND is a list of tuples of codes to merge together. The earlier codes will
# take priority, so if all are found, only the first one will be left after blending.
#
# Note that since not all tools will necessarily be run, the first message for a line
# as sorted by the code list will be the one remaining after blending.


def blend_line(messages, blend_combos=BLEND):
    """
    Given a list of messages on the same line, blend them together so that we end
    up with one message per actual problem. Note that we can still return more than
    one message here if there are two or more different errors for the line.
    """
    blend_lists = [[] for _ in range(len(blend_combos))]
    blended = []

    # first we split messages into each of the possible blendable categories
    # so that we have a list of lists of messages which can be blended together
    for message in messages:
        key = (message.source, message.code)
        found = False
        for blend_combo_idx, blend_combo in enumerate(blend_combos):
            if key in blend_combo:
                found = True
                blend_lists[blend_combo_idx].append(message)

        # note: we use 'found=True' here rather than a simple break/for-else because
        # this allows the same message to be put into more than one 'bucket'. This means
        # that the same message from pep8 can 'subsume' two from pylint, for example.

        if not found:
            # if we get here, then this is not a message which can be blended,
            # so by definition is already blended
            blended.append(message)

    # we should now have a list of messages which all represent the same
    # problem on the same line, so we will sort them according to the priority
    # in BLEND and pick the first one
    for blend_combo_idx, blend_list in enumerate(blend_lists):
        if len(blend_list) == 0:
            continue
        blend_list.sort(key=lambda msg: blend_combos[blend_combo_idx].index((msg.source, msg.code)))
        blended.append(blend_list[0])

    return blended


def blend(messages, blend_combos=BLEND):
    # group messages by file and then line number
    msgs_grouped = defaultdict(lambda: defaultdict(list))

    for message in messages:
        msgs_grouped[message.location.path][message.location.line].append(message)

    # now blend together all messages on the same line
    out = []
    for by_line in msgs_grouped.values():
        for messages_on_line in by_line.values():
            out += blend_line(messages_on_line, blend_combos)

    return out
