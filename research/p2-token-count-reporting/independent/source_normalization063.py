"""Verify exact importer projection, retaining raw scalar types in catalog fields."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/rougezhushou')
AUTHOR=Path('/workspace/.continuation/p2-token-count-report-audit-063')
HEAD='c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf'
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def load(p):return json.loads(p.read_text())
builder=subprocess.run(['git','show',HEAD+':scripts/build_catalog.py'],cwd=ROOT,check=True,capture_output=True).stdout
tree=ast.parse(builder)
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='attributes' for t in n.targets))
mapping=ast.literal_eval(assignment.value)
source=load(AUTHOR/'source-closure.json')
chars=load(ROOT/'.cache/p2-s1-binding/character_table.json')
skills=load(ROOT/'.cache/p2-s1-binding/skill_table.json')
catalog=load(AUTHOR/'baseline61/rouge/data/catalog.json')
op=catalog['operators']['char_110_deepcl'];token=chars['token_10001_deepcl_tentac'];norm=op['tokens']['token_10001_deepcl_tentac']
token_checks=[]
for elite,phase in enumerate(token['phases']):
    assert canon(phase['maxLevel'])==canon(norm['phases'][elite]['max_level'])
    for frame_index,frame in enumerate(phase['attributesKeyFrames']):
        raw=frame['data'];expected={'level':frame['level'],**{target:raw[key] for key,target in mapping.items()}}
        actual=norm['phases'][elite]['frames'][frame_index]
        assert canon(expected)==canon(actual)
        types={key:{'raw':type(raw[key]).__name__,'catalog':type(actual[target]).__name__} for key,target in mapping.items()}
        assert all(v['raw']==v['catalog'] for v in types.values())
        row=next(r for r in source['raw_token_cultivation_records'] if r['elite']==elite and r['level']==frame['level'])
        projected={key:raw[key] for key in row['values']}
        assert canon(projected)==canon(row['values'])
        token_checks.append({'selector':row['selector'],'level':frame['level'],'elite':elite,
            'receipt_11_parameter_projection_strict_match':True,
            'catalog_10_parameter_mapping_strict_match':True,'catalog_projection':actual,'dtypes':types,
            'raw_maxDeployCount_preserved_as_receipt_only':row['values']['maxDeployCount'],
            'maxDeployCount_not_in_catalog_attributes_mapping':True,
            'raw_other_keys_not_in_receipt':sorted(set(raw)-set(row['values']))})
skill_checks=[]
for i,binding in enumerate(chars['char_110_deepcl']['skills']):
    skill_id=binding['skillId'];actual_skill=op['skills'][i]
    assert actual_skill['id']==skill_id
    assert type(actual_skill['unlock_elite']) is int and actual_skill['unlock_elite']==int(binding['unlockCond']['phase'][-1])
    for rank,raw in enumerate(skills[skill_id]['levels'],1):
        expected={'name':raw['name'],'duration':raw['duration'],'description':raw['description'],
            'duration_type':raw['durationType'],'sp_type':raw['spData']['spType'],
            'sp_cost':raw['spData']['spCost'],'initial_sp':raw['spData']['initSp'],
            'sp_increment':raw['spData']['increment'],'max_charges':raw['spData']['maxChargeTime'],
            'values':{b['key']:b['value'] for b in raw['blackboard']}}
        assert canon(expected)==canon(actual_skill['levels'][rank-1])
        skill_checks.append({'selector':f'skill_table.{skill_id}.levels[{rank-1}]',
            'entire_normalized_level_strict_JSON_match':True,'scalar_numeric_dtype_preserved':True})
receipt={'scope':'Read-only fixed c3ccf25 importer AST and exact normalized source projection',
    'builder_commit':HEAD,'builder_selector':'scripts/build_catalog.py attributes at line15, token mapping at line40, skill mapping at line54',
    'builder_sha256':hashlib.sha256(builder).hexdigest(),'builder_executed':False,'attribute_mapping':mapping,
    'token_checks':token_checks,'skill_checks':skill_checks,'numeric_stat_conversions':[],
    'unlock_metadata_conversion':'Original PHASE_n string -> int(last digit), explicitly prescribed in importer; no numeric stat dtype coercion',
    'initial_failure_diagnosis':'Raw token data contains 28 fields. Source receipt records 11 selected parameters; catalog maps 10 and retains raw types. Initial whole-dictionary equality assertion was invalid.',
    'strict_JSON_compares_int_vs_float_as_different':True,'Python_numeric_equality_used_as_dtype_proof':False}
(HERE/'source-normalization063.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'token_endpoints':len(token_checks),'skill_ranks':len(skill_checks),'all_projection_dtype_matches':True,
                  'numeric_stat_conversions':[],'builder_sha256':receipt['builder_sha256']}))
