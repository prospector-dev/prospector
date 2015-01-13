# This module contains the logic for "blending" of errors.
# Since prospector runs multiple tools with overlapping functionality, this
# module exists to merge together equivalent warnings from different tools for
# the same line. For example, both pyflakes and pylint will generate an
# "Unused Import" warning on the same line. This is obviously redundant, so we
# remove duplicates.
from collections import defaultdict

import pkg_resources
import yaml


__all__ = (
    'blend',
    'BLEND_COMBOS',
)


def blend_line(messages, blend_combos=None):
    """
    Given a list of messages on the same line, blend them together so that we
    end up with one message per actual problem. Note that we can still return
    more than one message here if there are two or more different errors for
    the line.
    """
    blend_combos = blend_combos or BLEND_COMBOS
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

        # note: we use 'found=True' here rather than a simple break/for-else
        # because this allows the same message to be put into more than one
        # 'bucket'. This means that the same message from pep8 can 'subsume'
        # two from pylint, for example.

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
        blend_list.sort(
            key=lambda msg: blend_combos[blend_combo_idx].index(
                (msg.source, msg.code),
            ),
        )
        if blend_list[0] not in blended:
            # We may have already added this message if it represents
            # several messages in other tools which are not being run -
            # for example, pylint missing-docstring is blended with pep257 D100, D101
            # and D102, but should not appear 3 times!
            blended.append(blend_list[0])

        # Some messages from a tool point out an error that in another tool is handled by two
        # different errors or more. For example, pylint emits the same warning (multiple-statements)
        # for "two statements on a line" separated by a colon and a semi-colon, while pep8 has E701
        # and E702 for those cases respectively. In this case, the pylint error will not be 'blended' as
        # it will appear in two blend_lists. Therefore we mark anything not taken from the blend list
        # as "consumed" and then filter later, to avoid such cases.
        for now_used in blend_list[1:]:
            now_used.used = True

    return [m for m in blended if not getattr(m, 'used', False)]


def blend(messages, blend_combos=None):
    blend_combos = blend_combos or BLEND_COMBOS

    # group messages by file and then line number
    msgs_grouped = defaultdict(lambda: defaultdict(list))

    for message in messages:
        msgs_grouped[message.location.path][message.location.line].append(
            message,
        )

    # now blend together all messages on the same line
    out = []
    for by_line in msgs_grouped.values():
        for messages_on_line in by_line.values():
            out += blend_line(messages_on_line, blend_combos)

    return out


def get_default_blend_combinations():
    combos = yaml.safe_load(
        pkg_resources.resource_string(__name__, 'blender_combinations.yaml')
    )
    combos = combos.get('combinations', [])

    defaults = []
    for combo in combos:
        toblend = []
        for msg in combo:
            toblend += msg.items()
        defaults.append(tuple(toblend))

    return tuple(defaults)


BLEND_COMBOS = get_default_blend_combinations()
