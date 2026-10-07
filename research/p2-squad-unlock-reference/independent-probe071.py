"""Small independent API matrix; no GUI/private state."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).parent
package = ROOT / sys.argv[1]
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.technology import _data


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def cases():
    squads = config_data()['squads']
    upgraded = [key for key, record in squads.items() if record['bandLevel'] == 1]
    for squad, mode, flag in itertools.product(upgraded, ('frames','continuous'), ({},{'effect_verified':False},{'effect_verified':True})):
        grade = 0 if flag.get('effect_verified') else 15
        yield {'operator':'mechanist','skill':1,'window_seconds':10,'timing_mode':mode,
               'run_config':{'squad':{'id':squad,**flag},'difficulty':{'value':grade}}}
    for squad, mode, edge in itertools.product(upgraded, ('frames','continuous'),
            ({'window_seconds':0},{'timing':{'target_windows':[]}})):
        yield {'operator':'char_2025_shu','skill':2,'window_seconds':10,'timing_mode':mode,'four_sui':True,
               'run_config':{'squad':{'id':squad,'effect_verified':True}},**edge}
    for squad, mode in itertools.product((key for key, value in squads.items() if value['bandLevel']==0),('frames','continuous')):
        yield {'operator':'mechanist','skill':1,'window_seconds':10,'timing_mode':mode,
               'run_config':{'squad':{'id':squad,'effect_verified':True}}}
    for owner, (elite,rank) in itertools.product(('mechanist','char_110_deepcl'), ((0,1),(1,7),(2,10))):
        yield {'operator':owner,'skill':1,'elite':elite,'skill_rank':rank,
               'run_config':{'squad':{'id':'rogue_6_band_22'}}}
    for squad in upgraded:
        for extra in ({'effect_verified':'false'}, {'name':'wrong'}):
            yield {'operator':'mechanist','skill':1,'run_config':{'squad':{'id':squad,**extra}}}
    for extra in ({'modeDifficulty':'MONTH_TEAM'},{'modeDifficulty':'CHALLENGE'}):
        yield {'operator':'mechanist','skill':1,'run_config':{'squad':{'id':'rogue_6_band_7'},'difficulty':{'value':0,**extra}}}
    yield {'operator':'char_2025_shu','skill':2,'elite':0,'skill_rank':1,'run_config':{'squad':{'id':'rogue_6_band_7'}}}
    for run in (None,{}, {'squad':None}, {'squad':{}}):
        yield {'operator':'mechanist','skill':1,'run_config':run}


cache_before = [canonical(catalog()), canonical(config_data()), canonical(_data())]
rows = []
for args in cases():
    original = deepcopy(args)
    try:
        result = json.loads(canonical(calculate_damage(args)))
        row = {'request':original,'full_result':result,
               'full_result_sha256':hashlib.sha256(canonical(result).encode()).hexdigest()}
    except Exception as error:
        row = {'request':original,'error':{'type':type(error).__name__,'message':str(error)}}
    assert args == original
    rows.append(row)
assert cache_before == [canonical(catalog()), canonical(config_data()), canonical(_data())]
out = ROOT / sys.argv[2]
packet = {'package':str(package), 'calls':len(rows),'caller_and_caches_unchanged':True, 'records':rows}
out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'package':str(package),'calls':len(rows),'successes':sum('full_result' in row for row in rows),
                  'errors':sum('error' in row for row in rows),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
