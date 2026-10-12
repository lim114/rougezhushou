"""Counterfactual model differences, never observed effects or causal proof."""
from copy import deepcopy


def relic_panel_diagnostics(scenario, relic_ids=None):
    from .calibration import _scenario, panel_layers, LABELS, BOUNDARY
    from .relics import mechanics
    s = _scenario(scenario)
    selected = s.get('relic_ids', [])
    if (not isinstance(selected, list) or any(not isinstance(v, str) or not v for v in selected)
            or len(selected) != len(set(selected))):
        raise ValueError('当前藏品声明需为不重复的非空ID列表。')
    audited = list(selected) if relic_ids is None else deepcopy(relic_ids)
    if (not isinstance(audited, list) or not 1 <= len(audited) <= 12 or
            any(not isinstance(v, str) or v not in selected for v in audited) or
            len(audited) != len(set(audited))):
        raise ValueError('需选1–12件已在scenario声明且不重复的藏品；其余来源保留为共同背景。')
    background = [v for v in selected if v not in audited]

    def model(ids):
        variant = deepcopy(s)
        variant['relic_ids'] = list(ids)
        # In particular do not delete char_buff_ids. Acquired targeted buffs
        # are a separate declared source, not simulated discard consequences.
        return panel_layers(variant)

    full = model(selected)
    baseline = model(background)
    source_rows = []
    for rid in audited:
        without = model([v for v in selected if v != rid])
        alone = model([v for v in selected if v in background or v == rid])
        source = mechanics()['relics'].get(rid)
        fields = []
        for panel, stats in full['panels'].items():
            for field, value in stats.items():
                if field not in LABELS:
                    continue
                removed = without['panels'][panel].get(field)
                single = alone['panels'][panel].get(field)
                base = baseline['panels'][panel].get(field)
                fields.append({'panel': panel, 'field': field, 'label': LABELS[field],
                    'combined_model_reference': value, 'without_source_model_reference': removed,
                    'single_source_background_model_reference': single,
                    'background_model_reference': base,
                    'marginal_model_difference': None if value is None or removed is None else value-removed,
                    'single_background_model_difference': None if single is None or base is None else single-base,
                    'actual_source_effect': None})
        source_rows.append({'relic_id': rid, 'name': source['name'] if source else rid + '（固定机制未收录）',
            'fixed_mechanic_record_available': source is not None, 'fields': fields,
            'without_source_context': without['context_token'], 'single_source_context': alone['context_token'],
            'without_source_warnings': deepcopy(without['warnings']),
            'single_source_warnings': deepcopy(alone['warnings']),
            'actual_causal_attribution': None})
    combinations = []
    for panel, stats in full['panels'].items():
        for field, value in stats.items():
            if field not in LABELS:
                continue
            base = baseline['panels'][panel].get(field)
            singles = [next(row['single_background_model_difference'] for row in source['fields']
                            if row['panel'] == panel and row['field'] == field) for source in source_rows]
            difference = None if value is None or base is None else value-base
            residual = None if difference is None or any(v is None for v in singles) else difference-sum(singles)
            combinations.append({'panel': panel, 'field': field, 'label': LABELS[field],
                'combined_model_reference': value, 'background_model_reference': base,
                'combined_model_difference': difference,
                'sum_single_background_model_differences': None if any(v is None for v in singles) else sum(singles),
                'nonadditive_model_residual': residual, 'actual_combination_effect': None})
    return {'scope': 'counterfactual_existing_panel_model_diagnostics', 'operator': full['operator'],
            'audited_relic_ids': audited, 'background_relic_ids': background,
            'full_context_token': full['context_token'], 'background_context_token': baseline['context_token'],
            'source_rows': source_rows, 'combination_rows': combinations,
            'full_warnings': deepcopy(full['warnings']), 'background_warnings': deepcopy(baseline['warnings']),
            'preserved_targeted_buff_ids': deepcopy(s.get('char_buff_ids', [])),
            'source': deepcopy(full['source']), 'native_verified': False,
            'actual_panel_difference': None, 'actual_cause_of_observed_error': None,
            'notes': [BOUNDARY,
                '移除单件的边际差值与共同背景上单件增量口径不同；不能将边际差值相加作为总加成。',
                '非相加残差只是当前模型在此组条件下的算术差，不证明未知机制、获取顺序或实际叠加规则。',
                '未选择审计的藏品、培养、分队和其他条件作为共同背景；已领取定向强化不会随移除藏品声明一并删除。',
                '零差值可能来自职业不符、未建模或条件缺失，不证明这件藏品在实际游戏没有效果。',
                '所有警告及条件上下文分别保留；未填观察值，不作实机认证、逆推或自动修正本局。']}
