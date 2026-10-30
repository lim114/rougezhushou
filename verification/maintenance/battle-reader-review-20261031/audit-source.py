from pathlib import Path
from hashlib import sha256
import json,sys,subprocess,runpy,unittest,ctypes,win32gui,win32process
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];base=R/'verification/maintenance/battle-reader-review-20261031'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
    v=(R/n).read_bytes();return {'sha256':sha256(v).hexdigest(),'bytes':len(v)}
cp=read('DEVELOPMENT_CHECKPOINT.json');idx=read('CLOUD_INDEX.json');summary=read(cp['current_maintenance_save']['receipt'])
for path,h in idx['public_pointers'].items():assert pin(path)['sha256']==h,path
assert idx['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
assert cp['current_maintenance_save']['review_checklist_sha256']==pin('PROGRAM_REVIEW.md')['sha256']
assert idx['current_maintenance']['receipt_sha256']==pin(cp['current_maintenance_save']['receipt'])['sha256']
for k in ('source_review','related_receipt','native_receipt','image_review','runtime','replay_current_processes'):
    v=summary[k];assert pin(v['path'])=={key:v[key]for key in ('sha256','bytes')}
source=read(summary['source_review']['path'])
for v in source['changed_source']+source['additional_source_reviewed']:assert pin(v['path'])=={k:v[k]for k in ('sha256','bytes')}
proof=read(summary['related_receipt']['path']);initial=read('verification/maintenance/battle-reader-review-20261031/tests/results.json')
suite=unittest.TestLoader().loadTestsFromNames(initial['selectors'])
def ids(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from ids(item)
        else:yield item.id()
assert set(ids(suite))==set(proof['initial_ids'])|set(proof['final_ids'])
assert len(set(ids(suite)))==61
native=read(summary['native_receipt']['path']);assert native['passed']and native['unique_checks']==50 and not any(native['external_operation_attempts'].values())
for v in source['changed_source']:assert native['source_sha256_after'][v['path']]==v['sha256']
for v in read(summary['image_review']['path'])['final_images']:
    assert pin(v['current']['path'])==pin(v['reviewed_original']['path'])=={k:v['current'][k]for k in ('sha256','bytes')}
live=read('verification/maintenance/battle-reader-review-20261031/live-window-final/window.json')
assert live['private_six_paths_unchanged']
for v in source['changed_source']:assert live['source_sha256_after'][v['path']]==v['sha256']
for row in live['owned_windows']:assert win32gui.IsWindowVisible(row['hwnd']) and win32process.GetWindowThreadProcessId(row['hwnd'])[1]==row['pid'] and not ctypes.windll.user32.IsHungAppWindow(row['hwnd'])
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));assert m['validate_delivery'](R,cp)['current_section']==440
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=='b5ce07b802f51d42095f10fb12ce261b08dbd2f1'
tracked=subprocess.check_output(['git','ls-files','-z','rouge']).decode('utf8').split('\0')
sources={p for p in tracked if Path(p).suffix in ('.py','.js','.cjs')}|{'rouge/reference_image.py'}
assert len(sources)==529
from scripts.verify_full_available import maintained_selectors
assert len(maintained_selectors())==693
assert all(summary[k]is False for k in ('application_review_complete','video_parity_complete','P3_complete','P2_complete','P1_complete','game_operated','chat_sent','private_data_included'))
(base/'audit-source.py').write_bytes(Path(__file__).read_bytes())
result={'passed':True,'all_current_source_and_receipt_bindings_checked':True,'requirements_and_current_index_checked':True,
    'unique_related_test_ids_checked':61,'native_checks':50,'prior_cleanup_call_order_retained':True,
    'actual_test_window_visible_and_responding':True,'private_six_paths_preserved_during_startup':True,
    'current_maintained_selectors':693,'whole_program_review_complete':False,'video_parity_complete':False,'functional_section_added':False,
    'publication_binding':'enclosing maintenance commit after actual verified ordinary push'}
(base/'final-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
files=sorted(p for p in base.rglob('*')if p.is_file()and p.name!='archive-manifest.json')
manifest={'kind':'explicit_public_maintenance_archive','files':{p.relative_to(R).as_posix():pin(p.relative_to(R))for p in files},'private_state_included':False}
(base/'archive-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'final_audit_passed':True,'public_archive_files':len(files),'whole_program_complete':False}))
