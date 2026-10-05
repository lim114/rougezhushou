"""Product scope: stable offline estimates; combat-dependent relics are reference.

Pinned effects stay intact. This policy decides whether the public calculator
uses them; exclusion is not a statement that the in-game effect is absent.
"""

REFERENCE_KINDS = {'received_sp', 'event_sp', 'deployment_hp_loss', 'first_damage_scale',
    'barrier_on_deploy_ratio', 'evasion_chance', 'shield_layers', 'status_duration_delta',
    'incoming_element_resistance'}
COMBAT_CONDITIONS = {'current_hp_ratio', 'adjacent_allies', 'deployed_casters',
    'skill_cast_stacks', 'deployed_seconds', 'near_protection_point', 'blocked_enemies',
    'active_other_aura_sources', 'deployment_hp_ratio', 'deployment_loss_unused', 'enemy_first_damage_unused'}
# Full-item scripts whose required triggers/state depend on actual combat.
# Fixed cast/ammunition effects and confirmed persistent counters stay eligible.
REFERENCE_RELIC_IDS = {
    'rogue_6_relic_legacy_' + str(n) for n in
    (36, 37, 51, 65, 79, 114, 115, 116, 117, 119, 120, 121, 122, 123, 124, 126, 127, 135, 137)
} | {'rogue_6_relic_fight_' + str(n) for n in
    (3, 4, 5, 6, 8, 9, 10, 12, 13, 16, 17, 18, 19, 20, 23, 24)
} | {'rogue_6_relic_hand_' + str(n) for n in (2, 3, 5, 6, 7)
} | {'rogue_6_relic_book_' + str(n) for n in (2, 4, 5, 6)
} | {'rogue_6_relic_assign_' + str(n) for n in (1, 2, 3, 4, 6, 8, 11, 14)
} | {'rogue_6_relic_artifact_2', 'rogue_6_relic_artifact_3'}
REFERENCE_PENDING = {
    'global_buff_normal:rogue_6_char_kill_add_sp',
    'char_ability_new:rogue_6_random_damage_on_born',
    '部署损血为一次事件独立参考；真实触发帧、当前生命和复合生命机制未自动确认',
}


def reference_effect(effect, relic_id):
    return (relic_id in REFERENCE_RELIC_IDS or effect['kind'] in REFERENCE_KINDS or
        effect.get('condition') in COMBAT_CONDITIONS)


def partition(entry, identity):
    relic_id = entry.get('relic_id', identity)
    active, reference = [], []
    for effect in entry['effects']:
        (reference if reference_effect(effect, relic_id) else active).append(effect)
    pending, reference_pending = [], []
    for message in entry['pending']:
        (reference_pending if relic_id in REFERENCE_RELIC_IDS or message in REFERENCE_PENDING else pending).append(message)
    return active, reference, pending, reference_pending


def active_effects(entry, identity):
    return partition(entry, identity)[0]


def scope_counts(data):
    counts = {'reference_only': 0, 'mixed': 0, 'offline': 0}
    remaining = {'pending': 0, 'partial': 0}
    for rid, entry in data['relics'].items():
        active, reference, pending, reference_pending = partition(entry, rid)
        excluded = bool(reference or reference_pending or rid in REFERENCE_RELIC_IDS)
        scope = 'mixed' if excluded and (active or pending) else 'reference_only' if excluded else 'offline'
        counts[scope] += 1
        if pending:
            remaining['partial' if active else 'pending'] += 1
    return {'items': counts, 'offline_mechanism_gaps': remaining}
