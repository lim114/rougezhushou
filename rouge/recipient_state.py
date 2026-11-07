"""Retain positive buffs and invalidate only outdated negative evidence."""
import json
from functools import lru_cache
from pathlib import Path

from .catalog import operator_profiles
from .relics import mechanics
from .record_flags import active_record,metadata_mask,RECIPIENT_KEYS


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
    has_popup = 'char_buff_ids' in observed
    if not has_popup and metadata_mask(merged).intersection(RECIPIENT_KEYS):
        return  # Retain raw popup evidence; identity-only reads cannot renew it.
    positives = set(merged.get('char_buff_ids', []))
    if has_popup and observed.get('char_buffs_complete') is True:
        absent = compatible_buffs(merged['id'])
        pending = set()
        merged['char_buff_absence_observed_at'] = captured_at
    else:
        # A partial popup supersedes old absences; ordinary pages retain them.
        absent = absent_buffs(previous) if previous and not has_popup and not new_recruitment else set()
        pending = set() if new_recruitment else set(previous.get('char_buff_pending_ids', []))
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
    if not gained_relic_ids and not promoted_ids:
        return
    triggers = []
    for rid, rule in lifecycle_rules().items():
        trigger = rule['trigger']
        gained = rid in gained_relic_ids and trigger in ('gain_random', 'upgrade_ticket')
        on_promotion = (bool(promoted_ids) and trigger in ('next_recruit_or_upgrade', 'upgrade_ticket')
                        and rid in state['relics'] and active_record(state['relics'][rid], 'held'))
        if gained or on_promotion:
            triggers.append((rid, rule, gained, on_promotion))
    if not triggers:
        return
    observed = {m['id']: m for m in observations}
    for oid, member in state['operators'].items():
        current = observed.get(oid, {})
        if (member.get('scope') != 'run' or not active_record(member, 'present')
                or metadata_mask(member).intersection(RECIPIENT_KEYS)):
            continue
        if 'char_buff_ids' in current and current.get('char_buffs_complete') is True:
            continue
        eligible = []
        for rid, rule, gained, on_promotion in triggers:
            promoted = on_promotion and oid in promoted_ids
            if not gained and not promoted:
                continue
            # Historical icon resolution must not supersede a later popup.
            if gained and not promoted and state['relics'][rid]['captured_at'] <= member.get('char_buff_absence_observed_at', 0):
                continue
            eligible.append((rid, rule, promoted))
        if not eligible:
            continue
        absent = absent_buffs(member)
        reasons = []
        candidates = set()
        for rid, rule, promoted in eligible:
            affected = set(rule['char_buff_ids']) & absent
            if affected:
                candidates.update(affected)
                reasons.append({'relic_id': rid, 'trigger': rule['trigger'],
                                'observation': 'promotion' if promoted else 'newly_confirmed_item'})
        if not candidates:
            continue
        member['char_buff_absent_ids'] = sorted(absent - candidates)
        member['char_buffs_complete'] = False
        member['char_buff_pending_ids'] = sorted(set(member.get('char_buff_pending_ids', [])) | candidates)
        state['history'].append({'at': captured_at, 'kind': 'char_buff_absence_invalidated', 'id': oid,
                                 'char_buff_ids': sorted(candidates), 'reasons': reasons})
