"""Three source-bound healing relics: direct healing and regeneration differ."""
from math import prod

FLOWER_FACTORS={'rogue_6_relic_legacy_81':1.2,'rogue_6_relic_legacy_82':1.3,
                'rogue_6_relic_legacy_83':1.4}
COMPOSITION_EVIDENCE='research/p2-flower-healing-composition-current/receipt.json'


def verified_flower_factor(rule,kind):
    expected=FLOWER_FACTORS.get(rule.get('relic_id'))
    index=rule.get('source_buff_index')
    return bool(expected is not None and rule.get('_verified_rule') and
        rule.get('source_buff_key')=='global_buff_normal' and rule.get('value')==expected
        and rule.get('kind')==kind and
        (index==0 if kind=='healing_factor' else index in (1,2)) and
        rule.get('composition_evidence')==COMPOSITION_EVIDENCE)


def healing_factor(rules):
    if not rules:return 1
    if len(rules)==1:return rules[0]['value']
    if not all(verified_flower_factor(r,'healing_factor') for r in rules):return None
    # Each global_buff_normal creates its own non-overriding heal modifier.
    return prod({r['relic_id']:r['value'] for r in rules}.values())


def regeneration_factor(rules):
    selected={r['relic_id']:r['value'] for r in rules}
    if len(selected)<=1:return next(iter(selected.values()),1)
    if not all(verified_flower_factor(r,'regeneration_factor') for r in rules):return None
    # Each relic has separate flat- and HP-ratio modifiers. Deduplicate the two
    # channels by source; both use MULTIPLIER, whose percentages add.
    return 1+sum(value-1 for value in selected.values())
