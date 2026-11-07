"""Physical kettle copies from a complete positive bar, separate from relic IDs.

PRTS blackflow catalogue and kettle page: repeated fallback kettles are possible.
Other repeated identities or partial/ambiguous bars are not quantity evidence.
"""
from collections import Counter
from .record_flags import record_flag

KETTLE='rogue_6_relic_legacy_1'

def confirmed_bar_counts(icons,expected):
    if type(expected)is not int or expected<=0 or len(icons)!=expected or not all(i.get('confirmed')is True for i in icons):return None
    counts=Counter(i['id']for i in icons)
    return counts if all(n==1 or rid==KETTLE for rid,n in counts.items())else None

def kettle_copies(state, *, held_by_kind=None):
    relics = state.get('relics', {})
    tools = state.get('tactical_tools', {})
    records = relics | tools
    if KETTLE not in records or not all(isinstance(record, dict) for record in records.values()):
        return None

    if held_by_kind is None:
        flags = {rid: record_flag(record, 'held') for rid, record in records.items()}
        # Tools override matching relic IDs for counting. The legacy completeness
        # check also considers the hidden relic's original flag.
        other_flags = (record_flag(relics[rid], 'held') for rid in relics.keys() & tools.keys())
    else:
        relic_flags, tool_flags = held_by_kind
        flags = relic_flags | tool_flags
        other_flags = relic_flags.values()
    held = {rid for rid, flag in flags.items() if flag is True}
    if KETTLE not in held:
        return None

    expected = state.get('relic_count')
    if (state.get('inventory_verified') is True and type(expected) is int
            and None not in flags.values() and None not in other_flags and expected == len(held)):
        return 1
    memory = state.get('relic_icon_memory')
    if (not memory or memory.get('complete_bar') is not True
            or type(memory.get('count')) is not int or memory['count'] != expected):
        return None
    counts = confirmed_bar_counts(memory['icons'], expected)
    if counts is None or not counts.keys() <= held:
        return None
    return counts.get(KETTLE)
