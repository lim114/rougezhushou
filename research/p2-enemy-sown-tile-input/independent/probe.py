"""Independent public source-contract probes; explicit immutable package only."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import sys
sys.dont_write_bytecode = True
package = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report

OP = 'char_2025_shu'
FIELD = 'enemy_on_sown_tile'
texts = ('false','False','true','0','1','',' ','no','off','null','unknown')
nontexts = (False,True,0,1,None,0.0,1.0,{},[],[0],{'declared':False})
records, isolation_errors = [], []
original_catalog = deepcopy(catalog())


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def outcome(scenario):
    original = deepcopy(scenario)
    try:
        result = calculate_damage(scenario)
        value = {'accepted':True,'result':result,'report':format_report(result)}
    except Exception as exc:
        value = {'accepted':False,'error_type':type(exc).__name__,'error':str(exc)}
    if strict(scenario) != strict(original):
        isolation_errors.append(original)
    return value


def add(key, group, base, raw, comparison=None):
    scenario = {**deepcopy(base),FIELD:deepcopy(raw)}
    result = outcome(deepcopy(scenario))
    expected = outcome(deepcopy(comparison)) if comparison is not None else None
    records.append({'key':key,'group':group,'input':scenario,'outcome':result,
                    'comparison_input':comparison,'comparison_outcome':expected,
                    'matches_comparison':strict(result)==strict(expected) if expected is not None else None})


contexts = ({'window_seconds':10},{'window_seconds':0},
            {'window_seconds':10,'timing':{'target_disappears_seconds':0}},
            {'window_seconds':10,'timing':{'target_windows':[]}})
for mode in ('frames','continuous'):
    for rank in range(1,11):
        for ci, context in enumerate(contexts):
            base = {'operator':OP,'skill':3,'elite':2,'base_attack':1000,
                    'skill_rank':rank,'timing_mode':mode,**deepcopy(context)}
            for vi, raw in enumerate(texts):
                add(f'active_text:{mode}:{rank}:{ci}:{vi}','active_text',base,raw,
                    {**base,FIELD:False})
            for vi, raw in enumerate(nontexts):
                add(f'active_nontext:{mode}:{rank}:{ci}:{vi}','active_nontext',base,raw,
                    {**base,FIELD:bool(raw)})

# Source qualification rejects unavailable S3 before reading its condition.
for elite in (0,1):
    for mode in ('frames','continuous'):
        for rank in (1,7,10):
            base = {'operator':OP,'skill':3,'elite':elite,'base_attack':1000,
                    'skill_rank':rank,'timing_mode':mode,'window_seconds':10}
            for vi,raw in enumerate(texts+nontexts):
                add(f'locked:{elite}:{mode}:{rank}:{vi}','locked_skill',base,raw,base)

# Existing S1/S2 conditions are outside this owner+skill path.
for skill, elites in ((1,(0,1,2)),(2,(1,2))):
    for elite in elites:
        for mode in ('frames','continuous'):
            base = {'operator':OP,'skill':skill,'elite':elite,'base_attack':1000,
                    'skill_rank':1,'timing_mode':mode,'window_seconds':10}
            for vi,raw in enumerate(texts+nontexts):
                add(f'inactive_shu:{skill}:{elite}:{mode}:{vi}','inactive_shu_skill',base,raw,base)

for operator, profile in catalog()['operators'].items():
    if operator == OP:
        continue
    for skill in range(1,len(profile['skills'])+1):
        for mode in ('frames','continuous'):
            base = {'operator':operator,'skill':skill,'base_attack':1000,
                    'timing_mode':mode,'window_seconds':10}
            add(f'other_owner:{operator}:{skill}:{mode}','other_owner',base,'false',base)

# Observe the already-unbound four-Sui clock without changing its own input.
for mode in ('frames','continuous'):
    base = {'operator':OP,'skill':3,'elite':2,'base_attack':1000,'skill_rank':10,
            'timing_mode':mode,'window_seconds':10,'four_sui':True}
    for vi,raw in enumerate((False,True,0,1,None,'false','')):
        add(f'four_sui_context:{mode}:{vi}','four_sui_context',base,raw,
            {**base,FIELD:bool(raw)})

summary = {'package':str(package),'cases':len(records),
           'public_calls':sum(1+(r['comparison_input'] is not None) for r in records),
           'active_text_accepted':[r['key']for r in records if r['group']=='active_text' and r['outcome']['accepted']],
           'inactive_or_locked_drift':[r['key']for r in records if r['group']in('locked_skill','inactive_shu_skill','other_owner') and r['matches_comparison']is not True],
           'nontext_math_comparison_drift':[r['key']for r in records if r['group']=='active_nontext' and r['matches_comparison']is not True],
           'caller_isolation_errors':isolation_errors,'catalog_preserved':catalog()==original_catalog,
           'source_hashes':{str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((package/'rouge').rglob('*'))
                            if p.is_file()and p.suffix in('.py','.json')},
           'root_source_edits':0,'author_source_edits':0,'patch_written':False,
           'private_state_read':False,'native_validation':False,'new_mechanism_inferred':False}
with gzip.open(destination,'wt',encoding='utf-8')as handle:
    json.dump({'summary':summary,'records':records},handle,ensure_ascii=False,sort_keys=True)
destination.with_suffix('.summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items()if k not in('source_hashes','active_text_accepted')},ensure_ascii=False))
