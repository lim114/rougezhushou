"""Physical kettle copies from a complete positive bar, separate from relic IDs.

PRTS blackflow catalogue and kettle page: repeated fallback kettles are possible.
Other repeated identities or partial/ambiguous bars are not quantity evidence.
"""
from collections import Counter
from .record_flags import active_record,unconfirmed_item_ids

KETTLE='rogue_6_relic_legacy_1'

def confirmed_bar_counts(icons,expected):
    if type(expected)is not int or expected<=0 or len(icons)!=expected or not all(i.get('confirmed')is True for i in icons):return None
    counts=Counter(i['id']for i in icons)
    return counts if all(n==1 or rid==KETTLE for rid,n in counts.items())else None

def kettle_copies(state):
    records={**state.get('relics',{}),**state.get('tactical_tools',{})}
    if KETTLE not in records or not all(isinstance(record,dict)for record in records.values())or not active_record(records[KETTLE],'held'):return None
    # A healthy older complete record with exactly one slot per known ID
    # also proves one kettle; a larger badge never supplies a guessed count.
    if state.get('inventory_verified')is True and type(state.get('relic_count'))is int and not unconfirmed_item_ids(state)and state['relic_count']==sum(active_record(r,'held')for r in records.values()):return 1
    memory=state.get('relic_icon_memory')
    if not memory or memory.get('complete_bar')is not True or type(memory.get('count'))is not int or memory['count']!=state.get('relic_count'):return None
    counts=confirmed_bar_counts(memory['icons'],state.get('relic_count'))
    if counts is None or KETTLE not in counts:return None
    if not counts.keys()<=records.keys()or not all(active_record(records[rid],'held')for rid in counts):return None
    return counts[KETTLE]
