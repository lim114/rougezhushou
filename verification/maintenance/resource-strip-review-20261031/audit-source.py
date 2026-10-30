from pathlib import Path
from hashlib import sha256
import json, sys, runpy, subprocess, ctypes, win32gui, win32process

R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
base=R/'verification/maintenance/resource-strip-review-20261031'
def read(path):return json.loads((R/path).read_bytes())
def pin(path):
    raw=(R/path).read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}

(R/'research/resource-strip-review-20261031/qt-flow-layout-upstream.py').write_bytes((R/'.cache/qt-flow-layout-source/flowlayout.py').read_bytes())
upstream=read('research/resource-strip-review-20261031/upstream-source.json')
assert pin('research/resource-strip-review-20261031/qt-flow-layout-upstream.py')['sha256']==upstream['source_sha256']
assert pin('licenses/qt-flow-layout-BSD-3-Clause.txt')['sha256']==upstream['license_sha256']
cp=read('DEVELOPMENT_CHECKPOINT.json');idx=read('CLOUD_INDEX.json')
summary=read(cp['current_maintenance_save']['receipt'])
for path,h in idx['public_pointers'].items():assert pin(path)['sha256']==h,path
assert idx['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
assert idx['current_maintenance']['receipt_sha256']==pin(cp['current_maintenance_save']['receipt'])['sha256']
assert cp['current_maintenance_save']['review_checklist_sha256']==pin('PROGRAM_REVIEW.md')['sha256']
for key in ('source_review','image_review','runtime','upstream_source'):
    row=summary[key];assert pin(row['path'])=={k:row[k]for k in ('sha256','bytes')}
review=read(summary['source_review']['path'])
for row in review['changed_application_and_acceptance_source']+review['additional_source_read']:
    assert pin(row['path'])=={k:row[k]for k in ('sha256','bytes')}
for path in ('rouge/run_state.py','rouge/resource_recognition.py','rouge/record_flags.py'):
    assert subprocess.check_output(['git','show','HEAD:'+path])==(R/path).read_bytes()
for path in ('tests/process.json','index-tests/process.json','native-392/process.json','native-422/process.json'):
    assert read('verification/maintenance/resource-strip-review-20261031/'+path)['actual_observed_exit']==0
for row in summary['native_scopes']:
    v=read(row['receipt']['path']);assert v['passed'] and not any(v['external_operation_attempts'].values())
    assert pin(row['receipt']['path'])=={k:row['receipt'][k]for k in ('sha256','bytes')}
    for item in review['changed_application_and_acceptance_source']:assert v['source_sha256_after'][item['path']]==item['sha256']
for row in read(summary['image_review']['path'])['images']:
    assert pin(row['path'])=={k:row[k]for k in ('sha256','bytes')}
live=read('verification/maintenance/resource-strip-review-20261031/live-window/window.json')
assert live['private_six_paths_unchanged']
for row in live['owned_windows']:
    assert win32gui.IsWindowVisible(row['hwnd']) and win32process.GetWindowThreadProcessId(row['hwnd'])[1]==row['pid'] and not ctypes.windll.user32.IsHungAppWindow(row['hwnd'])
for item in review['changed_application_and_acceptance_source']:assert live['source_sha256_after'][item['path']]==item['sha256']
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
assert len(maintained_selectors())==692
paths=subprocess.check_output(['git','ls-files','-z','rouge']).decode('utf8').split('\0')
sources={n for n in paths if Path(n).suffix in ('.py','.js','.cjs')}
sources.update(('rouge/flow_layout.py','rouge/player_resource_facts.py','rouge/player_resource_strip.py'))
assert len(sources)==528,len(sources)
assert not any(summary[k] for k in ('application_review_complete','video_parity_complete','P3_complete','P2_complete','P1_complete','game_operated','chat_sent','private_data_included'))
(base/'record-source.py').write_bytes((R/'.cache/record_resource_strip_review.py').read_bytes())
(base/'audit-source.py').write_bytes(Path(__file__).read_bytes())
audit={'passed':True,'source_bound':True,'requirements_and_index_bound':True,'related_tests_passed':54,
    'index_tests_passed':26,'native_scopes_checked_individually':True,'actual_test_window_visible_and_responding':True,
    'private_six_paths_unchanged':True,'private_contents_or_hashes_published':False,'source_inventory_total':528,
    'full_scope_preserved':True,'full_validation_rerun':False,'whole_program_complete':False,'video_parity_complete':False,
    'Qt_upstream_bytes_and_license_verified':True,'publication_binding':'enclosing commit after verified ordinary push'}
(base/'final-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')
files=sorted(p for p in base.rglob('*')if p.is_file()and p.name!='archive-manifest.json')
manifest={'kind':'explicit_public_maintenance_archive','files':{p.relative_to(R).as_posix():pin(p.relative_to(R))for p in files},'private_state_included':False}
(base/'archive-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'final_audit_passed':True,'public_archive_files':len(files),'whole_program_complete':False}))
