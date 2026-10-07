from pathlib import Path
import argparse, collections, copy, datetime, hashlib, itertools, json, sys

base = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
args = parser.parse_args()
sys.path.insert(0, str(base / args.package))
from rouge.damage import calculate_damage


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


# The earlier retained matrix used an unsupported sp_per_second request and
# correctly compared its prior errors. These new requests use the existing
# supported sp_recovery input; do not rerun or replace that completed matrix.
rows = []
for skill, mode, flag, relics in itertools.product((1, 2, 3), ('frames', 'continuous'), (False, True),
                                                 ([], ['rogue_6_relic_legacy_67'])):
    request = {'operator': 'char_2025_shu', 'skill': skill, 'four_sui': flag,
               'timing_mode': mode, 'window_seconds': 10,
               'effects': [{'kind': 'sp_recovery', 'value': .2}, {'kind': 'attack_speed', 'value': 18}],
               'relic_ids': relics,
               'target_enemy': {'stage_id': 'ro6_e_3_6', 'enemy_id': 'enemy_10107_mjcdog_2', 'level': 0},
               'run_config': {'difficulty': {'value': 4}}}
    original = copy.deepcopy(request)
    result = json.loads(canonical(calculate_damage(request)))
    assert request == original
    assert result['estimate']['skill']['sp_recovery_per_second'] == 1.2
    if flag:
        for field in ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_damage',
                      'cycle_healing', 'cycle_dps', 'cycle_hps'):
            assert result['estimate']['skill'][field] is None
    rows.append({'request': original, 'full_result': result, 'full_result_sha256': digest(result)})
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'package': args.package,
       'public_calls': len(rows), 'supported_independent_natural_sp_and_attack_sp_relic_controls': True,
       'all_callers_preserved': True, 'records': rows}
(base / (args.package.split('/')[-1] + '-supplemental-sp075.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k != 'records'})
