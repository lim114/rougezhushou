"""Retain positive buffs and invalidate only outdated negative evidence."""
import json
from functools import lru_cache
from pathlib import Path

from .catalog import operator_profiles
from .relics import mechanics


@lru_cache(maxsize=1)
def lifecycle_rules():
    return json.loads((Path(__file__).with_name('data')/'recipient-lifecycle.json').read_text(encoding='utf-8'))['rules']


def compatible_buffs(operator_id):
    profession = operator_profiles()[operator_id]['profession']
    return {bid for bid, buff in mechanics()['char_buffs'].items()
            if not buff['required_profession'] or profession in buff['required_profession'].split('|')}


def absent_buffs(member):
    compatible = compatible_buffs(member['id'])
    positives = set(member.get('char_buff_ids', []))
    if member.get('char_buffs_complete') is True:
        return compatible - positives
    return set(member.get('char_buff_absent_ids', [])) & compatible - positives


def merge_recipient_evidence(previous, observed, merged, new_recruitment, captured_at):
    """A full popup replaces negatives; partial popups cannot renew absences."""
    absent = set() if new_recruitment or not previous else absent_buffs(previous)
    pending = set() if new_recruitment else set(previous.get('char_buff_pending_ids', []))
    positives = set(merged.get('char_buff_ids', []))
    if 'char_buff_ids' in observed and observed.get('char_buffs_complete') is True:
        absent = compatible_buffs(merged['id']) - positives
        pending.clear()
        merged['char_buff_absence_observed_at'] = captured_at
    elif 'char_buff_ids' in observed:
        # An explicitly incomplete current popup supersedes an older full
        # list. Ordinary pages without a popup still reuse scoped negatives.
        absent.clear()
    merged['char_buff_absent_ids'] = sorted(absent - positives)
    merged['char_buff_pending_ids'] = sorted(pending - positives)
    if new_recruitment and not observed.get('char_buffs_complete'):
        merged.pop('char_buff_absence_observed_at', None)


def invalidate_recipient_absence(state, observations, gained_relic_ids, promoted_ids, captured_at):
    """A possible new grant invalidates absence, but never proves receipt.

    First visibility of a new relic need not be its exact acquisition time.
    The old negative therefore becomes uncertain; no recipient is inferred.
    A complete popup in this same observation is newer direct evidence.
    """
    observed = {m['id']: m for m in observations}
    held = {rid for rid, record in state['relics'].items() if record.get('held', True)}
    rules = lifecycle_rules()
    for oid, member in state['operators'].items():
        current = observed.get(oid, {})
        if member.get('scope') != 'run' or not member.get('present', True):
            continue
        if 'char_buff_ids' in current and current.get('char_buffs_complete') is True:
            continue
        reasons = []
        candidates = set()
        for rid, rule in rules.items():
            gained = rid in gained_relic_ids and rule['trigger'] in ('gain_random', 'upgrade_ticket')
            promoted = oid in promoted_ids and rid in held and rule['trigger'] in ('next_recruit_or_upgrade', 'upgrade_ticket')
            if not gained and not promoted:
                continue
            # Historical icon resolution must not supersede a later popup.
            if gained and not promoted and state['relics'][rid]['captured_at'] <= member.get('char_buff_absence_observed_at', 0):
                continue
            affected = set(rule['char_buff_ids']) & absent_buffs(member)
            if affected:
                candidates.update(affected)
                reasons.append({'relic_id': rid, 'trigger': rule['trigger'],
                                'observation': 'promotion' if promoted else 'newly_confirmed_item'})
        if not candidates:
            continue
        member['char_buff_absent_ids'] = sorted(absent_buffs(member) - candidates)
        member['char_buffs_complete'] = False
        member['char_buff_pending_ids'] = sorted(set(member.get('char_buff_pending_ids', [])) | candidates)
        state['history'].append({'at': captured_at, 'kind': 'char_buff_absence_invalidated', 'id': oid,
                                 'char_buff_ids': sorted(candidates), 'reasons': reasons})
