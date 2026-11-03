"""One isolated process per fixed package, saving complete results/text/error."""
from pathlib import Path
import copy
import json
import sys

OUT=Path(__file__).resolve().parent
variant=sys.argv[1]
assert variant in ('baseline','draft')
sys.path.insert(0,str(OUT/('fixed-'+variant)))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.estimate import format_estimate
cases=json.loads((OUT/'independent-cases083.json').read_bytes())
original_catalog=copy.deepcopy(catalog())
rows=[]
for case in cases:
    args=copy.deepcopy(case['scenario']);before=copy.deepcopy(args)
    try:
        result=calculate_damage(args)
    except Exception as error:
        row={**case,'error':{'type':type(error).__name__,'message':str(error)},'actual_public_calls':1}
    else:
        row={**case,'result':result,'report_text':format_report(result),
             'technical_report_text':format_report(result,technical=True),'estimate_text':format_estimate(result),
             'actual_public_calls':1}
    row['caller_input_preserved']=args==before
    rows.append(row)
    with (OUT/f'{variant}-case-{len(rows):02}.json').open('x',encoding='utf-8') as f:
        json.dump(row,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
assert len(rows)==40 and catalog()==original_catalog and all(row['caller_input_preserved'] for row in rows)
with (OUT/f'{variant}-independent-public083.json').open('x',encoding='utf-8') as f:
    json.dump({'actual_public_calls':40,'variant':variant,'rows':rows,'catalog_preserved':True},f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':'completed','variant':variant,'actual_public_calls':40,'successful':sum('result'in r for r in rows),'errors':sum('error'in r for r in rows)}))
