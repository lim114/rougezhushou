import copy
import hashlib
import json
import sys
from pathlib import Path

OUT=Path(__file__).parent
source=Path(sys.argv[1]).resolve()
destination=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.operator_engine import selected_talents

def typed(value):
    if value is None:return ['none']
    if isinstance(value,bool):return ['bool',value]
    if isinstance(value,int):return ['int',value]
    if isinstance(value,float):return ['float',repr(value)]
    if isinstance(value,str):return ['str',value]
    if isinstance(value,list):return ['list',[typed(v) for v in value]]
    if isinstance(value,tuple):return ['tuple',[typed(v) for v in value]]
    if isinstance(value,dict):return ['dict',[[typed(k),typed(v)] for k,v in value.items()]]
    raise TypeError(type(value))

rows=json.loads((OUT/'public-cases84.json').read_bytes())
cached=copy.deepcopy(catalog())
for row in rows:
    args=row['scenario']
    before=copy.deepcopy(args)
    try:
        result=calculate_damage(args)
        row.update(result=result,typed_result=typed(result),estimate_text=format_estimate(result),
                   report_text=format_report(result),technical_report_text=format_report(result,technical=True))
        selected,parts=selected_talents(catalog()['operators'][args['operator']],args)
        row['actual_source_selection']={'selected_talents':selected,'module_parts':parts}
    except (ValueError,TypeError) as exc:
        row['error']={'type':type(exc).__name__,'message':str(exc)}
    assert typed(args)==typed(before)
assert typed(catalog())==typed(cached)
data=(json.dumps(rows,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
with destination.open('xb') as f:f.write(data)
receipt={'passed':True,'baseline_commit':'b5a40f30683bfc0945decaabbd4db5914c28427f',
         'source_tree':str(source),'file':str(destination),'sha256':hashlib.sha256(data).hexdigest(),
         'bytes':len(data),'calculate_damage_calls':len(rows),'successes':sum('result' in r for r in rows),
         'errors':sum('error' in r for r in rows),'typed_result_saved_before_json_encoding':True,
         'three_actual_reports_saved':True,'caller_and_catalog_unchanged':True,'python_hash_seed':'0',
         'gui_executed':False,'wine_executed':False}
destination.with_suffix('.receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
