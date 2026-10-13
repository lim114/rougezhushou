"""Seal exact public before/after workload and unchanged historical assertion."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
PUBLIC=REPO/'work/adaptive-261-public-operator'
before=json.loads((PUBLIC/'before-scenarios.json').read_text())
owner=json.loads((PUBLIC/'before-owner-sequence.json').read_text())
after=json.loads((ROOT/'candidate-real.json').read_text())
unit=json.loads((ROOT/'production-unit.json').read_text())
apply=json.loads((ROOT/'production-apply-manifest.json').read_text())
assert after['all_match_real_uncached_oracle'] and after['source_unchanged']
assert unit['successful'] and unit['source_unchanged'] and not unit['skips']
for path,record in apply['production_after'].items():
 assert hashlib.sha256((REPO/path).read_bytes()).hexdigest()==record['sha256']
assert hashlib.sha256((REPO/'tests/test_adaptive_recognition.py').read_bytes()).hexdigest()=='188ecc89418b02d656f6807b2ecf6b0b6b139fdcdc8961331c9bdf935467fe4a'
summary={'provider':'actual RapidOCR 1.4.4 / ONNX original calls','private_original230_replayed':False,'protocol_checks_are_engine_doubles':True,'same_exact_public_png_inputs':True,'scenarios':{},'owner_sequence':[],'unit_tests':unit['tests'],'unit_skips':unit['skips'],'production_hashes':unit['source_hashes_after'],'original_adaptive_test_unchanged_sha256':'188ecc89418b02d656f6807b2ecf6b0b6b139fdcdc8961331c9bdf935467fe4a'}
for name,record in after['scenarios'].items():
 old=before['scenarios'][name]['default'][name];new=record['changed']
 summary['scenarios'][name]={'input':record['input'],'before_ocr':old['performance']['ocr'],'after_ocr':new['performance']['ocr'],'before_routing':old['performance']['routing'],'after_routing':new['performance']['routing'],'current_operator_id':new['operator']['id'],'current_fields':new['operator']['fields'],'current_missing_fields':new['operator']['missing_fields'],'current_complete':new['operator']['complete'],'matches_saved_real_fresh_uncached_oracle':record['matches_saved_real_uncached_oracle'],'actual_before_work':next(v for v in before['actual_work_summary'] if v['phase']=='default:'+name+':'+name),'actual_before_onnx_events':[v for v in before['actual_call_events'] if v['phase']=='default:'+name+':'+name],'actual_after_work':next(v for v in after['work_summary'] if v['phase']==name+':changed')}
for record in after['current_owner_sequence']:
 label=record['input']['label'];old=owner['results'][label]['observed'];new=record['result']
 summary['owner_sequence'].append({'input':record['input'],'before_ocr':old['performance']['ocr'],'after_ocr':new['performance']['ocr'],'current_owner':new['operator']['id'],'current_fields':new['operator']['fields'],'current_missing_fields':new['operator']['missing_fields'],'matches_saved_real_fresh_uncached_oracle':True,'actual_before_onnx_events':[v for v in owner['actual_call_events'] if v['phase']=='sequence:'+label],'actual_after_work':next(v for v in after['work_summary'] if v['phase']=='owner_sequence:'+label)})
(ROOT/'before-after-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
copy_paths=[Path('verification/full-260/repair/adaptive-230-review/original-retrigger.json')]
for path in copy_paths:
 (ROOT/path.name).write_bytes((REPO/path).read_bytes())
allowed_bridge=('REPORT.md','replay_real_frames.py','run_candidate_unit.py','run_production_unit.py','seal_evidence.py','candidate-real.json','candidate-real.log','candidate-unit.json','candidate-unit.log','production-unit.json','production-unit.log','production-apply-manifest.json','before-after-summary.json','native-input-recovery.json','original-retrigger.json')
allowed_public=('REPORT.md','fixture-manifest.json','frames.json','owner-sequence-frames.json','run_fixture.py','run_scenarios.py','run_owner_sequence.py','before-scenarios.json','before-scenarios.log','before-owner-sequence.json','before-owner-sequence.log','before-summary.json','before-seal.json','owner-sequence-seal.json','validation.json','public-baseline.png','public-control-damaged.png','public-icon-removed.png','public-exterior-overlay.png','public-geometry-changed.png','public-owner-vanilla.png','public-owner-vanilla-control-damaged.png')
files=[]
for folder,names in ((ROOT,allowed_bridge),(PUBLIC,allowed_public)):
 for name in names:
  p=folder/name;assert p.exists(),p
  files.append({'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'archive-manifest.json').write_text(json.dumps({'scope':'new public synthetic real OCR and engine-double boundary checks; original230/native status unchanged','allowed_files':files,'total_bytes':sum(x['bytes'] for x in files),'excluded':'candidate source duplicates, exploratory-v1, __pycache__, model/runtime binaries, private samples, Wine prefix, personal content'},indent=2),encoding='utf-8')
print(json.dumps({'allowed_files':len(files),'total_bytes':sum(x['bytes'] for x in files),'source_frozen':True,'historical_assertion_unchanged':True}))
