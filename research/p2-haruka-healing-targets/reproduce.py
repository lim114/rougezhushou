"""Reproduce public before/after target references, never native battle events."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import io

BASELINE_HEAD = '04a9a3fbe3680dd221fc5254fadc9aeb050eb1cf'


def scenarios():
    rows = []
    for elite, level in ((0, 50), (1, 80), (2, 59), (2, 60), (2, 90)):
        for potential in (1, 6):
            for stage in (0, 1, 2, 3):
                for skill in range(1, min(3, elite + 1) + 1):
                    for mode in ('frames', 'continuous'):
                        for recipients in (0, 1, 2, 3):
                            s = {'operator': 'char_4202_haruka', 'skill': skill,
                                'elite': elite, 'level': level, 'potential': potential,
                                'skill_rank': 7 if elite < 2 else 10, 'base_attack': 1000,
                                'healing_targets': recipients, 'window_seconds': 10,
                                'timing_mode': mode, 'bubble_bursts': 0, 'levitate_triggers': 0}
                            if stage: s.update(module_id='uniequip_002_haruka', module_level=stage)
                            rows.append(s)
    assert len(rows) == 768
    for rank in range(1, 11):
        for stage in (0, 1, 2, 3):
            for mode in ('frames', 'continuous'):
                for recipients in (0, 1, 2, 3):
                    s = {'operator': 'char_4202_haruka', 'skill': 2,
                        'elite': 2, 'level': 60, 'potential': 1,
                        'skill_rank': rank, 'base_attack': 1000,
                        'healing_targets': recipients, 'window_seconds': 10,
                        'timing_mode': mode, 'bubble_bursts': 0, 'levitate_triggers': 0}
                    if stage: s.update(module_id='uniequip_002_haruka', module_level=stage)
                    rows.append(s)
    assert len(rows) == 1088
    return rows


CAPTURE = r'''
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog
scenarios=json.loads(Path(sys.argv[2]).read_text());rows=[]
profile_hash=hashlib.sha256(json.dumps(catalog(),sort_keys=True).encode()).hexdigest()
for s in scenarios:
 original=copy.deepcopy(s);r=calculate_damage(s);assert s==original
 body_full=next(c for c in r['components'] if c['name']=='护佑者普通治疗')
 body={k:body_full[k] for k in ('name','hits','per_hit','total')}
 skill=r['estimate']['skill']
 extras=[c for c in r['components'] if '组合待核验' in c['name']]
 row={'scenario':s,'ordinary_healing_component':body,'extra_conditional_components':extras,
      'total_healing':r['total_healing'],'total_damage':r['total_damage'],
      'known_healing_subtotals':r.get('known_healing_subtotals'),
      'known_damage_subtotals':r.get('known_damage_subtotals'),
      'skill':{k:skill.get(k) for k in ('initial_seconds','duration_seconds','cycle_seconds','recharge_seconds','total_damage','total_healing','phase_damage','phase_healing','window_damage','window_healing','cycle_damage','cycle_healing','cycle_dps','cycle_hps','window_dps','window_hps')},
      'bubble_components':[c for c in r['components'] if c['name'] in ('扶摇花火','浮泡治疗衍生伤害','浮泡浮空持续伤害')],
      'talent_parameters_sha256':hashlib.sha256(json.dumps(next(section for section in r['report']['sections'] if section['id']=='talents'),sort_keys=True).encode()).hexdigest(),
      'parameter_reference':{k:v for k,v in r.get('haruka_healing_reference',{}).items() if k not in ('window_reference','source_selectors','body_healing_reference_before_recipient_factor')},
      'timing_clock_sha256':hashlib.sha256(json.dumps({k:v for k,v in r['timing'].items() if k!='unplaced_components'},sort_keys=True).encode()).hexdigest(),
      'unplaced_components':r['timing'].get('unplaced_components', [])}
 rows.append(row)
assert profile_hash==hashlib.sha256(json.dumps(catalog(),sort_keys=True).encode()).hexdigest()
Path(sys.argv[3]).write_text(json.dumps({'rows':rows,'cached_catalog_unchanged':True,'catalog_sha256':profile_hash},ensure_ascii=False,indent=2)+'\n')
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='/workspace/rougezhushou')
    parser.add_argument('--candidate', default=str(Path(__file__).resolve().parents[2]))
    args = parser.parse_args()
    output = Path(__file__).parent
    rows = scenarios()
    with tempfile.TemporaryDirectory(prefix='p2-haruka-public-') as work:
        work = Path(work)
        before = work / 'before'; before.mkdir()
        archive = subprocess.check_output(['git', 'archive', BASELINE_HEAD, 'rouge'], cwd=args.repo)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tf: tf.extractall(before, filter='data')
        (work / 'scenarios.json').write_text(json.dumps(rows))
        for label, path in (('before', before), ('after', Path(args.candidate))):
            subprocess.run([sys.executable, '-c', CAPTURE, str(path), str(work / 'scenarios.json'),
                str(output / ('public-' + label + '.json'))], check=True)
    before = json.loads((output / 'public-before.json').read_text())
    after = json.loads((output / 'public-after.json').read_text())
    assert before['catalog_sha256'] == after['catalog_sha256']
    counts = {'unchanged_numerical_output': 0, 'qualified_s1_s3_reference': 0,
        's2_unresolved_extra_recipient': 0, 's2_low_rank_without_module_qualification': 0}
    comparison = []
    for b, a in zip(before['rows'], after['rows'], strict=True):
        s = b['scenario']; assert s == a['scenario']
        assert b['bubble_components'] == a['bubble_components']
        assert b['talent_parameters_sha256'] == a['talent_parameters_sha256']
        assert b['timing_clock_sha256'] == a['timing_clock_sha256']
        extra_names=[c['name'] for c in a['extra_conditional_components'] if c.get('actual_total', 0) is None]
        if s['timing_mode']=='frames':
            assert a['unplaced_components'] == b['unplaced_components'] + extra_names
        else:assert a['unplaced_components'] == b['unplaced_components']
        for key in ('initial_seconds', 'duration_seconds', 'cycle_seconds', 'recharge_seconds'):
            assert b['skill'][key] == a['skill'][key]
        qualified = bool(s.get('module_level') and s['elite'] == 2 and s['level'] >= 60)
        n = s['healing_targets']
        if qualified and s['skill'] in (1, 3) and n >= 2:
            category = 'qualified_s1_s3_reference'
            assert a['ordinary_healing_component']['total'] == b['ordinary_healing_component']['total'] * 2
        elif qualified and s['skill'] == 2 and s['skill_rank'] >= 7 and n >= 3:
            category = 's2_unresolved_extra_recipient'
            assert a['total_healing'] is None and a['total_damage'] is None
            assert a['known_healing_subtotals']['window_healing'] == b['total_healing']
            assert a['known_damage_subtotals']['window_damage'] == b['total_damage']
            assert a['ordinary_healing_component'] == b['ordinary_healing_component']
        elif not qualified and s['skill'] == 2 and s['skill_rank'] <= 6 and n >= 2:
            category = 's2_low_rank_without_module_qualification'
            assert a['ordinary_healing_component']['total'] * 2 == b['ordinary_healing_component']['total']
            assert a['total_damage'] * 2 == b['total_damage']
        else:
            category = 'unchanged_numerical_output'
            for key in ('total_healing', 'total_damage', 'ordinary_healing_component', 'skill'):
                assert a[key] == b[key], (s, key)
        counts[category] += 1
        comparison.append({'scenario': s, 'category': category})
    summary = {'baseline_head': BASELINE_HEAD, 'public_entry': 'rouge.damage.calculate_damage',
        'case_count': len(rows), 'original_cases': 768, 'all_s2_ranks_cases': 320,
        'counts': counts, 'cached_catalog_unchanged': True, 'inputs_unchanged': True,
        'bubble_and_levitate_components_unchanged': True, 'timing_streams_and_clocks_unchanged': True,
        'unplaced_component_annotations_added_only_for_unresolved_extra_recipient': True,
        'cultivation_and_sp_clocks_unchanged': True, 'native_windows_verified': False,
        'actual_friend_acquisition_verified': False, 'native_three_target_composition_verified': False,
        'rows': comparison}
    (output / 'public-comparison.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, ensure_ascii=False))


if __name__ == '__main__': main()
