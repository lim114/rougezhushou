"""Default native attribute range, distinct from the attack timer's range.

AttributeMeta(ATTACK_SPEED, 20f), pinned native evidence in batch 0.65.
Explicit runtime range overrides are not inferred by this offline calculator.
"""


def attack_speed_attribute(value):
    return max(20, value)


def effective_attack_speed(value):
    return min(600, attack_speed_attribute(value))


def finalize_attack_speed_references(result):
    # Keep ordinary sums unclamped until skill/finite bonuses are combined.
    # Only public snapshots are normalized here, after all calculation phases.
    for record, keys in (
        (result, ('base_attack_speed_reference', 'attack_speed_reference')),
        (result['estimate']['base_stats'], ('attack_speed_reference',)),
        (result['estimate']['skill'], ('skill_attack_speed_reference',)),
        (result.get('deployment_buff_reference', {}), ('permanent_attack_speed',)),
    ):
        for key in keys:
            if key in record:
                record[key] = attack_speed_attribute(record[key])
