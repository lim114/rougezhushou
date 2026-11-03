"""Seal five saved groups/source evidence with no new project calls."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def bind(p):
 d=p.read_bytes();return {'source_path':str(p),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(name,value):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def main():
 summary=json.loads((OUT/'five-reproduction-summary.json').read_bytes())
 assert summary['status']=='PASS_FIVE_SOURCE_REPRODUCTIONS'
 checks=[]
 for i in range(1,6):
  p=OUT/('case-'+str(i)+'.json');row=json.loads(p.read_bytes());directory=Path(row['file_path']).parent
  assert directory.resolve().is_relative_to(OUT/'runtime')
  seed=(directory/'seed-persisted.json').read_bytes();after=(directory/'run.json').read_bytes()
  assert hashlib.sha256(seed).hexdigest()==row['before_persisted_JSON_bytes_sha256']
  assert hashlib.sha256(after).hexdigest()==row['after_persisted_JSON_bytes_sha256']
  assert json.loads(seed)==row['before_persisted_JSON'] and json.loads(after)==row['after_persisted_JSON']
  assert row['seed_caller_typed_before']==row['seed_caller_typed_after']
  assert row['caller_typed_before']==row['caller_typed_after']
  checks.append({'case':row['case']['id'],'case_binding':bind(p),'seed_disk':bind(directory/'seed-persisted.json'),
   'after_disk':bind(directory/'run.json'),'caller_native_typed_unchanged':True,
   'departures':row['source_expected_departures_confirmed']})
 saved=write('saved-only-byte-check089.json',{'status':'PASS_SAVED_ONLY','groups':checks,'new_RunState_calls':0,
  'new_project_calls':0,'native_fulltree_checks_at_call_time':'All5before/after disk native trees and all10caller trees were checked inside the authorized runner; this sealing phase only rechecks saved bytes/caller trees, never reexecutes.',
  'natural_uuid_and_started_at_retained':True,'crossgroup_normalization_claimed':False})
 prep=write('read-only-discovery-notes089.json',{'events':['Broad read-only discovery included nonexistent optional schema/test/module file guesses; rg returned path diagnostics, then actual rg --files and valid production filenames resolved the required scope.','No cached roguelike_topic_table rawfile was found by the bounded filename query; fixed run-config metadata/source URL and source SHA are preserved, not promoted to a newly downloaded or independently raw-audited table.'],
   'no_project_calls_during_discovery':True,'product_failure':False})
 checkpoint=OUT/'CHECKPOINT.md'
 with checkpoint.open('x',encoding='utf-8') as f:f.write('89来源复现已完成并冻结。固定0f27027；5个全新临时RunState，5constructor+5seed apply+5subject apply，实际apply entry10。False+空名单错误删除mechanist；True+一名名单错误删除另一名char_151_myrtle；None保留、int0/int1正常原离队行为。所有10caller typed不变，5before+5after落盘全native一致；UUID与自然started_at/captured浮点完整保留，不跨组归一比较。0训练/伤害/app/recognition/formatter/Qt/Wine/tests/tracked，绝不访问真实.local。未创建产品草案；等待root排除bool合同patch授权。\n')
 handoff=write('handoff-final089-source.json',{'status':'FINAL_SEALED_SOURCE_POSITIVE_REPRODUCED','base_commit':summary['base_commit'],
  'summary':bind(OUT/'five-reproduction-summary.json'),'static_facts':bind(OUT/'static-source-facts089.json'),
  'saved_byte_check':bind(saved),'groups':5,'explicit_calls':summary['explicit_method_calls'],
  'actual_apply_entries':10,'source_confirmed_fix_scope':'Onlycrew bool aliases in RunState observation qualification; preserve valid int0/int1/None behavior and ignore stale/cross-run records according to existing gates. No productdraft authorized here.',
  'numeric_output_boundary':'Presence corruption reaches actual UI cultivation/skill/personalbuff input selection statically. No training/damage/app execution and no measured numericdelta.',
  'native_unknowns':'P1buff application, actual recruitment/departure/live roster mechanisms remain outside this input-truthfulness fix.',
  'source_tables_boundary':'run-config pinned source URL/SHA retained as existing derived metadata, not a fresh raw topic audit.',
  'next':'Root authorizes the minimal bool contract patch after reviewing this concrete five-case package.',
  'original130_9_passive6_UIstatic7_modified':False,'stop_changes':True})
 paths=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='public-manifest.json')
 rows=[{**bind(p),'archive_path':p.relative_to(OUT).as_posix()} for p in paths]
 manifest=write('public-manifest.json',{'version':1,'status':'FINAL_SEALED','files':rows,'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows)})
 for row in rows:assert bind(Path(row['source_path']))=={k:row[k] for k in ('source_path','bytes','sha256')}
 print(json.dumps({'status':'FINAL_SEALED_SOURCE_POSITIVE_REPRODUCED','manifest':bind(manifest),'handoff':bind(handoff),
  'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'new_project_calls':0}))
if __name__=='__main__':main()
