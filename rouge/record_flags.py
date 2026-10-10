"""Read-only held/present qualification for retained exploration records.

Missing flags keep their existing historical default. Only an exact bool is a
new presence claim. Text, numbers, null and containers remain raw evidence and
produce an unknown view; no truthiness or guessed string conversion supplies a
current possession, training fact, departure, recruitment or counter reset.
"""


def record_flag(record, key):
    if key not in record:
        return True
    value = record[key]
    return value if type(value) is bool else None


def active_record(record, key):
    return record_flag(record, key) is True


RECIPIENT_KEYS = ('char_buff_ids', 'char_buffs_complete',
                  'char_buff_absent_ids', 'char_buff_pending_ids')
RUN_METADATA_KEYS = ('recruitment_kind', 'advanced', *RECIPIENT_KEYS)


def metadata_mask(record):
    """Qualify our retained metadata mask without normalizing raw extras."""
    raw = record.get('unconfirmed_run_metadata', [])
    if type(raw) is list and all(type(key) is str for key in raw):
        return set(raw).intersection(RUN_METADATA_KEYS)
    return set(RUN_METADATA_KEYS)


def projected_run_metadata(record):
    """Leave healthy aliases intact; mask only explicitly unconfirmed history.

    A fresh partial popup may qualify its own visible positives, while an old
    complete/negative list remains historical until a fresh full popup arrives.
    This projection never writes or repairs the retained member or its proofs.
    """
    mask = metadata_mask(record)
    if not mask:
        return record
    view = dict(record)
    if 'recruitment_kind' in mask:
        view['recruitment_kind'] = None
    if 'advanced' in mask:
        view.pop('advanced', None)
    if mask.intersection(RECIPIENT_KEYS):
        ids = record.get('qualified_char_buff_ids', [])
        if type(ids) is not list or any(type(identity) is not str for identity in ids):
            ids = []
        view.update(char_buff_ids=ids, char_buffs_complete=False,
                    char_buff_absent_ids=[], char_buff_pending_ids=[])
    return view


def unconfirmed_record_ids(records, key):
    return sorted(identity for identity, record in records.items()
                  if record_flag(record, key) is None)


def unconfirmed_item_ids(state):
    return (unconfirmed_record_ids(state.get('relics', {}), 'held') +
            unconfirmed_record_ids(state.get('tactical_tools', {}), 'held'))


def memory_has_unconfirmed_items(state, memory):
    if not memory:
        return False
    unknown = set(unconfirmed_item_ids(state))
    return any(unknown.intersection([icon['id'], *icon['candidates']])
               for icon in memory['icons'])
