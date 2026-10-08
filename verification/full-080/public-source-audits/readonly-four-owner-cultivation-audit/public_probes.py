import copy, gzip, hashlib, json, pathlib, sys

sys.dont_write_bytecode = True
OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(OUT / 'frozen75'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report

strict = lambda obj: json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
records, cache, mutations = [], {}, []
catalog_before = strict(catalog())

def outcome(args):
    key = strict(args)
    if key not in cache:
        given = copy.deepcopy(args)
        before = strict(given)
        try:
            value = calculate_damage(given)
            result = {'accepted': True, 'result': value, 'formatted_report': format_report(value), 'technical_report': format_report(value, technical=True), 'formatted_estimate': format_estimate(value)}
        except Exception as exc:
            result = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
        if strict(given) != before:
            mutations.append(args)
        strict(result)
        cache[key] = result
    return cache[key]

def add(group, args):
    record = {'id': len(records), 'group': group, 'input': args, 'outcome': outcome(args)}
    records.append(record)
    return record

base = {'base_attack': 1000, 'enemy_resistance': 30, 'enemy_defense': 300, 'skill_rank': 7, 'window_seconds': 10}
owners = ('char_206_gnosis', 'char_437_mizuki', 'char_4087_ines', 'char_1035_wisdel')
qualification = {}
for owner in owners:
    profile = catalog()['operators'][owner]
    qualification[owner] = []
    for elite in range(3):
        for potential in (1, 6):
            args = dict(base, operator=owner, elite=elite, potential=potential, skill=1)
            talents, parts = selected_talents(profile, args)
            qualification[owner].append({'elite': elite, 'potential': potential, 'selected_talents': talents, 'module_parts': parts})
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for extra in ({}, {'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}, {'timing': {'target_windows': []}}):
                    add('all_skill_culture_and_window_gates', dict(base, operator=owner, elite=elite, skill=skill, timing_mode=mode, **extra))
    for module in profile['modules']:
        for elite, level in ((0, 1), (1, 1), (2, 59), (2, 60), (2, 90)):
            for stage in range(1, len(module['levels']) + 1):
                add('module_qualification_boundaries', dict(base, operator=owner, elite=elite, level=level, skill=1, module_id=module['id'], module_level=stage))

pairs = []
for mode in ('frames', 'continuous'):
    for op, field, values, elites in (
        ('char_4087_ines', 'stolen_enemy_count', (0, 1, 2), (0, 1, 2)),
        ('char_437_mizuki', 'enemy_below_half', (False, True), (0, 1, 2)),
        ('char_206_gnosis', 'cold_state', (0, 1, 2), (0, 1, 2)),
        ('char_1035_wisdel', 'ghost_count', (0, 1), (0, 1, 2)),
    ):
        for elite in elites:
            group = []
            for value in values:
                args = dict(base, operator=op, elite=elite, skill=1, timing_mode=mode)
                args[field] = value
                if op == 'char_1035_wisdel': args['ghost_casts'] = 1
                group.append(add('talent_gate_declared_control', args))
            pairs.append({'operator': op, 'elite': elite, 'mode': mode, 'field': field, 'ids': [r['id'] for r in group], 'complete_outcomes_equal': all(strict(r['outcome']) == strict(group[0]['outcome']) for r in group)})

# Keep the current Gnosis contract ambiguity visible without changing any clock.
for stage in (1, 2, 3):
    for state in (0, 1, 2):
        add('gnosis_full_state_label_vs_initial_note', dict(base, operator='char_206_gnosis', elite=2, level=60, skill=2, module_id='uniequip_004_gnosis', module_level=stage, cold_state=state))

# Read only existing relevance gates for each owner; the effects are not reclassified.
from rouge.relics import mechanics, matches
from rouge.offline_scope import partition
relic_conditions = {}
for owner in owners:
    profile = catalog()['operators'][owner]
    candidates = []
    for rid, data in mechanics()['relics'].items():
        active, reference, pending, reference_pending = partition(data, rid)
        selected = [e for e in active if e.get('condition') and matches(e, profile)]
        if selected:
            candidates.append({'relic_id': rid, 'name': data['name'], 'active_owner_conditional_rules': selected, 'source': data['source']})
    relic_conditions[owner] = candidates

assert not mutations
assert strict(catalog()) == catalog_before
raw = (strict(records) + '\n').encode()
compressed = gzip.compress(raw, mtime=0)
(OUT / 'public-whole-outcomes.json.gz').write_bytes(compressed)
(OUT / 'selected-talents-and-conditional-relic-selectors.json').write_text(json.dumps({'selected_talents': qualification, 'owner_matched_existing_conditional_rules': relic_conditions}, ensure_ascii=False, indent=2) + '\n')
(OUT / 'public-pair-comparison.json').write_text(json.dumps(pairs, ensure_ascii=False, indent=2) + '\n')
receipt = {'baseline_head': '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc', 'kind': 'readonly targeted public API audit; no draft or candidate claimed', 'records': len(records), 'actual_unique_public_calculate_calls': len(cache), 'accepted_calls': sum(v['accepted'] for v in cache.values()), 'error_calls': sum(not v['accepted'] for v in cache.values()), 'input_mutations': len(mutations), 'catalog_mutated': False, 'all_public_results_and_three_formatted_texts_or_exact_errors_recorded': True, 'raw_bytes': len(raw), 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'gzip_bytes': len(compressed), 'gzip_sha256': hashlib.sha256(compressed).hexdigest(), 'not_native_validation': True}
(OUT / 'public-probe-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt))
print(json.dumps(pairs, ensure_ascii=False))
