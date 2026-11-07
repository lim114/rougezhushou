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


def rune_operand(effect):
    if effect.get('native_count_scale') == 'float32_before_fp':
        from .deployment import _single
        return _single(effect['native_rune_base']) * _single(effect['native_rune_factor'])
    return effect['value']


def _apply_selected_runes(attributes, runes, preview_attack=None):
    """Apply classified runes once, including an optional explicit ATK preview."""
    attributes = dict(attributes)
    grouped = {field: [] for field in FIELDS.values()}
    for effect in runes:
        grouped[FIELDS[effect['kind']]].append(effect)
    # The native rune accumulator is FP/Q32. AttributesData's HP/ATK/DEF
    # are ObscuredInt: FP -> float32 -> ties-to-even happens before talents.
    # Reuse the previously sealed pure numeric conversion, not card costs.
    from .deployment import _fp, _fp_product, _single, _Q32
    for field, rules in grouped.items():
        if not rules:
            continue
        addition = sum(_fp(rune_operand(e)) for e in rules if e['formula_item'] == 'ADDITION')
        multiplier = _Q32 + sum(_fp(rune_operand(e)) for e in rules if e['formula_item'] == 'MULTIPLIER')
        scalers = []
        for effect in rules:
            if effect['formula_item'] == 'FINAL_SCALER':
                factor = _fp(effect['value'])
                if factor < 0:
                    factor += _Q32
                scalers.append(factor)
        bases = [attributes[field]]
        preview_field = field == 'attack' and preview_attack is not None
        if preview_field and preview_attack != bases[0]:
            bases.append(preview_attack)
        values = []
        for basis in bases:
            value = _fp_product(_fp(basis) + addition, multiplier)
            for factor in scalers:
                value = _fp_product(value, factor)
            value = max(0, _single(_single(value) / _Q32))
            value = round(value) if field in ('hp', 'attack', 'defense', 'redeploy_seconds') else value
            values.append(min(100, value) if field == 'resistance' else value)
        attributes[field] = values[0]
        if preview_field:
            preview_attack = values[-1]
    if 'attack_speed' in attributes:
        from .attribute_limits import attack_speed_attribute
        attributes['attack_speed'] = attack_speed_attribute(attributes['attack_speed'])
    return attributes, preview_attack


def prepare_attribute_runes(scenario, attributes):
    """Split resolved current-operator runes from ordinary battle effects once."""
    scenario = dict(scenario)
    runes, ordinary = [], []
    for effect in scenario.get('effects', []):
        if is_attribute_rune(effect):
            if not effect.get('token_only'):runes.append(effect)
        else:ordinary.append(effect)
    for effect in scenario.get('_relic_rules', []):
        if is_attribute_rune(effect) and not effect.get('token_only'):runes.append(effect)
    scenario['effects'] = ordinary
    scenario['_attribute_runes'] = runes
    cultivated = dict(attributes)
    # Explicit preview attack uses the same proven rune layer as cultivated ATK.
    attributes, scenario['base_attack'] = _apply_selected_runes(attributes, runes, scenario['base_attack'])
    scenario['_attribute_attack_speed'] = attributes['attack_speed']
    from .panel_native_bridge import prepare as prepare_native_panels
    prepare_native_panels(scenario, cultivated, attributes, runes)
    return scenario, attributes
