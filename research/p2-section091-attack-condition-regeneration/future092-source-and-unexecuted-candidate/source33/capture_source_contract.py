"""Static source projection only; no project helpers or runtime code imported."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIXED=HERE/'fixed-actual90'


def put(name, value):
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


binding=json.loads((HERE/'fixed-source-binding.json').read_text())
for item in binding['sources']:
    raw=Path(item['archive_path']).read_bytes()
    assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
app=(FIXED/'rouge/app.py').read_text()
tree=ast.parse(app)
parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
fields=('window_seconds','limit_window','frame_timing','timing_scenario')
refs=[]
for node in ast.walk(tree):
    if not (isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name)
            and node.value.id=='self' and node.attr in fields):continue
    enclosing=node
    while enclosing in parents and not isinstance(enclosing,ast.stmt):enclosing=parents[enclosing]
    context=node
    while context in parents and not isinstance(context,ast.FunctionDef):context=parents[context]
    refs.append({'field':node.attr,'line':node.lineno,'method':getattr(context,'name',None),
                 'statement':ast.get_source_segment(app,enclosing)})
refs.sort(key=lambda r:(r['line'],r['field']))
window_refs=[r for r in refs if r['field'] in ('window_seconds','limit_window')]
assert len(window_refs)==6
assert not any('.connect(' in r['statement'] for r in window_refs)
put('actual-Qt-producer-and-all-references.json',{
    'status':'SOURCE_AST_ONLY_NO_QT_EXECUTION','git_ref':binding['actual_root_commit'],
    'number_source':'app.py72-77 QDoubleSpinBox with setRange(0,maximum), decimals, initial value',
    'window_source':'app.py593 number(40,3600,2); app.py594 QCheckBox initially no explicit setChecked; app1073-1074 writes window only when checkbox.checked',
    'window_limit_refs':window_refs,'timing_related_refs':refs,
    'window_controls_no_declared_signal_connection_in_full_app_AST':True,
    'contrasting_existing_signal_sources':'OPTIONS bool666-667 / numeric671,674; frame_timing613 and timing_scenario614',
    'input_boundary':'Numeric window is declared bounded QDoubleSpinBox, not arbitrary JSON. Bool aliases/negative/NaN API examples are not claimed GUI window inputs. Timing text separately parses JSON object at1141-1144 before numerical API1150.',
    'native_actual_value_type_or_signal_counts_measured':False,'project_calls':0})

ranges={
    'rouge/app.py':[(72,77),(593,615),(663,676),(1070,1089),(1138,1157),(1206,1219)],
    'rouge/damage.py':[(28,46),(236,287),(289,334),(343,388),(411,457)],
    'rouge/operator_engine.py':[(110,148),(285,300),(1300,1307),(1523,1545)],
    'rouge/estimate.py':[(17,20),(101,107),(153,165),(229,247),(263,281)],
    'rouge/timing.py':[(12,20),(103,117),(164,199),(230,261),(299,324),(357,370),(387,395)],
    'rouge/reporting.py':[(381,400),(763,775),(1092,1106)],
    'rouge/run_modifiers.py':[(4,10),(79,95)],
    'rouge/relics.py':[(55,61),(372,384)],
}
text=[];excerpts=[]
for rel,pairs in ranges.items():
    raw=(FIXED/rel).read_bytes();lines=raw.decode().splitlines()
    for start,end in pairs:
        assert 1<=start<=end<=len(lines),(rel,start,end)
        body='\n'.join(f'{n}: {lines[n-1]}' for n in range(start,end+1))+'\n'
        text.append(f'[{rel}:{start}-{end}; fixed actual2cbc]\n'+body)
        excerpts.append({'path':rel,'start_line':start,'end_line':end,
                         'source_sha256':hashlib.sha256(raw).hexdigest(),
                         'numbered_excerpt_sha256':hashlib.sha256(body.encode()).hexdigest()})
(HERE/'source-excerpts.txt').write_text('\n'.join(text))
put('source-excerpt-index.json',{'status':'FIXED_SOURCE_TEXT_EXCERPTS_NOT_EXECUTION','excerpts':excerpts,'count':len(excerpts)})

historical=Path('/workspace/.continuation/independent-finite085/guard-subreview/guard-subreceipt.json')
raw=historical.read_bytes();saved=json.loads(raw)
assert saved['actionable_candidates']==[] and saved['historical_numbertypes_and_zero_aliases'].startswith('Historical')
(HERE/'historical-finite085-guard-receipt.json').write_bytes(raw)
put('historical-boundary-binding.json',{
    'source_path':str(historical),'archive_path':'historical-finite085-guard-receipt.json',
    'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
    'status':'HISTORICAL_SOURCE_ONLY_NEGATIVE_NOT_NEW_EXECUTION',
    'old_fixed_commit':saved['fixed_commit'],'old_actionable_candidates':[],
    'meaning':'Existing finite guards, historical zero/number aliases and derived-overflow limitations retained. No rerun of old audit/133consumer/18guard/matrices; current window/timing source separately frozen.',
    'old_checks_newly_run':False})
print(json.dumps({'status':'STATIC_SOURCE_CONTRACT_CAPTURE_PASS','window_refs':len(window_refs),
                  'excerpts':len(excerpts),'new_project_calls':0}))
