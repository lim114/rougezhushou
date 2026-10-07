"""Independent public checks for periodic Shu SP; no game or native execution."""
from pathlib import Path
import sys, json, hashlib, itertools, datetime

sys.path.insert(0, sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.estimate import format_estimate

draft = Path(sys.argv[1]).name == 'draft060'
root = Path(__file__).parent
records = []; calls = 0; failures = []

def call(request):
    global calls
    calls += 1
    return calculate_damage(request)

def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

resource_keys = ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_healing', 'cycle_dps', 'cycle_hps')
direct_keys = ('duration_seconds', 'total_damage', 'total_healing', 'phase_damage', 'phase_healing',
               'window_seconds', 'window_healing', 'window_dps', 'window_hps')
timings = ({}, {'sp_lockout_extra_seconds': 2.25, 'post_skill_lock_frames': 91},
           {'target_windows': [], 'sp_lockout_extra_seconds': 20},
           {'target_disappears_seconds': 0, 'sp_lockout_extra_seconds': 20},
           {'target_disappears_seconds': '0.0'},
           {'moving_windows': [[0, 10]], 'interrupt_windows': [[0, 10]]})

for skill, rank, mode, timing, relics in itertools.product(
        (1, 2, 3), range(1, 11), ('frames', 'continuous'), timings,
        ([], ['rogue_6_relic_legacy_99'])):
    request = {'operator': 'char_2025_shu', 'skill': skill, 'skill_rank': rank,
               'timing_mode': mode, 'four_sui': True, 'window_seconds': 10,
               'timing': timing, 'relic_ids': relics}
    result = call(request)
    without = call({**request, 'four_sui': False})
    s = result['estimate']['skill']; ws = without['estimate']['skill']
    if draft:
        try:
            for key in resource_keys:
                assert s[key] is None, key
            assert s['initial_seconds'] == (0 if ws['initial_seconds'] == 0 else None)
            if 'initial_seconds' in result['timing']:
                assert result['timing']['initial_seconds'] == s['initial_seconds']
            if 'cycle_seconds' in result['timing']:
                assert result['timing']['cycle_seconds'] is None
            assert result['timing']['recharge_streams'] == []
            assert result['timing']['phase_clock_unbound']
            assert not result['timing']['resource_and_damage_shared_clock']
            assert s['sp_recovery_per_second'] == ws['sp_recovery_per_second']
            ref = result['shu_periodic_sp_reference']
            assert ref['independent_sp_clock_reference']['initial_seconds'] == ws['initial_seconds']
            assert ref['independent_sp_clock_reference']['recharge_seconds'] == ws['recharge_seconds']
            for key in ('first_tick_seconds', 'actual_tick_times_seconds', 'clock_origin', 'reset_rule', 'blocked_credit_rule'):
                assert ref[key] is None, key
            for family in ('known_healing_subtotals', 'known_damage_subtotals'):
                if family in result:
                    for key in ('cycle_healing', 'cycle_damage', 'cycle_dps'):
                        if key in result[family]: assert result[family][key] is None, (family, key)
            assert result['scope'] == result['estimate']['scenario_scope']
            assert not result['complete'] and not result['estimate']['complete']
            report_clock = next(section for section in result['report']['sections'] if section['id'] == 'timing')
            metrics = {m['key']: m['value'] for m in report_clock['metrics']}
            assert metrics['initial'] == s['initial_seconds']
            assert metrics['cycle'] is None and metrics['recharge'] is None
        except (AssertionError, KeyError) as error:
            failures.append({'request': request, 'problem': repr(error)})
    records.append({'request': request, 'kind': 'qualified', 'direct': {
        'base_stats': result['estimate']['base_stats'], 'attack': result['attack'],
        'total_damage': result['total_damage'], 'total_healing': result['total_healing'],
        'components_hash': sha(result['components']),
        'skill': {k: s[k] for k in direct_keys}},
        'resource': {k: s[k] for k in ('initial_seconds', 'sp_recovery_per_second', *resource_keys)}})

for elite, levels, skills, rank in ((0, (1, 50), (1,), 1), (1, (1, 80), (1, 2), 7)):
    for level, skill, mode, potential, flag in itertools.product(levels, skills, ('frames', 'continuous'), (1, 6), (True, False, 'truthy')):
        request = {'operator': 'char_2025_shu', 'elite': elite, 'level': level, 'skill': skill,
                   'skill_rank': rank, 'potential': potential, 'four_sui': flag, 'timing_mode': mode}
        result = call(request)
        without = call({k:v for k,v in request.items() if k != 'four_sui'})
        assert result == without
        records.append({'request': request, 'kind': 'ineligible', 'full_hash': sha(result)})

for operator, profile in catalog()['operators'].items():
    if operator == 'char_2025_shu': continue
    for skill, mode in itertools.product(range(1, len(profile['skills'])+1), ('frames', 'continuous')):
        request = {'operator': operator, 'skill': skill, 'timing_mode': mode, 'four_sui': True,
                   'window_seconds': 0, 'timing': {'target_disappears_seconds': 0}}
        result = call(request)
        without = call({k:v for k,v in request.items() if k != 'four_sui'})
        assert result == without
        records.append({'request': request, 'kind': 'other_operator', 'full_hash': sha(result)})

example = call({'operator': 'char_2025_shu', 'skill': 2, 'four_sui': True})
Path(sys.argv[2]).write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'package':sys.argv[1], 'calls': calls, 'scenarios':len(records), 'failures':failures,
    'draft_source_hashes':{str(p.relative_to(Path(sys.argv[1]))):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in (Path(sys.argv[1])/'rouge/operator_engine.py',Path(sys.argv[1])/'rouge/reporting.py')},
    'formatted_example':format_estimate(example), 'records':records}, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'calls':calls,'scenarios':len(records),'failures':len(failures),'output':sys.argv[2]}))
assert not failures, failures[:3]
