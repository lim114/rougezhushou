"""Stdlib-only v1 transport of immutable public packets; no product import."""
from pathlib import Path
import ast, hashlib, json, re

HERE=Path(__file__).resolve().parent
NEW8=Path('/workspace/.continuation/ui-090-runtime-increment088')
def sha(b):return hashlib.sha256(b).hexdigest()
def f(p,archive):return {'source_path':str(p),'archive_path':archive,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def save(name,obj):
    p=HERE/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');return f(p,name)

runner=HERE/'wine-ui-smoke-090-final.py';body=runner.read_text();tree=ast.parse(body)
out_sinks=[]
for node in ast.walk(tree):
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div) and isinstance(node.left,ast.Name) and node.left.id=='OUT' and isinstance(node.right,ast.Constant) and isinstance(node.right.value,str):
        out_sinks.append(node.right.value)
assert len(out_sinks)==len(set(out_sinks))==8
assert all('-090.' in name for name in out_sinks)
pngs=[n for n in out_sinks if n.endswith('.png') and 'failure' not in n]
assert sorted(pngs)==sorted(['wine-window-090.png','wine-movement-reference-090.png','wine-sown-tile-control-090.png','wine-medical-trait-090.png'])
save('actual-output-sink-mapping090.json',{'passed':True,'actual_OUT_sinks':out_sinks,'each_sink_emission_count':{n:out_sinks.count(n) for n in out_sinks},'old_actual085_sink_suffix_inverse':{n.replace('-090.','-085.'):n for n in out_sinks if n!='wine-ui-new-states-090.json.gz'},'additional_lossless_actual_52_state_archive':'wine-ui-new-states-090.json.gz','actual_success_four_PNG':pngs,'no_old080_or085_output_sink_overwritten':True,'API_Qt_Wine_calls':0})
new8mf=NEW8/'public-artifacts-manifest-new8-increment090.json';packet=json.loads(new8mf.read_bytes())
assert len(packet['files'])==210 and packet['total_bytes']==4893867
transport=[]
for row in packet['files']:
    p=Path(row['source_path']);assert p.stat().st_size==row['bytes'] and sha(p.read_bytes())==row['sha256']
    transport.append({**row,'archive_path':'completed-preflight-packet/'+row['archive_path']})
transport.append(f(new8mf,'completed-preflight-packet/original-public-artifacts-manifest-new8-increment090.json'))
hand=NEW8/'handoff-new8-increment090.json'
if not any(r['source_path']==str(hand) for r in transport):transport.append(f(hand,'completed-preflight-packet/original-handoff-new8-increment090.json'))
scope=json.loads((HERE/'runner-scope-and-source-freeze090.json').read_bytes())
save('handoff-final-runner090.json',{'format_version':1,'status':'FINAL_STABLE_SOURCE_BOUND_PENDING_ROOT_SOLE_ACTUAL_WINDOW','runner':f(runner,'wine-ui-smoke-090-final.py'),'actual_source_binding':f(HERE/'actual-root090-source-binding.json','actual-root090-source-binding.json'),'actual_root_commit':scope['actual_commit'],'maintained_source_files':730,'public_source_files':126,'old4217_inverse':f(HERE/'old4217-byte-inverse-proof090.json','old4217-byte-inverse-proof090.json'),'scope':f(HERE/'runner-scope-and-source-freeze090.json','runner-scope-and-source-freeze090.json'),'planned_new_rows':66,'planned_total_rows':4283,'actual_new_GUI_pass':False,'actual_new_Qt_Wine_calls_in_this_preparation':0,'completed_preflight':scope['already_completed_preflight'],'final_independent_static_review_not_yet_executed':True,'sole_execution':'Root copies exactly this frozen runner to /workspace/.compat/wine-ui-smoke-090.py after independent source-only review; root performs one real Wine MainWindow run in the existing isolated prefix. Do not execute the original True-guarded pending090 draft.','actual_artifacts':out_sinks,'existing_final89_small_source_packet':f(HERE/'review-saved89-source/manifest-static-consumer089.json','review-saved89-source/manifest-static-consumer089.json'),'packet_manifest_name':'public-artifacts-manifest-final-runner090.json'})
own=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file() and '__pycache__' not in p.parts and p.name!='public-artifacts-manifest-final-runner090.json':own.append(f(p,'final-runner090/'+p.relative_to(HERE).as_posix()))
rows=own+transport
assert len({r['source_path'] for r in rows})==len(rows)
assert len({r['archive_path'] for r in rows})==len(rows)
mf=save('public-artifacts-manifest-final-runner090.json',{'format_version':1,'status':'FINAL_STABLE_PUBLIC_PACKET_WITH_ROOT_SOLE_ACTUAL_QT_PENDING','files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'manifest_self_excluded':True,'all_immutable_initial_preparations_and_counterexamples_included':True,'duplicate_full_public126_and_maintained730_trees_excluded_with_complete_named_gitblob_rebuild_proof':True,'API_helper_formatter_Qt_Wine_tests':0})
print(json.dumps({'manifest':mf,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'handoff':f(HERE/'handoff-final-runner090.json','handoff-final-runner090.json'),'runner':f(runner,'wine-ui-smoke-090-final.py')},ensure_ascii=False))
