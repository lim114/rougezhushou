"""Relic runes modify cultivated attributes before battle modifiers.

The raw source key, not the public effect's name, establishes this layer.
Costs retain their independently verified integer/card pipeline in deployment.
"""
FIELDS = {'attack_pct': 'attack', 'hp_pct': 'hp', 'defense_pct': 'defense',
          'attack_speed': 'attack_speed', 'resistance_flat': 'resistance',
          'redeploy_delta': 'redeploy_seconds'}


def is_attribute_rune(effect):
    return (effect.get('attribute_layer') == 'relic_rune'
            and effect['kind'] in FIELDS
            and effect.get('formula_item') in ('ADDITION', 'MULTIPLIER', 'FINAL_SCALER'))


def apply_attribute_runes(attributes, effects):
    """Return an independent snapshot; never fold runes into talent multipliers."""
    attributes = dict(attributes)
    for field in FIELDS.values():
        rules = [e for e in effects if is_attribute_rune(e) and FIELDS[e['kind']] == field]
        if not rules:
            continue
        # The native rune accumulator is FP/Q32. AttributesData's HP/ATK/DEF
        # are ObscuredInt: FP -> float32 -> ties-to-even happens before talents.
        # Reuse the previously sealed pure numeric conversion, not card costs.
        from .deployment import _fp, _fp_product, _single, _Q32
        def term(effect):
            if effect.get('native_count_scale') == 'float32_before_fp':
                return _fp(_single(_single(effect['native_rune_base']) * _single(effect['native_rune_factor'])))
            return _fp(effect['value'])
        addition = sum(term(e) for e in rules if e['formula_item'] == 'ADDITION')
        multiplier = _Q32 + sum(term(e) for e in rules if e['formula_item'] == 'MULTIPLIER')
        value = _fp_product(_fp(attributes[field]) + addition, multiplier)
        for effect in rules:
            if effect['formula_item'] == 'FINAL_SCALER':
                factor = _fp(effect['value'])
                if factor < 0:
                    factor += _Q32
                value = _fp_product(value, factor)
        value = max(0, _single(_single(value) / _Q32))
        attributes[field] = round(value) if field in ('hp', 'attack', 'defense', 'redeploy_seconds') else value
        if field == 'resistance':
            attributes[field] = min(100, attributes[field])
    if 'attack_speed' in attributes:
        from .attribute_limits import attack_speed_attribute
        attributes['attack_speed'] = attack_speed_attribute(attributes['attack_speed'])
    return attributes


def prepare_attribute_runes(scenario, attributes):
    """Split resolved current-operator runes from ordinary battle effects once."""
    scenario = dict(scenario)
    runes = [e for e in scenario.get('effects', []) + scenario.get('_relic_rules', [])
             if is_attribute_rune(e) and not e.get('token_only')]
    scenario['effects'] = [e for e in scenario.get('effects', []) if not is_attribute_rune(e)]
    scenario['_attribute_runes'] = runes
    original_attack = scenario['base_attack']
    # Explicit preview attack uses the same proven rune layer as cultivated ATK.
    preview = apply_attribute_runes({**attributes, 'attack': original_attack}, runes)
    scenario['base_attack'] = preview['attack']
    attributes = apply_attribute_runes(attributes, runes)
    scenario['_attribute_attack_speed'] = attributes['attack_speed']
    return scenario, attributes
